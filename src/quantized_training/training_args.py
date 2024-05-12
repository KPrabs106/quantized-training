import argparse
import collections
import json
from dataclasses import dataclass, asdict, field
from enum import Enum, IntEnum
from typing import Optional, List

from .utils import SLURM_ARGS

__all__ = [
    "add_training_args",
    "QuantizationConfig",
]


# Enum for rounding modes
class RoundingMode(IntEnum):
    nearest = 0
    floor = 1
    even = 2

    @staticmethod
    def string_enums():
        return [s.name for s in list(RoundingMode)]


class QScheme(Enum):
    PER_TENSOR = "per_tensor"
    PER_CHANNEL = "per_channel"
    PER_VECTOR = "per_vector"


DTYPE_TO_QUANT_MAX = {
    "int8": 127,
    "int4": 7,
    "posit8_1": 64,
    "fp8_e4m3": 448,
    "fp8_e5m2": 57344,
    "fp4_e2m1": 6,
}

ABBREV_MAP = {
    'dt': 'dtype',
    'qs': 'qscheme',
    'qmax': 'quant_max',
    'ahl': 'amax_history_len',
    'ax': 'ch_axis',
    'bs': 'block_size',
}

PARAMS_TYPE = {
    'dtype': str,
    'qscheme': QScheme,
    'quant_max': float,
    'amax_history_len': int,
    'ch_axis': int,
    'block_size': int,
}

qconfig_help_string = """
Input arguments as a comma-separated list. The first argument must specify the dtype.
Subsequent arguments can be specified using either abbreviations or full names.
Abbreviations and their full names:
  - dt: dtype
  - qs: qscheme
  - qmax: quant_max
  - ahl: amax_history_len
  - ax: ch_axis
  - bs: block_size

Example usage:
  --params dtype=int8,qscheme=qscheme1,quant_max=123.456,amax_history_len=10,ch_axis=1,block_size=64
or
  --params dt=int8,qs=qscheme1,qmax=123.456,ahl=10,ax=1,bs=64

Parameter details:
  - dtype (str): Data type (e.g., int8, int4, posit8_1, fp8_e4m3, fp8_e5m2, fp4_e2m1)
  - qscheme (str): Quantization scheme
  - quant_max (float): Maximum quantization value
  - amax_history_len (int): Length of the amax history (default: 50)
  - ch_axis (int): Channel axis (default: 1)
  - block_size (int): Block size (default: 32)
"""

@dataclass
class QuantizationConfig:
    dtype: str
    qscheme: str
    quant_max: float
    amax_history_len: int
    ch_axis: int
    block_size: int

    @staticmethod
    def from_str(s):
        assert(s != None), "String elem_format == None"
        s = s.lower()
        fields = s.split(',')

        # Initialize default arguments
        params = {
            'dtype': fields[0],
            'qscheme': None,
            'quant_max': DTYPE_TO_QUANT_MAX.get(fields[0]),
            'amax_history_len': 50,
            'ch_axis': 1,
            'block_size': 32,
        }

        # Parse the input string
        for item in fields[1:]:
            key, value = item.split('=')
            key = ABBREV_MAP.get(key, key)
            if key not in PARAMS_TYPE:
                raise argparse.ArgumentTypeError(f"Unknown argument: {key}")
            params[key] = PARAMS_TYPE[key](value)

        # Check argument
        if params['qscheme'] is not None and params['quant_max'] is None:
            raise argparse.ArgumentTypeError(
                f"quant_max is a required for {params['qscheme']}."
            )

        return QuantizationConfig(**params)

    def to_dict(self):
        return asdict(self)


class QSpecs(collections.UserDict):
    """
    Class for handling quantization parameters.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor inheriting from UserDict/dict.
        Args:
            *args:        Passing a dict will initialize using those entries.
        """
        super(QSpecs, self).__init__(*args, **kwargs)

        defaults = {
            "activation": None,
            "weight": None,
            "error": None,
            "quantize_forward": "gemm",
            "quantize_backward": "gemm",
            "op_fusion": None,
            "posit_exp": False,
            "posit_exp_shifted": False,
            "posit_reciprocal": False,
            "record_histogram": False,
            "use_bfloat16": False,
        }

        for k in defaults:
            if k not in self.data.keys():
                self.data[k] = defaults[k]

    def safe_json(self, indent=None):
        """
        Return json of parameters.
        """
        default = lambda o: f"<<non-serializable: {type(o).__qualname__}>>"
        return json.dumps(self.data, indent=indent, default=default)

    def __str__(self):
        return self.safe_json(indent=4)


