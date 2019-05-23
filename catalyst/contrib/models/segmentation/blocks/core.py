from abc import abstractmethod, ABC

import torch
import torch.nn as nn
import torch.nn.functional as F

from ..abn import ABN, ACT_RELU


def _get_block(
    in_channels: int,
    out_channels: int,
    abn_block: nn.Module = ABN,
    activation: str = ACT_RELU,
    first_stride: int = 1,
    second_stride: int = 1,
    complexity: int = 1,
    **kwargs
):
    layers = [
        nn.Conv2d(
            in_channels, out_channels,
            kernel_size=3, padding=1, stride=first_stride, bias=False,
            **kwargs),
        abn_block(out_channels, activation=activation),
    ]
    if complexity > 0:
        layers_ = [
            nn.Conv2d(
                out_channels, out_channels,
                kernel_size=3, padding=1, stride=second_stride, bias=False,
                **kwargs),
            abn_block(out_channels, activation=activation)
        ] * complexity
        layers = layers + layers_
    block = nn.Sequential(*layers)
    return block


def _upsample(
    x: torch.Tensor,
    scale: int = None,
    size: int = None,
    interpolation_mode: str = "bilinear",
    align_corners: bool = True
) -> torch.Tensor:
    if scale is None:
        x = F.interpolate(
            x,
            size=size,
            mode=interpolation_mode,
            align_corners=align_corners)
    else:
        x = F.interpolate(
            x,
            scale_factor=scale,
            mode=interpolation_mode,
            align_corners=align_corners)
    return x


class EncoderBlock(ABC, nn.Module):

    @property
    @abstractmethod
    def block(self) -> nn.Module:
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class CentralBlock(ABC, nn.Module):

    @property
    @abstractmethod
    def block(self) -> nn.Module:
        pass

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.block(x)


class DecoderBlock(ABC, nn.Module):

    def __init__(
        self,
        in_channels: int,
        enc_channels: int,
        out_channels: int,
        **kwargs
    ):
        super().__init__()
        self.in_channels = in_channels
        self.enc_channels = enc_channels
        self.out_channels = out_channels
        pass

    @property
    @abstractmethod
    def block(self) -> nn.Module:
        pass

    @abstractmethod
    def forward(
        self,
        down: torch.Tensor,
        left: torch.Tensor
    ) -> torch.Tensor:
        pass
