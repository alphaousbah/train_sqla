from dataclasses import dataclass
from enum import Enum


class ModelType(Enum):
    """Defines the supported loss models."""

    EMPIRICAL = "empirical"
    # FREQUENCY_SEVERITY = "frequency_severity"
    FREQUENCY_SEVERITY = "frequencyseveritymodel"
    COMPOSITE_FREQUENCY_SEVERITY = "composite_frequency_severity"
    EXPOSURE_BASED = "exposure_based"


class DistributionType(Enum):
    """Defines the supported statistical distributions."""

    POISSON = "poisson"
    NEGATIVE_BINOMIAL = "negative_binomial"
    PARETO = "pareto"


class LossType(Enum):
    """Defines the loss types."""

    CAT = "cat"
    NON_CAT = "non_cat"


@dataclass
class DistributionInput:
    """
    Configuration for a statistical distribution.

    Attributes:
        dist: The distribution type (enum).
        params: Parameters specific to the distribution.
    """

    dist: DistributionType
    params: list[float]
