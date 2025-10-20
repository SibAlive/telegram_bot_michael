from sqlalchemy import (Column, DateTime, func, Integer, ForeignKey,
                        Text, BigInteger, CHAR, Boolean, String)
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, unique=True, nullable=False, index=True)
    full_name = Column(Text, nullable=True)
    phone_number = Column(BigInteger)
    age = Column(Integer)

    finance = relationship("Finance", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("Statistic", back_populates="user", cascade="all, delete-orphan")
    appoints = relationship("Appoint", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.telegram_id}, fill_name={self.full_name}, phone_number={self.phone_number}, age={self.age})>"


class Finance(Base):
    __tablename__ = "finance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True)
    income_points = Column(Integer, default=0)
    expense_points = Column(Integer, default=0)
    date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="finance")

    def __repr__(self):
        return f"<Finance(id={self.id} user_id={self.telegram_id})>"


class Point(Base):
    """points является не таблицей, а представлением (view)"""
    __tablename__ = "points"
    __table_args__ = {"info": {"is_view": True}} # в alembic/.env создаем функцию include_object

    telegram_id = Column(BigInteger, primary_key=True)
    total_points = Column(Integer)

    # Запрещаем вставку/обновление
    __mapper_args__ = {"primary_key": [telegram_id]}

    def __repr__(self):
        return f"<Point(telegram_id={self.telegram_id}, total_points={self.total_points})>"


class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(Text)
    contact_phone = Column(BigInteger)
    date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="statistics")

    def __repr__(self):
        return f"<Statistic(id={self.id}, telegram_id={self.telegram_id}, message={self.message})>"


class Appoint(Base):
    __tablename__ = "appoints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey("doctor_slots.id", ondelete="CASCADE"), nullable=False)
    service = Column(CHAR(50), nullable=False)
    accepted = Column(Boolean, default=False, nullable=False) # Врач заполняет вручную после услуги
    # Флаг, необходимый для проверки отправлено ли сообщение с анкетой пользователю
    notified = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="appoints")
    slot = relationship("DoctorSlot", back_populates="appointments")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    speciality = Column(String(50), nullable=False)

    slot = relationship("DoctorSlot", back_populates="doctor", cascade="all, delete-orphan")


class DoctorSlot(Base):
    __tablename__ = "doctor_slots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    doctor = relationship("Doctor", back_populates="slot")
    appointments = relationship("Appoint", back_populates="slot", cascade="all, delete-orphan")