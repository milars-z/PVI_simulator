# interaction/bin_cutter.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinRule:
    """
    单个变量的 bin 切割规则。

    example:
        BinRule(
            key="veh_speed",
            bins=[0.0, 2.0, 5.0, 8.0, float("inf")]
        )

    对应：
        [0.0, 2.0) -> 0
        [2.0, 5.0) -> 1
        [5.0, 8.0) -> 2
        [8.0, inf) -> 3
    """

    key: str
    bins: list[float]


def bin_cut(
    value: float,
    bins: list[float],
) -> int:
    """
    将一个连续值切割到对应 bin。

    特点：
    - bins 必须严格递增
    - 返回 bin index
    - value 小于 bins[0] 时，归入第一个 bin
    - value 大于 bins[-1] 时，归入最后一个 bin

    example:
        bins = [0.0, 2.0, 5.0, 8.0, float("inf")]

        value = 1.5 -> 0
        value = 3.0 -> 1
        value = 6.0 -> 2
        value = 9.0 -> 3
    """

    _validate_bins(bins)

    if value < bins[0]:
        return 0

    for index in range(len(bins) - 1):
        left = bins[index]
        right = bins[index + 1]

        if left <= value < right:
            return index

    return len(bins) - 2


def _validate_bins(
    bins: list[float],
) -> None:
    """
    检查 bins 是否合法。
    """

    if len(bins) < 2:
        raise ValueError("bins must contain at least two values.")

    for i in range(len(bins) - 1):
        if bins[i] >= bins[i + 1]:
            raise ValueError(
                f"bins must be strictly increasing: {bins}"
            )