@dataclass
class QuantizationArguments:
    project: Optional[str] = field(
        default=None,
        metadata={"help": "The name of the project where the new run will be sent."}
    )
    run_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "A short display name for this run, which is this run will be identified in the UI."
        }
    )
    run_id: Optional[str] = field(
        default=None,
        metadata={"help": "A unique ID for a wandb run, used for resuming."}
    )
    sweep_config: Optional[str] = field(
        default=None,
        metadata={"help": "Path to JSON file that stores W&B sweep configuration."}
    )
    sweep_id: Optional[str] = field(
        default=None,
        metadata={
            "help": "The unique identifier for a sweep generated by W&B CLI or Python SDK."
        }
    )
    max_trials: Optional[int] = field(
        default=None,
        metadata={"help": "The number of sweep config trials to try."}
    )
    log_level: str = field(
        default="INFO",
        metadata={
            "help": "Set the logging level",
            "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
    )
    log_file: Optional[str] = field(
        default=None,
        metadata={
            "help": "Set the logging file. If not specified, the log will be printed to stdout.",
            "nargs": '?',
            "const": ""
        }
    )
    #----------------------------------------------------
    # Training arguments
    #----------------------------------------------------
    gpu: Optional[int] = field(default=None, metadata={"help": "GPU to use."})
    do_train: bool = field(
        default=False, metadata={"help": "Whether to run training"}
    )
    sgd: bool = field(
        default=False, metadata={"help": "Whether to use SGD optimizer."}
    )
    warmup_ratio: float = field(
        default=0.0, metadata={"help": "Ratio of warmup steps in the lr scheduler."}
    )
    use_bfloat16: bool = field(
        default=False,
        metadata={
            "help": "Whether to use bf16 (mixed) precision instead of 32-bit float."
        }
    )
    num_hidden_layers: Optional[int] = field(
        default=None,
        metadata={"help": "Number of Tranformer encoder layers to use."}
    )
    lora_rank: int = field(
        default=0,
        metadata={"help": "The dimension of the low-rank matrices."}
    )
    lora_alpha: int = field(
        default=8,
        metadata={"help": "The scaling factor for the low-rank matrices."}
    )
    target_modules: List[str] = field(
        default="query,value",
        metadata={
            "help": "The modules (for example, attention blocks) to apply the LoRA update matrices.",
            "type": lambda x: x.split(','),
        }
    )
    #----------------------------------------------------
    # Quantization arguments
    #----------------------------------------------------
    activation: str = field(
        default=None,
        metadata={
            "type": QuantizationConfig.from_str,
            "help": "Activation data type and quantization configuration."
        }
    )
    weight: str = field(
        default=None,
        metadata={
            "type": QuantizationConfig.from_str,
            "help": "Weight data type and quantization configuration."
        }
    )
    error: str = field(
        default=None,
        metadata={
            "type": QuantizationConfig.from_str,
            "help": "Activation gradient data type and quantization configuration."
        }
    )
    op_fusion: Optional[str] = field(
        default=None,
        metadata={
            "help": "Fuse operation with previous GEMM to reduce quantization error.",
            "type": lambda x: x.split(','),
        }
    )
    posit_exp: bool = field(
        default=False,
        metadata={
            "help": "Whether to use posit approximated exponential function in softmax.",
        }
    )
    posit_exp_shifted: bool = field(
        default=False,
        metadata={
            "help": "Whether to use shifted posit approximated exponential function in softmax.",
        }
    )
    posit_reciprocal: bool = field(
        default=False,
        metadata={
            "help": "Whether to use posit approximated reciprocal function in softmax.",
        }
    )
    record_histogram: bool = field(
        default=False,
        metadata={
            "help": "Whether to store and plot the histogram of tensor value.",
        }
    )


def add_training_args(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description="Run quantized inference or training.")
    #----------------------------------------------------
    # Wandb and logging arguments
    #----------------------------------------------------
    parser.add_argument(
        '--project',
        default=None,
        help='The name of the project where the new run will be sent.'
    )
    parser.add_argument(
        '--run_name',
        default=None,
        help='A short display name for this run, which is this run will be identified in the UI.'
    )
    parser.add_argument(
        '--run_id',
        default=None,
        help='A unique ID for a wandb run, used for resuming.'
    )
    parser.add_argument(
        '--sweep_config',
        default=None,
        help='Path to JSON file that stores W&B sweep configuration.'
    )
    parser.add_argument(
        '--sweep_id',
        default=None,
        help='The unique identifier for a sweep generated by W&B CLI or Python SDK.'
    )
    parser.add_argument(
        "--max_trials",
        type=int,
        default=None,
        help="The number of sweep config trials to try."
    )
    parser.add_argument(
        "--log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    parser.add_argument(
        "--log_file",
        nargs='?',
        const="",
        default=None,
        help="Set the logging file. If not specified, the log will be printed to stdout."
    )
    #----------------------------------------------------
    # Training arguments
    #----------------------------------------------------
    parser.add_argument("--gpu", type=int, default=None, help="GPU to use.")
    parser.add_argument(
        "--do_train", action="store_true", help="Whether to run training"
    )
    parser.add_argument(
        "--sgd", action="store_true", help="Whether to use SGD optimizer."
    )
    parser.add_argument(
        "--warmup_ratio",
        type=float,
        default=0.0,
        help="Ratio of warmup steps in the lr scheduler."
    )
    parser.add_argument(
        "--bf16",
        action="store_true",
        help="Whether to use bf16 (mixed) precision instead of 32-bit float."
    )
    parser.add_argument(
        "--num_hidden_layers",
        type=int,
        default=None,
        help="Number of Tranformer encoder layers to use."
    )
    parser.add_argument(
        "--lora_rank",
        type=int,
        default=0,
        help="The dimension of the low-rank matrices."
    )
    parser.add_argument(
        "--lora_alpha",
        type=int,
        default=8,
        help="The scaling factor for the low-rank matrices."
    )
    parser.add_argument(
        "--target_modules",
        type=lambda x: x.split(','),
        default="query,value",
        help="The modules (for example, attention blocks) to apply the LoRA update matrices."
    )
    parser.add_argument(
        "--peft_model_id",
        default=None,
        help="Name of path of pre-trained peft adapter."
    )
    #----------------------------------------------------
    # Quantization arguments
    #----------------------------------------------------
    parser.add_argument(
        "--activation",
        default=None,
        type=QuantizationConfig.from_str,
        help=(
            "Activation quantization data type and configurations. "
            "Comma-separated key=value pairs using abbreviations or full names. "
            "See below for details:\n" + qconfig_help_string
        ),
    )
    parser.add_argument(
        "--weight",
        default=None,
        type=QuantizationConfig.from_str,
        help=(
            "Weight quantization data type and configurations. Format same as activation."
        ),
    )
    parser.add_argument(
        "--error",
        default=None,
        type=QuantizationConfig.from_str,
        help=(
            "Activation gradient quantization data type and configurations. Format same as activation."
        ),
    )
    parser.add_argument(
        "--quantize_forward",
        default='gemm',
        help=(
            "Forward operations to quantize. Choose from gemm, residual, "
            "activation, layernorm, and scaling."
        ),
    )
    parser.add_argument(
        "--quantize_backprop",
        default='gemm',
        help=(
            "Backprop operations to quantize. Choose from gemm, residual, "
            "activation, layernorm, and scaling."
        ),
    )
    parser.add_argument(
        '--force_scale_power_of_two',
        action='store_true',
        help='Whether to force the scaling factor to be a power of two.'
    )
    parser.add_argument(
        '--print_graph',
        action='store_true',
        help='Print the extracted graph module.'
    )
    parser.add_argument(
        "--op_fusion",
        type=lambda x: x.split(','),
        default=None,
        help="Fuse operation with previous GEMM to reduce quantization error.",
    )
    parser.add_argument(
        "--posit_exp",
        action="store_true",
        help="Whether to use posit approximated exponential function in softmax."
    )
    parser.add_argument(
        "--posit_exp_shifted",
        action="store_true",
        help="Whether to use shifted posit approximated exponential function in softmax."
    )
    parser.add_argument(
        "--posit_reciprocal",
        action="store_true",
        help="Whether to use posit approximated reciprocal function in softmax."
    )
    parser.add_argument(
        "--record_histogram",
        action="store_true",
        help="Whether to store and plot the histogram of tensor value.",
    )
    #----------------------------------------------------
    # Slurm arguments
    #----------------------------------------------------
    subparsers = parser.add_subparsers(help='sub-command help', dest='action')
    parser_slurm = subparsers.add_parser("slurm", help="slurm command help")
    for k, v in SLURM_ARGS.items():
        parser_slurm.add_argument("--" + k, **v)
    parser_bash = subparsers.add_parser("bash", help="bash command help")
    return parser
