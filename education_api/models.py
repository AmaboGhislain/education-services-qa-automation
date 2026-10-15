
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import Mapped, mapped_column, relationship

from education_api.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_number: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    class_name: Mapped[str] = mapped_column(String(50), nullable=False)

    results: Mapped[list["Result"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Result(Base):
    __tablename__ = "results"

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="valid_score"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    term: Mapped[str] = mapped_column(String(30), nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="results")

class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_payment_amount"),
        CheckConstraint(
            "status IN ('PENDING', 'SUCCESS', 'FAILED')",
            name="valid_payment_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    payment_reference: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(nullable=False)

    currency: Mapped[str] = mapped_column(
        String(3), default="XAF", nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(10), default="PENDING", nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship()