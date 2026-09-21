from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, Schema
from ninja.errors import HttpError

# --- Autenticação Padronizada ---
from core.authentication import FirebaseHttpBearer
from core.firebase import db

# --- Models e Schemas do Módulo Principal ---
from .models import Course, Challenge, UserProgress
from .schemas import CourseSchema, SubmitChallengeSchema, ProgressResponseSchema

# --- Routers de Outros Módulos (ERP) ---
from modules.financeiro.views import router as financeiro_router

# Descomente conforme os novos módulos forem implementados:
# from modules.estoque.views import router as estoque_router
# from modules.vendas.views import router as vendas_router


firebase_auth = FirebaseHttpBearer()

# --- Instância Principal da API ---
api = NinjaAPI(
    title="ERP & Knowledge Platform API",
    version="1.0.0",
    description="API unificada para Gestão Empresarial e Plataforma Educacional",
    docs_url="/docs",
)

# --- Routers Internos do Módulo ---
user_router = Router(tags=["Usuário"])
games_router = Router(tags=["Jogos Interativos"])


# --- Schemas ---
class UserProfileSchema(Schema):
    uid: str
    email: Optional[str] = None
    name: str


class HealthCheckSchema(Schema):
    status: str
    firebase_connected: bool


class GameSchema(Schema):
    id: str
    titulo: str
    slug: str
    descricao: str
    categoria: str
    icone: str


class GameSubmitPayloadSchema(Schema):
    score: int
    tempo_segundos: Optional[int] = 0
    metadados: Optional[dict] = None


class GameSubmitResponseSchema(Schema):
    sucesso: bool
    pontos_ganhos: int
    mensagem: str


# --- Base de Dados Estática / Mapeamento de Jogos ---
JOGOS_DISPONIVEIS = [
    {
        "id": "battleship",
        "titulo": "Batalha Naval Algorítmica",
        "slug": "batalha-naval",
        "descricao": "Jogo de coordenadas e matrizes para treinar lógica de programação.",
        "categoria": "Algoritmos",
        "icone": "ship",
    },
    {
        "id": "hangman",
        "titulo": "Jogo da Forca Python",
        "slug": "jogo-da-forca",
        "descricao": "Adivinhe as palavras-chave e sintaxes da linguagem Python.",
        "categoria": "Python",
        "icone": "code",
    },
    {
        "id": "kanban",
        "titulo": "Simulador de Quadro Kanban",
        "slug": "kanban-sim",
        "descricao": "Desafio interativo de fluxo de trabalho e metodologias ágeis.",
        "categoria": "Agile",
        "icone": "kanban",
    },
]


# --- Rotas Globais / Públicas ---
@api.get("/healthcheck", response=HealthCheckSchema, tags=["Sistema"])
def healthcheck(request):
    """Verifica a integridade do sistema e conexão com o Firebase DB."""
    return {"status": "online", "firebase_connected": db is not None}


@api.get("/courses", response=List[CourseSchema], tags=["Cursos"])
def list_courses(request):
    """Lista todos os cursos ativos na plataforma."""
    return Course.objects.filter(is_active=True)


# --- Rotas do Router: Usuário ---
@user_router.get("/profile", response=UserProfileSchema, auth=firebase_auth)
def get_user_profile(request):
    """Retorna o perfil do usuário autenticado via Firebase."""
    user = request.auth
    return {
        "uid": getattr(user, "username", str(user)),
        "email": getattr(user, "email", None),
        "name": getattr(user, "first_name", None)
        or getattr(user, "username", "Usuário"),
    }


@user_router.post(
    "/challenges/submit",
    response=ProgressResponseSchema,
    auth=firebase_auth,
)
def submit_challenge(request, payload: SubmitChallengeSchema):
    """Valida o código submetido em um desafio e atualiza o progresso."""
    user = request.auth
    challenge = get_object_or_404(Challenge, id=payload.challenge_id)

    is_correct = payload.submitted_code.strip() == challenge.expected_output.strip()

    progress, _ = UserProgress.objects.update_or_create(
        user=user,
        challenge=challenge,
        defaults={"submitted_code": payload.submitted_code, "completed": is_correct},
    )
    return progress


# --- Rotas do Router: Jogos ---
@games_router.get("", response=List[GameSchema])
def listar_jogos(request):
    """Retorna a lista de jogos interativos disponíveis no portal."""
    return JOGOS_DISPONIVEIS


@games_router.get("/{slug}", response=GameSchema)
def obter_jogo(request, slug: str):
    """Retorna os detalhes de um jogo específico pelo slug ou id."""
    for jogo in JOGOS_DISPONIVEIS:
        if jogo["slug"] == slug or jogo["id"] == slug:
            return jogo
    raise HttpError(404, "Jogo não encontrado.")


@games_router.post(
    "/{slug}/submit", response=GameSubmitResponseSchema, auth=firebase_auth
)
def registrar_pontuacao_jogo(request, slug: str, payload: GameSubmitPayloadSchema):
    """Registra o progresso e a pontuação obtida pelo usuário ao finalizar uma partida."""
    user = request.auth
    pontos_calculados = payload.score * 10

    identificador = getattr(user, "email", None) or getattr(user, "username", "Usuário")

    return {
        "sucesso": True,
        "pontos_ganhos": pontos_calculados,
        "mensagem": f"Partida registrada com sucesso para o usuário {identificador}!",
    }


# --- Registro de Todos os Routers na API Unificada ---
api.add_router("/user", user_router)
api.add_router("/jogos", games_router)
api.add_router("/financeiro", financeiro_router)
# api.add_router("/estoque", estoque_router)
# api.add_router("/vendas", vendas_router)
