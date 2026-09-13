from ninja import Schema
from typing import List, Optional
from datetime import datetime


class CourseSchema(Schema):
    id: int
    title: str
    slug: str
    description: str
    is_active: bool


class ChallengeSchema(Schema):
    id: int
    title: str
    instructions: str
    language: str
    initial_code: Optional[str] = ""
    points: int


class LessonSchema(Schema):
    id: int
    title: str
    order: int
    content: str
    challenges: List[ChallengeSchema] = []


class SubmitChallengeSchema(Schema):
    challenge_id: int
    submitted_code: str


class ProgressResponseSchema(Schema):
    firebase_uid: str
    challenge_id: int
    completed: bool
    submitted_code: str
    completed_at: datetime
