import argparse
import logging
import os

import torch
from datasets import load_dataset
from tqdm import tqdm
from torch.ao.quantization import FakeQuantizeBase
from transformers import AutoModelForCausalLM, AutoTokenizer

from quantized_training import (
    FusedAmaxObsFakeQuantize,
    add_training_args,
    get_qconfig,
    get_qconfig_mapping,
    quantize,
    quantize_pt2e,
    run_task,
    plot_layer_distribution,
    plot_layer_range
)

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Process model parameters.")
    parser.add_argument('--model_id', required=True, help='Pretrained model identifier')
    parser.add_argument('--max_length', type=int, default=1024, help='Maximum sequence length')
    parser.add_argument('--stride', type=int, default=512, help='Stride for processing the data')
    parser.add_argument('--output_dir', default=None, help='Output directory for histograms')
    parser.add_argument(
        '--torch_dtype',
        default="bfloat16",
        choices=["auto", "bfloat16", "float16", "float32"],
        help=(
            "Override the default `torch.dtype` and load the model under this dtype. If `auto` is passed, the "
            "dtype will be automatically derived from the model's weights."
        )
    )
    parser.add_argument('--max_calibration_steps', type=int, default=1000, help='Maximum number of calibration steps')
    add_training_args(parser)
    return parser.parse_args()

def main(args):
    device = torch.device(f"cuda:{args.gpu}" if args.gpu is not None else "cuda")
    torch_dtype = (
        args.torch_dtype
        if args.torch_dtype in ["auto", None]
        else getattr(torch, args.torch_dtype)
    )
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=torch_dtype,
        device_map=args.gpu if args.gpu is not None else "auto",
        attn_implementation="eager", # flash attention is not supported
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)

    def calibrate(model):
        validation = load_dataset("wikitext", "wikitext-2-raw-v1", split="validation")
        encodings = tokenizer("\n\n".join(validation["text"]), return_tensors="pt")
        seq_len = encodings.input_ids.size(1)
        steps = 0
        for begin_loc in tqdm(range(0, seq_len - args.max_length, args.stride)):
            end_loc = min(begin_loc + args.max_length, seq_len)
            input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
            target_ids = input_ids.clone()
            with torch.no_grad():
                model(input_ids, labels=target_ids)

            steps += 1
            if steps == args.max_calibration_steps - 1:
                break

        # fix quantization parameters
        for module in model.modules():
            if isinstance(module, FakeQuantizeBase):
                module.disable_observer()

    # do_scaling = args.activation and args.activation.qscheme
    # quantize(model, args, run_fn=calibrate if do_scaling else None)

    qconfig = get_qconfig(args.activation, args.weight, args.error,
                          args.record_histogram, args.force_scale_power_of_two)
    operations = args.quantize_forward.lower().split(",")
    qconfig_mapping = get_qconfig_mapping(qconfig, operations)

    input_ids = torch.randint(0, 100, (1, args.max_length), device=device)
    target_ids = input_ids.clone()
    seq_len = torch.export.Dim("seq_length", min=3, max=args.max_length)
    dynamic_shapes = {"input_ids": {1: seq_len}, "labels": {1: seq_len}}
    model = quantize_pt2e(
        model,
        args,
        qconfig_mapping,
        example_args=(input_ids,),
        example_kwargs={"labels": target_ids},
        dynamic_shapes=dynamic_shapes,
        run_fn=calibrate,
    )

    test = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    encodings = tokenizer("\n\n".join(test["text"]), return_tensors="pt")

    seq_len = encodings.input_ids.size(1)

    nlls = []
    prev_end_loc = 0
    # Subtract max_length from seq_len to ensure that the last window has length max_length
    for begin_loc in tqdm(range(0, seq_len - args.max_length, args.stride)):
        end_loc = min(begin_loc + args.max_length, seq_len)
        trg_len = end_loc - prev_end_loc  # may be different from stride on last loop
        input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
        target_ids = input_ids.clone()
        target_ids[:, :-trg_len] = -100

        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)

            # loss is calculated using CrossEntropyLoss which averages over valid labels
            # N.B. the model only calculates loss over trg_len - 1 labels, because it internally shifts the labels
            # to the left by 1.
            neg_log_likelihood = outputs.loss

        nlls.append(neg_log_likelihood)

        prev_end_loc = end_loc
        if end_loc == seq_len:
            break

    ppl = torch.exp(torch.stack(nlls).mean())

    logger.info(f"model:      {args.model_id}")
    logger.info(f"max length: {args.max_length}")
    logger.info(f"stride:     {args.stride}")
    logger.info(f"perplexity: {ppl.item()}")

    if args.record_histogram and args.output_dir is not None:
        os.makedirs(args.output_dir, exist_ok=True)
        plot_layer_distribution(model, args.output_dir)
        plot_layer_range(model, args.output_dir)

if __name__ == "__main__":
    args = parse_args()
    run_task(main, args)
