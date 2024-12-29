from dataclasses import dataclass


@dataclass
class ParsedNode:
    split_feature: str | None
    split_threshold: float | None
    lower_node: int | None
    upper_node: int | None
    expected_lifetime: float
    n_samples: int
    median_lifetime: float
    lower_lifetime: float
    upper_lifetime: float
