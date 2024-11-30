from typing import Final, List, Optional

from sqlalchemy import Column, ForeignKey, String, Table, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
    sessionmaker,
)


# --------------------------------------
# Create the SQLite database
# --------------------------------------


# Declare the models
class Base(DeclarativeBase):
    pass


class CommonMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Define a standard representation of an instance
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(id={self.id!r})"


class Client(CommonMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    # Define the 1-to-many relationship between Client and ModelFile
    modelfiles: Mapped[List["ModelFile"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class ModelFile(CommonMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    model_class: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    years_simulated: Mapped[int]

    # Define the 1-to-many relationship between Client and ModelFile
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    client: Mapped["Client"] = relationship(back_populates="modelfiles")

    # Define the 1-to-many relationship between ModelFile and ModelYearLoss
    yearlosses: Mapped[List["ModelYearLoss"]] = relationship(
        back_populates="modelfile", cascade="all, delete-orphan"
    )

    # Define the joined table inheritance for ModelFile which is the base class
    # https://docs.sqlalchemy.org/en/20/orm/inheritance.html#joined-table-inheritance
    __mapper_args__ = {
        "polymorphic_identity": "modelfile",
        "polymorphic_on": "model_class",
    }


class EmpiricalModel(ModelFile):
    id: Mapped[int] = mapped_column(ForeignKey("modelfile.id"), primary_key=True)
    threshold: Mapped[int] = Column(BigInteger)

    # Define the joined table inheritance from ModelFile
    __mapper_args__ = {
        "polymorphic_identity": "empiricalmodel",
    }


# Approx. 5k records per year
class FrequencySeverityModel(ModelFile):
    id: Mapped[int] = mapped_column(ForeignKey("modelfile.id"), primary_key=True)
    threshold: Mapped[int] = Column(BigInteger)

    # Define the joined table inheritance from ModelFile
    __mapper_args__ = {
        "polymorphic_identity": "frequencyseveritymodel",
    }


class ModelYearLoss(CommonMixin, Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int]
    day: Mapped[int]
    loss: Mapped[float]
    loss_type: Mapped[str] = mapped_column(String(50))  # Cat/Non-cat

    # Define the 1-to-many relationship between ModelFile and ModelYearLoss
    modelfile_id: Mapped[int] = mapped_column(ForeignKey("modelfile.id"))
    modelfile: Mapped["ModelFile"] = relationship(back_populates="yearlosses")


# Create an engine connected to a SQLite database
engine = create_engine("sqlite://")

# Create the database tables
Base.metadata.create_all(engine)

# Create a session to the database
Session = sessionmaker(engine)
