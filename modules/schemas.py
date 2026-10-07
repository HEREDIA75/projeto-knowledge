from datetime import datetime
from typing import List, Optional
from ninja import Schema


# --- Schemas do LMS Existente ---
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


# --- SCHEMAS DO REPLANEJAMENTO ESCOLAR ---
class UploadResponseSchema(Schema):
    sucesso: bool
    arquivo: str
    escola: str
    total_registros: int
    mensagem: str


class DuplaTutoriaSchema(Schema):
    disciplina: str
    monitor: str
    nota_monitor: float
    aluno_recomposicao: str
    nota_recomposicao: float


class ReplanejamentoDashboardSchema(Schema):
    escola: str
    turma: str
    total_alunos: int
    media_geral: float
    alunos_recomposicao_count: int
    duplas_tutoria: List[DuplaTutoriaSchema]


class BoletimItemSchema(Schema):
    disciplina: str
    trabalho: float
    atividades: float
    prova: float
    prova_paulista: float
    media_final: float


class AlunoDetalheSchema(Schema):
    nome: str
    media_geral: float
    situacao_pedagogica: str
    intervencao_sugerida: str
    boletim: List[BoletimItemSchema]
