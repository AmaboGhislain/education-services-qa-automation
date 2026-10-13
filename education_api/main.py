
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from education_api.database import Base, engine, get_db
from education_api.models import Result, Student


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


@app.get("/health")
def health_check():
    return {"status": "ok"}


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