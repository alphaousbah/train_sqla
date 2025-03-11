from dataclasses import dataclass
from enum import Enum

import numpy as np
import polars as pl
from scipy.stats import nbinom, pareto, poisson


class DistributionType(Enum):
    """Defines the supported statistical distributions."""

    POISSON = "poisson"
    NEGATIVE_BINOMIAL = "negative_binomial"
    PARETO = "pareto"


class LossType(Enum):
    """Defines the loss types."""

    CAT = "cat"
    NON_CAT = "non_cat"
    CAT_NON_CAT = "cat_non_cat"


@dataclass
class DistributionInput:
    """
    Configuration for a statistical distribution.

    Attributes:
        dist: The type of distribution (enum).
        threshold: A float value representing the threshold for the distribution.
        params: A list of float values representing the parameters specific to the distribution.
    """

    dist: DistributionType
    threshold: float
    params: list[float]


# Main function to generate model year losses
def get_modelyearloss_frequency_severity(
    frequency_input: DistributionInput,
    severity_input: DistributionInput,
    cat_share: float,
    simulated_years: int,
    modelfile_id: int,
) -> pl.DataFrame:
    """
    Simulates yearly loss events based on frequency and severity distributions.

    Args:
        frequency_input (DistributionInput): Configuration for the frequency distribution.
        severity_input (DistributionInput): Configuration for the severity distribution.
        cat_share (float): The proportion of losses attributed to catastrophic events.
        simulated_years (int): Number of years to simulate loss events.
        modelfile_id (int): Unique identifier for the model file.

    Returns:
        pl.DataFrame: A Polars DataFrame containing simulated loss events, including
                      year, day, loss amount, catastrophe share, and other metadata.
    """
    # Generate frequency and loss-related data
    frequencies = generate_frequencies(frequency_input, simulated_years)
    loss_count = frequencies.sum()
    years = generate_years(frequencies.tolist())
    days = generate_days(loss_count)
    losses = generate_losses_from_parametric_dist(severity_input, loss_count)
    loss_types = generate_loss_types(cat_share, loss_count)

    # Create a default array for repeated `None` values
    none_array = np.full(loss_count, None, dtype=object)

    # Create DataFrame efficiently
    modelyearloss = pl.DataFrame(
        {
            "year": years,
            "day": days,
            "loss": losses,
            "loss_type": loss_types,
            "peril_id": none_array,
            "peril": none_array,
            "region": none_array,
            "model_hash": none_array,
            "model": none_array,
            "line_of_business": none_array,
            "modelfile_id": np.full(loss_count, modelfile_id),
        }
    )

    return modelyearloss


def generate_frequencies(
    frequency_input: DistributionInput,
    size: int,
) -> np.ndarray:
    """
    Generate a list of event frequencies based on a specified distribution.

    Args:
        frequency_input (DistributionInput): The distribution and parameters for frequency generation.
        size (int): Number of values to generate.

    Returns:
        list[int]: A list of event frequencies for each simulated year.
    """
    frequencies = get_sample_from_dist(frequency_input, size)
    return frequencies


def generate_years(frequencies: list[int]) -> list[int]:
    """
    Generate a list of years for loss events based on event frequencies.

    Args:
        frequencies (list[int]): A list where each element represents the number of events in a year.

    Returns:
        list[int]: A list of years, repeated according to their respective frequencies.
    """
    years = [year for year, freq in enumerate(frequencies) for _ in range(freq)]
    return years


def generate_days(size: int) -> np.ndarray:
    """
    Generate random days of the year for loss events.

    Args:
        size (int): Number of days to generate.

    Returns:
        np.ndarray: An array of random integers representing days (1 to 365).
    """
    days = np.random.randint(1, 366, size)
    return days


def generate_loss_types(cat_share: float, size: int) -> np.ndarray:
    """
    Generate random loss types (catastrophic or non-catastrophic) based on a given share.

    Args:
        cat_share (float): The proportion of losses classified as catastrophic (between 0 and 1).
        size (int): The number of loss types to generate.

    Returns:
        np.ndarray: An array of randomly assigned loss types, indicating whether each event is
                    catastrophic or non-catastrophic.
    """
    loss_types = np.random.choice(
        [LossType.CAT.value, LossType.NON_CAT.value],
        size=size,
        p=[cat_share, 1 - cat_share],
    )
    return loss_types


def generate_losses_from_parametric_dist(
    severity_input: DistributionInput,
    loss_count: int,
) -> np.ndarray:
    """
    Generates a set of rounded loss values from a parametric distribution.

    Args:
        severity_input (DistributionInput): Parameters defining the severity distribution.
        loss_count (int): The number of loss values to generate.

    Returns:
        np.ndarray: An array of rounded loss values.
    """
    sample = get_sample_from_dist(severity_input, loss_count)
    sample_to_int = sample.astype(int)
    return sample_to_int


def get_sample_from_dist(
    distribution_input: DistributionInput, size: int
) -> np.ndarray:
    """
    Generate a sample from the specified distribution.

    Args:
        distribution_input (DistributionInput): An object containing the distribution type
            (e.g., Poisson, Negative Binomial, Pareto) and its associated parameters.
        size (int): The number of samples to generate.

    Returns:
        np.ndarray: An array of samples drawn from the specified distribution.

    Raises:
        ValueError: If the distribution type is not supported.
    """
    dist = distribution_input.dist
    threshold = distribution_input.threshold
    params = distribution_input.params

    match dist:
        case DistributionType.POISSON:
            return poisson.rvs(mu=params[0], size=size)
        case DistributionType.NEGATIVE_BINOMIAL:
            return nbinom.rvs(n=threshold, p=params[0], size=size)
        case DistributionType.PARETO:
            return pareto.rvs(scale=threshold, b=params[0], size=size)
        case _:
            raise ValueError(f"Unsupported distribution: {dist}")
