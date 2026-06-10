from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime, ForeignKey, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./citysim.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


class WorldState(Base):
    __tablename__ = "world_state"
    id = Column(Integer, primary_key=True, default=1)
    tick = Column(Integer, default=0)
    sim_date = Column(String, default="1990-01-01")  # ISO date string
    running = Column(Boolean, default=False)
    tick_speed_ms = Column(Integer, default=1000)


class Plot(Base):
    __tablename__ = "plots"
    id = Column(Integer, primary_key=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    terrain = Column(String, default="grass")  # grass, river, road
    households = relationship("Household", back_populates="plot")


class Household(Base):
    __tablename__ = "households"
    id = Column(Integer, primary_key=True)
    plot_id = Column(Integer, ForeignKey("plots.id"), nullable=True)
    plot = relationship("Plot", back_populates="households")
    members = relationship("Person", back_populates="household")


class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True)
    household_id = Column(Integer, ForeignKey("households.id"))
    household = relationship("Household", back_populates="members")
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    sex = Column(String, nullable=False)  # M / F
    birth_date = Column(String, nullable=False)  # ISO date string
    alive = Column(Boolean, default=True)


def init_db():
    Base.metadata.create_all(bind=engine)
