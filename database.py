from contextlib import contextmanager
from typing import Final, List

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    text,
    Table,
    create_engine,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
    sessionmaker,
)


# --------------------------------------
# Base Classes and Mixins
# --------------------------------------


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# noinspection SpellCheckingInspection,PyMethodParameters,PyUnresolvedReferences
class CommonMixin:
    """Mixin to add common attributes and functionality to models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Automatically generate table names based on class name."""
        return cls.__name__.lower()

    def __repr__(self) -> str:
        """String representation of the instance."""
        class_name = self.__class__.__name__
        return f"{class_name}(id={self.id!r})"


# --------------------------------------
# ORM Models
# --------------------------------------


class Client(CommonMixin, Base):
    """Represents a client entity."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    analyses: Mapped[List["Analysis"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    histolossfiles: Mapped[List["HistoLossFile"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )
    modelfiles: Mapped[List["ModelFile"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class Analysis(CommonMixin, Base):
    """Represents an analysis entity."""

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    client: Mapped["Client"] = relationship(back_populates="analyses")

    histolossfiles: Mapped[List["HistoLossFile"]] = relationship(
        secondary=lambda: analysis_histolossfile_table, back_populates="analyses"
    )
    modelfiles: Mapped[List["ModelFile"]] = relationship(
        secondary=lambda: analysis_modelfile_table, back_populates="analyses"
    )


class HistoLossFile(CommonMixin, Base):
    """Represents a historical loss file."""

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    client: Mapped["Client"] = relationship(back_populates="histolossfiles")

    analyses: Mapped[List[Analysis]] = relationship(
        secondary=lambda: analysis_histolossfile_table, back_populates="histolossfiles"
    )


analysis_histolossfile_table: Final[Table] = Table(
    "analysis_histolossfile",
    Base.metadata,
    Column("analysis_id", ForeignKey("analysis.id"), primary_key=True),
    Column("histolossfile_id", ForeignKey("histolossfile.id"), primary_key=True),
)


class ModelFile(CommonMixin, Base):
    """Base class for model files."""

    id: Mapped[int] = mapped_column(primary_key=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    years_simulated: Mapped[int] = mapped_column(nullable=False)

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    client: Mapped["Client"] = relationship(back_populates="modelfiles")

    yearlosses: Mapped[List["ModelYearLoss"]] = relationship(
        back_populates="modelfile",
        cascade="all, delete-orphan",
    )

    analyses: Mapped[List[Analysis]] = relationship(
        secondary=lambda: analysis_modelfile_table, back_populates="modelfiles"
    )

    __mapper_args__ = {
        "polymorphic_identity": "modelfile",
        "polymorphic_on": "model_type",
    }


analysis_modelfile_table: Final[Table] = Table(
    "analysis_modelfile",
    Base.metadata,
    Column("analysis_id", ForeignKey("analysis.id"), primary_key=True),
    Column("modelfile_id", ForeignKey("modelfile.id"), primary_key=True),
)


class EmpiricalModel(ModelFile):
    """Represents an empirical model."""

    id: Mapped[int] = mapped_column(ForeignKey("modelfile.id"), primary_key=True)
    threshold: Mapped[int] = mapped_column(nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "empiricalmodel",
    }


class FrequencySeverityModel(ModelFile):
    """Represents a frequency-severity model."""

    id: Mapped[int] = mapped_column(ForeignKey("modelfile.id"), primary_key=True)
    threshold: Mapped[int] = mapped_column(nullable=False)
    lossfile_id: Mapped[int] = mapped_column(ForeignKey("histolossfile.id"))
    lossfile: Mapped["HistoLossFile"] = relationship()

    frequencymodel: Mapped["FrequencyModel"] = relationship(
        back_populates="frequencyseveritymodel", cascade="all, delete-orphan"
    )
    severitymodel: Mapped["SeverityModel"] = relationship(
        back_populates="frequencyseveritymodel", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_identity": "frequencyseveritymodel",
    }


class FrequencyModel(CommonMixin, Base):
    """Represents a frequency model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    parameter_0: Mapped[float] = mapped_column(nullable=False)
    parameter_1: Mapped[float]
    parameter_2: Mapped[float]
    parameter_3: Mapped[float]
    parameter_4: Mapped[float]
    frequencyseveritymodel_id: Mapped[int] = mapped_column(
        ForeignKey("frequencyseveritymodel.id"), nullable=False
    )
    frequencyseveritymodel: Mapped["FrequencySeverityModel"] = relationship(
        back_populates="frequencymodel"
    )


class SeverityModel(CommonMixin, Base):
    """Represents a severity model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    parameter_0: Mapped[float] = mapped_column(nullable=False)
    parameter_1: Mapped[float]
    parameter_2: Mapped[float]
    parameter_3: Mapped[float]
    parameter_4: Mapped[float]
    frequencyseveritymodel_id: Mapped[int] = mapped_column(
        ForeignKey("frequencyseveritymodel.id"), nullable=False
    )
    frequencyseveritymodel: Mapped["FrequencySeverityModel"] = relationship(
        back_populates="severitymodel"
    )


class ModelYearLoss(CommonMixin, Base):
    """Represents model year loss data."""

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    loss: Mapped[float] = mapped_column(nullable=False)
    loss_type: Mapped[str] = mapped_column(String(50), nullable=False)

    modelfile_id: Mapped[int] = mapped_column(
        ForeignKey("modelfile.id"), nullable=False
    )
    modelfile: Mapped["ModelFile"] = relationship(back_populates="yearlosses")


# --------------------------------------
# Database Setup
# --------------------------------------

# DATABASE_URI = "sqlite:///tnv_database.db"
DATABASE_URI = "postgresql+psycopg2://postgres:aqzsed12@localhost:5432/tnv_database"
engine = create_engine(DATABASE_URI)

# Ensure foreign key constraints are enabled in SQLite
if engine.dialect.name == "sqlite":
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON;"))

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@contextmanager
def session_scope():
    """Provide a transactional scope for database operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()
