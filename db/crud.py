import time
from typing import Type

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeMeta, Session

from db.models import (
    Analysis,
    Client,
    FrequencyModel,
    FrequencySeverityModel,
    HistoLossFile,
    ModelType,  # TODO: To be added
    ModelYearLoss,
    PremiumFile,
    SeverityModel,
)
from engine.model.frequency_severity import (
    DistributionInput,
    get_modelyearloss_frequency_severity,
)


# Create a client
def create_client(session: Session, client_name: str):
    """
    Add a new client to the db.

    Args:
        session (Session): The SQLAlchemy session to use.
        client_name (str): The name of the client to be added.

    Raises:
        SQLAlchemyError: If a db error occurs.
        Exception: If any other unexpected error occurs.
    """
    try:
        # Create a new client
        client = Client(name=client_name)

        # Add the client to the session
        session.add(client)

        # Commit the transaction
        session.commit()
        print(f"Client '{client_name}' with ID {client.id} added successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred: {e}")
        raise

    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {e}")
        raise

    finally:
        session.close()


# Create an analysis and associate it with a client
def create_analysis(session, client_id):
    """
    Create an analysis and associates it with a client.

    Args:
        session (Session): The SQLAlchemy session to use.
        client_id (int): The ID of the client to associate the analysis with.

    Raises:
        SQLAlchemyError: If a database error occurs.
        Exception: If any other unexpected error occurs.
    """
    try:
        # Retrieve the client
        client = session.get_one(Client, client_id)

        # Create a new analysis
        analysis = Analysis()

        # Associate the analysis with the client
        client.analyses.append(analysis)

        # Commit the transaction
        session.commit()
        print(f"Analysis with ID {analysis.id} added successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred: {e}")
        raise

    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {e}")
        raise

    finally:
        session.close()


# Create a premium file and associate it with a client and an analysis
def create_premium_file(session: Session, analysis_id: int):
    """
    Create a premium file and associates it with a client and an analysis.

    Args:
        session (Session): The SQLAlchemy session to use.
        analysis_id (int): The ID of the analysis to associate the premium file with.

    Raises:
        SQLAlchemyError: If a database error occurs.
        Exception: If any other unexpected error occurs.
    """
    try:
        # Retrieve the analysis and the associated client
        analysis = session.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found.")
        client = analysis.client

        # Create the premium file
        premiumfile = PremiumFile()

        # Associate the historical loss file with the client and analysis
        client.premiumfiles.append(premiumfile)
        analysis.premiumfiles.append(premiumfile)

        # Commit the transaction
        session.commit()
        print(f"Premium file with ID {premiumfile.id} added successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred: {e}")
        raise

    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {e}")
        raise

    finally:
        session.close()


# Create a historical loss file and associate it with a client and an analysis
def create_historical_loss_file(session: Session, analysis_id: int):
    """
    Create a historical loss file and associates it with a client and an analysis.

    Args:
        session (Session): The SQLAlchemy session to use.
        analysis_id (int): The ID of the analysis to associate the historical loss file with.

    Raises:
        SQLAlchemyError: If a database error occurs.
        Exception: If any other unexpected error occurs.
    """
    try:
        # Retrieve the analysis and the associated client
        analysis = session.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found.")
        client = analysis.client

        # Create the historical loss file
        histolossfile = HistoLossFile()

        # Associate the historical loss file with the client and analysis
        client.histolossfiles.append(histolossfile)
        analysis.histolossfiles.append(histolossfile)

        # Commit the transaction
        session.commit()
        print(f"Historical loss file with ID {histolossfile.id} added successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred: {e}")
        raise

    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {e}")
        raise

    finally:
        session.close()


