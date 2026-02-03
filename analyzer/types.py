from dataclasses import dataclass


@dataclass(frozen=True)
class RISK:
    value: int  # 1–10

    def __post_init__(self):
        if not 1 <= self.value <= 10:
            raise ValueError("RISK must be between 1 and 10")


@dataclass(frozen=True)
class GAIN:
    value: int  # 1–10

    def __post_init__(self):
        if not 1 <= self.value <= 10:
            raise ValueError("GAIN must be between 1 and 10")