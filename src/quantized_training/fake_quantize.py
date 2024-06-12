import logging
import math
import re
from typing import Optional

import torch
from torch.ao.quantization import FakeQuantizeBase

import quantized_training as qt
from quantized_training.fp8 import (
    _quantize_elemwise_core,
    quantize_to_fp8_e4m3,
    quantize_to_fp8_e5m2,
)
from quantized_training.mx_utils import (
    _reshape_to_blocks,
    _shared_exponents,
    _undo_reshape_to_blocks,
)
from quantized_training.posit import quantize_to_posit


__all__ = [
    "FusedAmaxObsFakeQuantize",
]


logger = logging.getLogger(__name__)


def _get_fake_quant_fn(dtype: str):
    """Return the quantization function for the given dtype."""
    if (match := re.fullmatch(r'posit(\d+)_(\d+)', dtype)):
        nbits, es = match.groups()
        return lambda x: quantize_to_posit(x, int(nbits), int(es), round_to_even=True)

    if (match := re.fullmatch(r'(?:fp8\.)?(e4m3|e5m2)', dtype, re.IGNORECASE)):
        fp8_format = match.group(1).lower()
        return quantize_to_fp8_e4m3 if fp8_format == 'e4m3' else quantize_to_fp8_e5m2

    if (match := re.fullmatch(r"fp(\d+)_e(\d+)m(\d+)", dtype)):
        nbits, ebits, mbits = map(int, match.groups())
        assert nbits == ebits + mbits + 1
        mbits = mbits + 2
        emax = 2 ** (ebits - 1) - 1 if ebits > 4 else 2 ** (ebits - 1)
        if dtype != "fp8_e4m3":
            max_norm = 2**emax * float(2**(mbits-1) - 1) / 2**(mbits-2)
        else:
            max_norm = 2**emax * 1.75
        return lambda x: _quantize_elemwise_core(x, mbits, ebits, max_norm, "even", True)

    if (match := re.fullmatch(r'int(\d+)', dtype)):
        nbits = int(match.group(1))
        quant_min, quant_max = -2 ** (nbits - 1), 2 ** (nbits - 1) - 1
        return lambda x: torch.clamp(torch.round(x), quant_min, quant_max)

    raise ValueError(f"Unrecognized dtype: {dtype}")


def  _get_amax(x, qscheme, ch_axis=None):
    if qscheme == qt.per_tensor_symmetric:
        amax = torch.amax(torch.abs(x))
    elif qscheme == qt.per_channel_symmetric:
        if ch_axis < 0:
            ch_axis = ch_axis + x.ndim
        dim = tuple(i for i in range(x.ndim) if i != ch_axis)
        amax = torch.amax(torch.abs(x), dim=dim, keepdim=True)
    elif qscheme == qt.per_vector_symmetric:
        amax = torch.amax(torch.abs(x), dim=(0, ch_axis), keepdim=True)
    else:
        raise ValueError(f"Unsupported qscheme: {qscheme}")
    return amax


def _quantize(input, qvalues):
    if input.dtype == torch.bfloat16:
        indices = input.view(torch.int16).to(torch.int32) & 0xffff
    else:
        raw_bits = input.to(torch.float32).view(torch.int32)
        indices = (raw_bits >> 16) & 0xffff
        indices = indices | ((raw_bits & 0xffff) != 0).to(indices.dtype)
    return qvalues[indices].to(input.dtype)


class MXFakeQuantFunction(torch.autograd.Function):
    """This function is similar to FusedAmaxObsFakeQuantFunction, but it
    performs dynamic quantization by calculating the scaling factor on the
    run.
    """

    @staticmethod
    def forward(
        ctx,
        input,
        qvalues,
        fake_quant_enabled,
        quant_max,
        shared_exp_method="max",
        axes=None,
        block_size=0,
    ):
        if fake_quant_enabled[0] == 0:
            return input

        axes = [axes] if type(axes) == int else axes
        axes = [x + input.ndim if x < 0 else x for x in axes]

        # Perform tiling to the hardware vector size
        if block_size > 0:
            input, axes, orig_shape, padded_shape = _reshape_to_blocks(
                input, axes, block_size
            )

        shared_exp_axes = [x + 1 for x in axes] if block_size > 0 else axes

        shared_exp = _shared_exponents(
            input, method=shared_exp_method, axes=shared_exp_axes, ebits=0,
        )

        shared_exp = shared_exp - math.floor(math.log2(quant_max))
        scale = (2**shared_exp).to(input.dtype)

        input = input / scale
        input = _quantize(input, qvalues)
        input = input * scale

        # Undo tile reshaping
        if block_size:
            input = _undo_reshape_to_blocks(input, padded_shape, orig_shape, axes)

        return input

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None, None, None, None, None, None


