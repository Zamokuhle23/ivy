# global
import ivy
from ivy.func_wrapper import with_unsupported_dtypes
from ivy.func_wrapper import with_supported_dtypes
from ivy.functional.frontends.paddle.func_wrapper import (
    to_ivy_arrays_and_back,
)


@with_supported_dtypes(
    {"2.5.0 and below": ("complex64", "complex128")},
    "paddle",
)
@to_ivy_arrays_and_back
def fft(x, n=None, axis=-1.0, norm="backward", name=None):
    ret = ivy.fft(ivy.astype(x, "complex128"), axis, norm=norm, n=n)
    return ivy.astype(ret, x.dtype)


@with_supported_dtypes(
    {
        "2.5.0 and below": (
            "int32",
            "int64",
            "float32",
            "float64",
            "complex64",
            "complex128",
        )
    },
    "paddle",
)
@to_ivy_arrays_and_back
def fftshift(x, axes=None, name=None):
    shape = x.shape

    if axes is None:
        axes = tuple(range(x.ndim))
        shifts = [(dim // 2) for dim in shape]
    elif isinstance(axes, int):
        shifts = shape[axes] // 2
    else:
        shifts = ivy.concat([shape[ax] // 2 for ax in axes])

    roll = ivy.roll(x, shifts, axis=axes)

    return roll


@with_supported_dtypes(
    {"2.5.0 and below": ("complex64", "complex128")},
    "paddle",
)
@to_ivy_arrays_and_back
def ifft(x, n=None, axis=-1.0, norm="backward", name=None):
    ret = ivy.ifft(ivy.astype(x, "complex128"), axis, norm=norm, n=n)
    return ivy.astype(ret, x.dtype)


@with_supported_dtypes(
    {"2.5.0 and below": ("complex64", "complex128")},
    "paddle",
)
@to_ivy_arrays_and_back
def irfft(x, n=None, axis=-1.0, norm="backward", name=None):
    if n is None:
        n = 2 * (x.shape[axis] - 1)

    pos_freq_terms = ivy.take_along_axis(x, range(n // 2 + 1), axis)
    neg_freq_terms = ivy.conj(pos_freq_terms[1:-1][::-1])
    combined_freq_terms = ivy.concat((pos_freq_terms, neg_freq_terms), axis=axis)
    time_domain = ivy.ifft(combined_freq_terms, axis, norm=norm, n=n)
    if ivy.isreal(x):
        time_domain = ivy.real(time_domain)
    return time_domain


@with_supported_dtypes(
    {
        "2.5.0 and below": (
            "int32",
            "int64",
            "float32",
            "float64",
        )
    },
    "paddle",
)
@to_ivy_arrays_and_back
def ifftshift(x, axes=None, name=None):
    shape = x.shape

    if axes is None:
        axes = tuple(range(x.ndim))
        shifts = [-(dim // 2) for dim in shape]
    elif isinstance(axes, int):
        shifts = -(shape[axes] // 2)
    else:
        shifts = ivy.concat([-shape[ax] // 2 for ax in axes])

    roll = ivy.roll(x, shifts, axis=axes)

    return roll

_SWAP_DIRECTION_MAP = {
    None: "forward",
    "backward": "forward",
    "ortho": "ortho",
    "forward": "backward",
}


def _swap_direction(norm):
    try:
        return _SWAP_DIRECTION_MAP[norm]
    except KeyError:
        raise ValueError(
            f'Invalid norm value {norm}; should be "backward", "ortho" or "forward".'
        ) from None


@with_unsupported_dtypes({"1.25.1 and below": ("float16",)}, "numpy")
@to_ivy_arrays_and_back
def rfft(a, n=None, axis=-1, norm=None):
    if norm is None:
        norm = "backward"
    a = ivy.array(a, dtype=ivy.float64)
    return ivy.dft(a, axis=axis, inverse=False, onesided=True, dft_length=n, norm=norm)

@with_supported_dtypes(
    {"2.5.0 and below": ("complex64", "complex128")},
    "paddle",
)  
@to_ivy_arrays_and_back
def ihfft(a, n=None, axis=-1, norm=None):
    if n is None:
        n = a.shape[axis]
    norm = _swap_direction(norm)
    return ivy.conj(rfft(a, n, axis, norm=norm).ivy_array)
