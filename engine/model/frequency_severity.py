import numpy as np
import polars as pl
from scipy.stats import poisson, nbinom, pareto

from utils import DistributionType, LossType, DistributionInput


# Main function to generate model year loss
def get_modelyearloss_frequency_severity(
        frequency_input: DistributionInput,
        severity_input: DistributionInput,
        simulated_years: int,
        modelfile_id: int,
) -> pl.DataFrame:
    """
    Generate loss data for a frequency-severity model over a number of simulated years.

    Args:
        frequency_input (DistributionInput): Distribution defining the frequency of events per year.
        severity_input (DistributionInput): Distribution defining the severity of each event.
        simulated_years (int): Number of years to simulate.
        modelfile_id (int): ID of the related model file.

    Returns:
        dict: A dictionary with the following keys:
            - "year": List of years for each loss event.
            - "day": Random day of the year for each loss.
            - "loss": Calculated loss values.
            - "loss_type": Type of loss (e.g., catastrophic or non-catastrophic).
    """
    frequencies = generate_frequencies(frequency_input, simulated_years)
    loss_count = frequencies.sum()
    years = generate_years(frequencies.tolist())
    days = generate_days(loss_count)
    losses = generate_losses_from_parametric_dist(severity_input, loss_count)
    loss_types = generate_loss_types(loss_count)
    modelfile_ids = np.repeat(modelfile_id, loss_count)

    modelyearloss = pl.DataFrame(
        {
            "year": years,
            "day": days,
            "loss": losses,
            "loss_type": loss_types,
            "modelfile_id": modelfile_ids,
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
    years = [
        year for year, freq in enumerate(frequencies, start=1) for _ in range(freq)
    ]
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


def generate_loss_types(size: int) -> np.ndarray:
    """
    Generate random loss types (catastrophic or non-catastrophic) for events.

    Args:
        size (int): Number of loss types to generate.

    Returns:
        np.ndarray: An array of randomly chosen loss types (catastrophic or non-catastrophic).
    """
    loss_types = np.random.choice([LossType.CAT.value, LossType.NON_CAT.value], size)
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
    params = distribution_input.params

    match dist:
        case DistributionType.POISSON:
            return poisson.rvs(mu=params[0], size=size)
        case DistributionType.NEGATIVE_BINOMIAL:
            return nbinom.rvs(n=params[0], p=params[1], size=size)
        case DistributionType.PARETO:
            return pareto.rvs(scale=params[0], b=params[1], size=size)
        case _:
            raise ValueError(f"Unsupported distribution: {dist}")
