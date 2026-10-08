import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import Course, Lesson, RegistroReplanejamento


def dashboard_view(request):
    """Renderiza a página inicial com as trilhas de conhecimento."""
    courses = Course.objects.filter(is_active=True)
    return render(request, "dashboard.html", {"courses": courses})


def lesson_detail_view(request, slug, lesson_id):
    """Renderiza o ambiente de exercícios e editor de código."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    return render(
        request,
        "lesson_detail.html",
        {
            "course": course,
            "lesson": lesson,
            "challenges": lesson.challenges.all(),
        },
    )


def jogos_view(request):
    """Renderiza o hub/página de listagem de jogos."""
    context = {
        "jogos": [
            {
                "slug": "neon-tetris",
                "titulo": "Neon Tetris",
                "descricao": "Jogo de raciocínio e organização espacial em estética neon.",
                "url": "/jogos/neon-tetris/",
            }
        ]
    }
    return render(request, "jogos.html", context)


@xframe_options_exempt
def neon_tetris_view(request):
    game_path = os.path.join(
        settings.BASE_DIR, "public", "jogos", "neon-tetris", "index.html"
    )

    if os.path.exists(game_path):
        with open(game_path, "r", encoding="utf-8") as f:
            return HttpResponse(f.read(), content_type="text/html")

    return render(request, "jogos/neon-tetris/index.html")


def psicologia_view(request):
    return render(request, "jogos/psicologia/psicologo.html")


# --- VIEWS DO REPLANEJAMENTO ESCOLAR ---


def lista_alunos_view(request):
    """Renderiza a lista completa de alunos cadastrados via ETL para consulta do Conselho."""
    alunos = (
        RegistroReplanejamento.objects.values("nome_aluno", "escola")
        .distinct()
        .order_by("nome_aluno")
    )
    return render(request, "escola/lista_alunos.html", {"alunos": alunos})


def analytics_avancado_json_view(request, escola_slug):
    """
    Endpoint analítico que processa via Pandas/Scikit-Learn:
    1. Análise combinatória para duplas de tutoria (Monitores x Recomposição).
    2. Modelo preditivo de Machine Learning para risco de reprovação.
    """
    nome_escola = (
        "EE Prof. Walkir Vergani"
        if escola_slug == "walkir"
        else "EE Profª Maria José da Penha Frúgoli"
    )

    qs = RegistroReplanejamento.objects.filter(escola__icontains=nome_escola)
    if not qs.exists():
        return JsonResponse(
            {
                "sucesso": False,
                "mensagem": "Nenhum registro encontrado para esta escola.",
            }
        )

    # Conversão do QuerySet para DataFrame
    df = pd.DataFrame(
        list(
            qs.values(
                "nome_aluno",
                "disciplina",
                "media_final",
                "trabalho",
                "atividades",
                "prova",
                "prova_paulista",
            )
        )
    )

    # 1. Análise Combinatória para Duplas de Tutoria (Nota >= 8.5 com Nota < 5.0)
    monitores = df[df["media_final"] >= 8.5]
    recomposicao = df[df["media_final"] < 5.0]

    duplas = []
    for _, aluno in recomposicao.iterrows():
        match = monitores[monitores["disciplina"] == aluno["disciplina"]]
        if not match.empty:
            monitor_ideal = match.iloc[0]
            duplas.append(
                {
                    "disciplina": aluno["disciplina"],
                    "aluno_recomposicao": aluno["nome_aluno"],
                    "nota_aluno": float(aluno["media_final"]),
                    "monitor": monitor_ideal["nome_aluno"],
                    "nota_monitor": float(monitor_ideal["media_final"]),
                }
            )

    # 2. Aprendizado de Máquina (Random Forest Preditivo)
    features = ["trabalho", "atividades", "prova", "prova_paulista"]
    df_ml = df.dropna(subset=features + ["media_final"])

    predicoes_risco = []
    if len(df_ml) >= 10:
        X = df_ml[features]
        y = (df_ml["media_final"] < 5.0).astype(int)

        model = RandomForestClassifier(n_estimators=30, random_state=42)
        model.fit(X, y)

        df_ml["probabilidade_risco"] = model.predict_proba(X)[:, 1]
        riscos_altos = df_ml[df_ml["probabilidade_risco"] > 0.6].drop_duplicates(
            subset=["nome_aluno"]
        )

        for _, row in riscos_altos.iterrows():
            predicoes_risco.append(
                {
                    "aluno": row["nome_aluno"],
                    "probabilidade_reprovacao_pct": round(
                        float(row["probabilidade_risco"]) * 100, 1
                    ),
                }
            )

    return JsonResponse(
        {
            "escola": nome_escola,
            "total_alunos_analisados": int(df["nome_aluno"].nunique()),
            "duplas_tutoria_sugeridas": duplas[
                :6
            ],  # Limita a uma amostra limpa para exibição
            "alunos_em_risco_preditivo_ml": predicoes_risco[:5],
        }
    )
