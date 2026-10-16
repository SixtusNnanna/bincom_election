from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class AgentName(Base):
    __tablename__ = "agentname"

    name_id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(13), nullable=False)
    pollingunit_uniqueid = Column(Integer, nullable=False)


class AnnouncedLGAResult(Base):
    __tablename__ = "announced_lga_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    lga_name = Column(String(50), nullable=False)
    party_abbreviation = Column(String(4), nullable=False)
    party_score = Column(Integer, nullable=False)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)


class AnnouncedPUResult(Base):
    __tablename__ = "announced_pu_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    polling_unit_uniqueid = Column(String(50), nullable=False)
    party_abbreviation = Column(String(4), nullable=False)
    party_score = Column(Integer, nullable=False)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)


class AnnouncedStateResult(Base):
    __tablename__ = "announced_state_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    state_name = Column(String(50), nullable=False)
    party_abbreviation = Column(String(4), nullable=False)
    party_score = Column(Integer, nullable=False)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)


class AnnouncedWardResult(Base):
    __tablename__ = "announced_ward_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    ward_name = Column(String(50), nullable=False)
    party_abbreviation = Column(String(4), nullable=False)
    party_score = Column(Integer, nullable=False)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)


class LGA(Base):
    __tablename__ = "lga"

    uniqueid = Column(Integer, primary_key=True, autoincrement=True)
    lga_id = Column(Integer, nullable=False)
    lga_name = Column(String(50), nullable=False)
    state_id = Column(Integer, nullable=False)
    lga_description = Column(Text, nullable=True)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)


class Party(Base):
    __tablename__ = "party"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partyid = Column(String(11), nullable=False)
    partyname = Column(String(11), nullable=False)


class PollingUnit(Base):
    __tablename__ = "polling_unit"

    uniqueid = Column(Integer, primary_key=True, autoincrement=True)
    polling_unit_id = Column(Integer, nullable=False)
    ward_id = Column(Integer, nullable=False)
    lga_id = Column(Integer, nullable=False)
    uniquewardid = Column(Integer, nullable=True)
    polling_unit_number = Column(String(50), nullable=True)
    polling_unit_name = Column(String(50), nullable=True)
    polling_unit_description = Column(Text, nullable=True)
    lat = Column(String(255), nullable=True)
    long = Column(String(255), nullable=True)
    entered_by_user = Column(String(50), nullable=True)
    date_entered = Column(DateTime, nullable=True)
    user_ip_address = Column(String(50), nullable=True)


class State(Base):
    __tablename__ = "states"

    state_id = Column(Integer, primary_key=True)
    state_name = Column(String(50), nullable=False)


class Ward(Base):
    __tablename__ = "ward"

    uniqueid = Column(Integer, primary_key=True, autoincrement=True)
    ward_id = Column(Integer, nullable=False)
    ward_name = Column(String(50), nullable=False)
    lga_id = Column(Integer, nullable=False)
    ward_description = Column(Text, nullable=True)
    entered_by_user = Column(String(50), nullable=False)
    date_entered = Column(DateTime, nullable=False)
    user_ip_address = Column(String(50), nullable=False)