class FusedAmaxObsFakeQuantFunction(torch.autograd.Function):
    """This function observes the amax statistics of inputs and
    quantize the inputs based on the observed amax values.
    """

    @staticmethod
    def forward(
        ctx,
        input,
        qvalues,
        observer_enabled,
        fake_quant_enabled,
        amax_history,
        scale,
        quant_max,
        qscheme,
        ch_axis=None,
        block_size=0,
        force_scale_power_of_two=False,
    ):
        if qscheme == qt.per_vector_symmetric:
            # Make sure axes is a list of non-negative numbers
            axes = [ch_axis + input.ndim if ch_axis < 0 else ch_axis]

            # Perform tiling to the hardware vector size
            if block_size > 0:
                input, axes, orig_shape, padded_shape = _reshape_to_blocks(
                    input, axes, block_size
                )
            ch_axis = axes[0] + 1

        if observer_enabled[0] == 1:
            amax = torch.amax(amax_history, dim=0)

            if amax_history.shape[0] > 1:
                new_amax_history = torch.roll(amax_history, -1, 0)
                amax_history.copy_(new_amax_history)
            amax_history[0] = _get_amax(input, qscheme, ch_axis)

            sf = amax / quant_max
            sf = torch.where(amax > 0.0, sf, scale)
            sf = torch.where(torch.isfinite(amax), sf, scale)
            if force_scale_power_of_two:
                sf = torch.pow(2, torch.floor(torch.log2(sf)))
            scale.copy_(sf)

        if fake_quant_enabled[0] == 1:
            scale = scale.to(input.dtype)
            input = input / scale
            input = _quantize(input, qvalues)
            input = input * scale

        if qscheme == qt.per_vector_symmetric:
            # Undo tile reshaping
            if block_size:
                input = _undo_reshape_to_blocks(input, padded_shape, orig_shape, axes)

        return input

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output, None, None, None, None, None, None, None, None, None, None


class FusedAmaxObsFakeQuantize(FakeQuantizeBase):
    r"""Observer module for computing the quantization parameters based on the
    historical amax values.

    This observer uses the tensor amax statistics to compute the quantization
    parameters. The module records the maximums of absolute values of output
    tensors, and uses this statistic to compute the quantization parameters.
    """
    qvalues: torch.Tensor
    amax_history: torch.Tensor
    scale: torch.Tensor

    def __init__(
        self,
        dtype: str,
        qscheme: Optional[str] = None,
        quant_max: Optional[float] = None,
        amax_history_len: int = 50,
        ch_axis: Optional[int] = None,
        block_size: Optional[int] = None,
        record_histogram: bool = False,
        force_scale_power_of_two: bool = False,
        **kwargs,
    ) -> None:
        super().__init__()
        self.dtype = dtype
        self.qscheme = qscheme
        self.quant_max = quant_max
        self.amax_history_len = amax_history_len
        self.ch_axis = ch_axis
        self.block_size = block_size
        self.force_scale_power_of_two = force_scale_power_of_two
        self.name = kwargs.get("name", None)
        device = kwargs.get("device", None)
        # Generates a mapping from bfloat16 to quantized values of the given dtype
        input = torch.arange(2 ** 16, dtype=torch.int16, device=device).view(torch.bfloat16)
        self.fake_quant_fn = _get_fake_quant_fn(dtype)
        self.register_buffer("qvalues", self.fake_quant_fn(input), persistent=False)
        # Create amax history and scale buffer
        self.enable_observer(self.qscheme is not None)
        factory_kwargs = {'device': device, 'dtype': torch.float}
        self.register_buffer("amax_history", torch.tensor([], **factory_kwargs))
        self.register_buffer('scale', torch.tensor([1.0], **factory_kwargs))
        # Create histogram buffer
        self.record_histogram = record_histogram
        self.register_buffer("histogram", torch.zeros(254, **factory_kwargs), persistent=False)

    @torch.jit.export
    def calculate_qparams(self):
        return self.scale

    @torch.jit.export
    def extra_repr(self):
        return (
            "fake_quant_enabled={}, observer_enabled={}, name={}, dtype={}, "
            "quant_max={}, qscheme={}, amax_history_len={}, ch_axis={}, "
            "block_size={}, record_histogram={}, force_scale_power_of_two={}, "
            "scale={}".format(
                self.fake_quant_enabled,
                self.observer_enabled,
                self.name,
                self.dtype,
                self.quant_max,
                self.qscheme,
                self.amax_history_len,
                self.ch_axis,
                self.block_size,
                self.record_histogram,
                self.force_scale_power_of_two,
                self.scale,
            )
        )

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        if self.record_histogram:
            exp = torch.floor(torch.log2(torch.abs(X.detach().float())))
            self.histogram += torch.histc(exp, 254, min=-126, max=127)

        # TODO: make this a separate module?
        if self.qscheme == qt.microscaling:
            return MXFakeQuantFunction.apply(
                X,
                self.qvalues,
                self.fake_quant_enabled,
                self.quant_max,
                "max",
                self.ch_axis,
                self.block_size,
            )

        if self.qscheme is not None:
            if self.amax_history.numel() == 0:
                amax_cur = _get_amax(X.detach(), self.qscheme, self.ch_axis)
                self.amax_history = torch.zeros(
                    (self.amax_history_len,) + amax_cur.shape, device=X.device
                )
                self.scale = torch.ones_like(amax_cur)

        return FusedAmaxObsFakeQuantFunction.apply(
            X,
            self.qvalues,
            self.observer_enabled,
            self.fake_quant_enabled,
            self.amax_history,
            self.scale,
            self.quant_max,
            self.qscheme,
            self.ch_axis,
            self.block_size,
            self.force_scale_power_of_two,
        )