# Create a frequency-severity loss model
def create_frequency_severity_model(
    session: Session,
    analysis_id: int,
    lossfile_id: int,
    premiumfile_id: int,
    threshold: float,
    frequency_input: DistributionInput,
    severity_input: DistributionInput,
    cat_share: float,
    years_simulated: int,
) -> None:
    """
    Create a frequency-severity model and persists related data in the database.

    Args:
        session (Session): The SQLAlchemy session to use for database operations.
        analysis_id (int): ID of the analysis to associate the model with.
        lossfile_id (int): ID of the loss file to associate the model with.
        premiumfile_id (int): ID of the premium file to associate the model with.
        threshold (float): Threshold parameter for the model.
        frequency_input (DistributionInput): Input parameters for the frequency model.
        severity_input (DistributionInput): Input parameters for the severity model.
        cat_share (float): The proportion of losses attributed to catastrophic events.
        years_simulated (int): Number of years simulated for the model.

    Raises:
        SQLAlchemyError: If a database error occurs during the process.
        Exception: If an unexpected error occurs.
    """
    try:
        # Fetch analysis and ensure it exists
        analysis = session.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found.")

        # Create frequency and severity models
        start_time = time.perf_counter()
        frequencymodel = FrequencyModel(
            **{
                f"parameter_{i}": param
                for i, param in enumerate(frequency_input.params)
            }
        )
        severitymodel = SeverityModel(
            **{f"parameter_{i}": param for i, param in enumerate(severity_input.params)}
        )

        # Create the frequency-severity model
        modelfile = FrequencySeverityModel(
            model_type=ModelType.FREQUENCY_SEVERITY.value,  # TODO: To be corrected
            threshold=threshold,
            years_simulated=years_simulated,
            lossfile_id=lossfile_id,
            premiumfile_id=premiumfile_id,
            frequencymodel=frequencymodel,
            severitymodel=severitymodel,
        )

        # Link the model to the analysis and the client
        analysis.client.modelfiles.append(modelfile)
        analysis.modelfiles.append(modelfile)
        print(
            f"Time to create model file: {time.perf_counter() - start_time:.2f} seconds"
        )

        # Flush to get modelfile ID
        start_time = time.perf_counter()
        session.flush()
        modelfile_id = modelfile.id
        print(
            f"Time to flush the session: {time.perf_counter() - start_time:.2f} seconds"
        )

        # Generate year loss data
        start_time = time.perf_counter()
        modelyearloss = get_modelyearloss_frequency_severity(
            frequency_input, severity_input, cat_share, years_simulated, modelfile_id
        )
        print(
            f"Time to generate year loss data: {time.perf_counter() - start_time:.2f} seconds"
        )

        # Insert records into the database
        start_time = time.perf_counter()
        session.execute(insert(ModelYearLoss), modelyearloss.to_dicts())
        print(
            f"Time to insert year loss records into database: {time.perf_counter() - start_time:.2f} seconds"
        )

        # Commit the transaction
        start_time = time.perf_counter()
        session.commit()
        print(
            f"Time to commit transaction: {time.perf_counter() - start_time:.2f} seconds"
        )
        print(f"Frequency-Severity Model with ID {modelfile.id} created successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred: {e}")
        raise
    except Exception as e:
        session.rollback()
        print(f"An unexpected error occurred: {e}")
        raise
    finally:
        session.close()


# Delete a database record
def delete_db_record(
    session: Session,
    model: Type[DeclarativeMeta],
    record_id: int,
) -> None:
    """
        Delete a record from the database by its model class and ID.
    <
        Args:
            session (Session): The SQLAlchemy session to use for database operations.
            model (Type[DeclarativeMeta]): The SQLAlchemy model class of the record to delete.
            record_id (int): The ID of the record to delete.

        Raises:
            ValueError: If the record with the given ID is not found.
            SQLAlchemyError: If a database error occurs.
            Exception: For any other unexpected errors.
    """
    try:
        # Fetch the record
        record = session.get(model, record_id)
        if not record:
            raise ValueError(f"{model.__name__} record with ID {record_id} not found.")

        # Delete the record
        session.delete(record)
        session.commit()
        print(f"{model.__name__} record with ID {record_id} has been deleted.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Database error occurred while deleting {model.__name__} record: {e}")
        raise

    except Exception as e:
        session.rollback()
        print(
            f"An unexpected error occurred while deleting {model.__name__} record: {e}"
        )
        raise

    finally:
        session.close()
