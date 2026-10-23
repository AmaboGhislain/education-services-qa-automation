
import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from education_api.database import Base, engine, get_db
from education_api.models import (
    Payment,
    Result,
    SalaryPayment,
    Student,
    Teacher,
)


SIMULATOR_API_KEY = os.getenv(
    "SIMULATOR_API_KEY",
    "local-test-simulator-key",
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Education Services API",
    description="Student records and examination results API",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    student_number: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=1, max_length=120)
    class_name: str = Field(min_length=1, max_length=50)


class StudentResponse(StudentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ResultCreate(BaseModel):
    student_id: int = Field(gt=0)
    subject: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0, le=100, allow_inf_nan=False)
    term: str = Field(min_length=1, max_length=30)
    academic_year: str = Field(min_length=1, max_length=20)


class ResultResponse(ResultCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int

class PaymentCreate(BaseModel):
    payment_reference: str = Field(min_length=1, max_length=50)
    student_id: int = Field(gt=0)
    amount: float = Field(gt=0, allow_inf_nan=False)
    currency: str = Field(default="XAF", pattern="^XAF$")



class PaymentResponse(PaymentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime


class PaymentVerification(BaseModel):
    outcome: str = Field(pattern="^(SUCCESS|FAILED)$")


class TeacherCreate(BaseModel):
    employee_number: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=1, max_length=120)
    department: str = Field(min_length=1, max_length=100)


class TeacherResponse(TeacherCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SalaryPaymentCreate(BaseModel):
    payment_reference: str = Field(min_length=1, max_length=50)
    teacher_id: int = Field(gt=0)
    amount: float = Field(gt=0, allow_inf_nan=False)
    currency: str = Field(default="XAF", pattern="^XAF$")
    payment_month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class SalaryPaymentResponse(SalaryPaymentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime



@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/teachers",
    response_model=TeacherResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher(
    payload: TeacherCreate,
    db: Session = Depends(get_db),
):
    teacher = Teacher(**payload.model_dump())
    db.add(teacher)

    try:
        db.commit()
        db.refresh(teacher)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee number already exists",
        )

    return teacher


@app.get("/teachers", response_model=list[TeacherResponse])
def list_teachers(db: Session = Depends(get_db)):
    return db.scalars(select(Teacher).order_by(Teacher.id)).all()


@app.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
):
    teacher = db.get(Teacher, teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )

    return teacher


@app.post(
    "/salary-payments",
    response_model=SalaryPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_salary_payment(
    payload: SalaryPaymentCreate,
    db: Session = Depends(get_db),
):
    teacher = db.get(Teacher, payload.teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )

    salary_payment = SalaryPayment(**payload.model_dump())
    db.add(salary_payment)

    try:
        db.commit()
        db.refresh(salary_payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment reference already exists",
        )

    return salary_payment


@app.get(
    "/salary-payments/{salary_payment_id}",
    response_model=SalaryPaymentResponse,
)
def get_salary_payment(
    salary_payment_id: int,
    db: Session = Depends(get_db),
):
    salary_payment = db.get(SalaryPayment, salary_payment_id)

    if salary_payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary payment not found",
        )

    return salary_payment

@app.post(
    "/salary-payments/{salary_payment_id}/verify",
    response_model=SalaryPaymentResponse,
)
def verify_salary_payment(
    salary_payment_id: int,
    payload: PaymentVerification,
    x_simulator_key: str | None = Header(
        default=None,
        alias="X-Simulator-Key",
    ),
    db: Session = Depends(get_db),
):
    if (
        x_simulator_key is None
        or not secrets.compare_digest(
            x_simulator_key,
            SIMULATOR_API_KEY,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing simulator API key",
        )

    salary_payment = db.get(SalaryPayment, salary_payment_id)

    if salary_payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary payment not found",
        )

    if salary_payment.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending salary payments can be verified",
        )

    salary_payment.status = payload.outcome
    db.commit()
    db.refresh(salary_payment)

    return salary_payment

@app.get(
    "/teachers/{teacher_id}/salary-payments",
    response_model=list[SalaryPaymentResponse],
)
def get_teacher_salary_payments(
    teacher_id: int,
    db: Session = Depends(get_db),
):
    teacher = db.get(Teacher, teacher_id)

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )

    statement = (
        select(SalaryPayment)
        .where(SalaryPayment.teacher_id == teacher_id)
        .order_by(SalaryPayment.id)
    )
    return db.scalars(statement).all()
@app.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    payment = Payment(**payload.model_dump())
    db.add(payment)

    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment reference already exists",
        )

    return payment
@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@app.post(
    "/payments/{payment_id}/verify",
    response_model=PaymentResponse,
)
def verify_payment(
    payment_id: int,
    payload: PaymentVerification,
    x_simulator_key: str | None = Header(
        default=None,
        alias="X-Simulator-Key",
    ),
    db: Session = Depends(get_db),
):

    if (
        x_simulator_key is None
        or not secrets.compare_digest(
            x_simulator_key,
            SIMULATOR_API_KEY,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing simulator API key",
        )
    payment = db.get(Payment, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    if payment.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending payments can be verified",
        )

    payment.status = payload.outcome

    db.commit()
    db.refresh(payment)

    return payment


@app.get(
    "/students/{student_id}/payments",
    response_model=list[PaymentResponse],
)
def get_student_payments(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    statement = (
        select(Payment)
        .where(Payment.student_id == student_id)
        .order_by(Payment.id)
    )
    return db.scalars(statement).all()

@app.post(
    "/students",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student = Student(**payload.model_dump())
    db.add(student)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student number already exists",
        )

    return student


@app.get("/students", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(Student).order_by(Student.id)).all()


@app.post(
    "/results",
    response_model=ResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_result(payload: ResultCreate, db: Session = Depends(get_db)):
    student = db.get(Student, payload.student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    result = Result(**payload.model_dump())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@app.get("/students/{student_id}/results", response_model=list[ResultResponse])
def get_student_results(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    statement = (
        select(Result)
        .where(Result.student_id == student_id)
        .order_by(Result.id)
    )
    return db.scalars(statement).all()
