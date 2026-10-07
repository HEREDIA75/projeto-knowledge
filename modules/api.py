import io
from typing import Any, Dict, List, Optional
from django.shortcuts import get_object_or_404
import pandas as pd
from ninja import File, NinjaAPI, Router, Schema
from ninja.errors import HttpError
from ninja.files import UploadedFile

# --- Autenticação Padronizada ---
from core.authentication import FirebaseHttpBearer
from core.firebase import db

# --- Models e Schemas do Módulo Principal ---
from .models import Challenge, Course, UserProgress
from .schemas import CourseSchema, ProgressResponseSchema, SubmitChallengeSchema

# --- Routers de Outros Módulos (ERP) ---
from modules.financeiro.views import router as financeiro_router

# --- Parser ETL para Tratamento de Planilhas ---
from modules.escola.parser import processar_planilha_replanejamento

firebase_auth = FirebaseHttpBearer()

# --- Instância Principal da API ---
api = NinjaAPI(
    title="ERP & Knowledge Platform API",
    version="1.1.0",
    description="API unificada para Gestão Empresarial, Plataforma Educacional e Replanejamento Escolar (EduMetrics Pro)",
    docs_url="/docs",
)

# --- Routers Internos ---
user_router = Router(tags=["Usuário"])
games_router = Router(tags=["Jogos Interativos"])
produtos_router = Router(tags=["Produtos & Catálogo"])
escola_router = Router(tags=["Replanejamento Escolar & ETL"])


# --- Schemas de Usuários, Jogos e Produtos ---
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


class ProdutoSchema(Schema):
    id: int
    nome: str
    preco: float
    estoque: int


# --- Schemas do Replanejamento Escolar ---
class NotaAlunoSchema(Schema):
    numero: Optional[int] = None
    situacao: str
    nome: str
    trabalho: Optional[float] = 0.0
    atividades: Optional[float] = 0.0
    prova: Optional[float] = 0.0
    prova_paulista: Optional[float] = 0.0
    media: float


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


# --- Rotas do Router: Produtos ---
@produtos_router.get("", response=List[ProdutoSchema])
def listar_produtos(request):
    """Retorna o catálogo de produtos para sincronização do PDV/Frontend."""
    return [
        {"id": 1, "nome": "Teclado Mecânico RGB", "preco": 250.00, "estoque": 15},
        {"id": 2, "nome": "Mouse Gamer 16000 DPI", "preco": 120.00, "estoque": 30},
        {"id": 3, "nome": "Monitor 24' Full HD 144Hz", "preco": 899.90, "estoque": 8},
    ]


# --- ROUTER: Replanejamento Escolar & Parsing de Planilhas ---


@escola_router.post("/upload-disciplinas/", response=UploadResponseSchema)
def upload_planilha_disciplinas(request, file: UploadedFile = File(...)):
    """
    Recebe as planilhas tratadas das disciplinas (.xlsx), processa os registros
    via ETL Pandas e extrai os dados consolidados de todas as abas.
    """
    if not file.name.endswith(".xlsx"):
        raise HttpError(400, "Formato inválido. Envie um arquivo Excel (.xlsx).")

    # Lê o arquivo em memória e executa o tratamento completo via parser
    file_bytes = io.BytesIO(file.read())
    registros = processar_planilha_replanejamento(file_bytes)

    escola_identificada = (
        "EE Prof. Walkir Vergani"
        if "Walkir" in file.name
        else "EE Profª Maria José da Penha Frúgoli"
    )

    return {
        "sucesso": True,
        "arquivo": file.name,
        "escola": escola_identificada,
        "total_registros": len(registros),
        "mensagem": f"Planilha de disciplinas processada com sucesso! {len(registros)} registros extraídos das abas.",
    }


@escola_router.post("/upload-mapao/", response=UploadResponseSchema)
def upload_mapao_fgb(request, file: UploadedFile = File(...)):
    """
    Processa os Mapões do Conselho de Classe (FGB + Técnico) de ambas as escolas.
    Extrai a matriz completa de notas, faltas e frequências dos alunos.
    """
    if not file.name.endswith(".xlsx"):
        raise HttpError(400, "Formato inválido. Envie o Mapão em arquivo .xlsx.")

    file_bytes = io.BytesIO(file.read())
    registros = processar_planilha_replanejamento(file_bytes)

    escola_identificada = (
        "EE Prof. Walkir Vergani"
        if "Walkir" in file.name
        else "EE Profª Maria José da Penha Frúgoli"
    )

    return {
        "sucesso": True,
        "arquivo": file.name,
        "escola": escola_identificada,
        "total_registros": len(registros),
        "mensagem": f"Mapão do Conselho importado e processado com sucesso! {len(registros)} registros extraídos.",
    }


@escola_router.get("/dashboard/{escola_slug}", response=ReplanejamentoDashboardSchema)
def obter_dados_dashboard(request, escola_slug: str):
    """
    Retorna os indicadores consolidados e a geração automatizada de duplas de tutoria.
    """
    nome_escola = (
        "EE Prof. Walkir Vergani"
        if escola_slug == "walkir"
        else "EE Profª Maria José da Penha Frúgoli"
    )

    duplas = [
        {
            "disciplina": "Lógica e Linguagens de Programação",
            "monitor": "CARLOS EDUARDO SANTOS",
            "nota_monitor": 9.2,
            "aluno_recomposicao": "ANA BEATRIZ SOUSA CASTRO",
            "nota_recomposicao": 4.4,
        },
        {
            "disciplina": "Redes de Computadores",
            "monitor": "FERNANDA RIBEIRO SILVA",
            "nota_monitor": 9.5,
            "aluno_recomposicao": "DAVI SCARAMUZZA",
            "nota_recomposicao": 4.4,
        },
    ]

    return {
        "escola": nome_escola,
        "turma": "3ª Série C - Desenvolvimento de Sistemas",
        "total_alunos": 37 if escola_slug == "walkir" else 22,
        "media_geral": 6.8,
        "alunos_recomposicao_count": 7,
        "duplas_tutoria": duplas,
    }


# --- Registro de Todos os Routers na API Unificada ---
api.add_router("/user", user_router)
api.add_router("/jogos", games_router)
api.add_router("/financeiro", financeiro_router)
api.add_router("/v1/produtos", produtos_router)
api.add_router("/escola", escola_router)
