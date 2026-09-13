from ninja import NinjaAPI, Router, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import Course, Challenge, UserProgress
from .schemas import CourseSchema, SubmitChallengeSchema, ProgressResponseSchema
from .auth import FirebaseAuthBearer
from core.firebase import db

api = NinjaAPI(title="Knowledge Project API", version="1.0.0")
router = Router()

# Instância da autenticação Firebase
firebase_auth = FirebaseAuthBearer()


# --- Schemas de Resposta ---
class UserProfileSchema(Schema):
    uid: str
    email: Optional[str] = None
    name: str


class HealthCheckSchema(Schema):
    status: str
    firebase_connected: bool


# --- Rotas Públicas ---
@api.get("/healthcheck", response=HealthCheckSchema, tags=["Sistema"])
def healthcheck(request):
    return {"status": "online", "firebase_connected": db is not None}


@api.get("/courses", response=List[CourseSchema], tags=["Cursos"])
def list_courses(request):
    return Course.objects.filter(is_active=True)


# --- Rotas Protegidas ---
@router.get(
    "/profile", response=UserProfileSchema, auth=firebase_auth, tags=["Usuário"]
)
def get_user_profile(request):
    user_data = request.auth
    return {
        "uid": user_data.get("uid"),
        "email": user_data.get("email"),
        "name": user_data.get("name", "Usuário"),
    }


@router.post(
    "/challenges/submit",
    response=ProgressResponseSchema,
    auth=firebase_auth,
    tags=["Desafios"],
)
def submit_challenge(request, payload: SubmitChallengeSchema):
    firebase_uid = request.auth.get("uid")
    challenge = get_object_or_404(Challenge, id=payload.challenge_id)

    is_correct = payload.submitted_code.strip() == challenge.expected_output.strip()

    progress, _ = UserProgress.objects.update_or_create(
        firebase_uid=firebase_uid,
        challenge=challenge,
        defaults={"submitted_code": payload.submitted_code, "completed": is_correct},
    )
    return progress


api.add_router("/user", router)
