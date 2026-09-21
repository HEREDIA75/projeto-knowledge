import os
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import Course, Lesson


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
    """
    Renderiza o jogo Neon Tetris permitindo exibição em <iframe>.
    Se existir no diretório public/, serve o ficheiro; caso contrário, utiliza os templates do Django.
    """
    game_path = os.path.join(
        settings.BASE_DIR, "public", "jogos", "neon-tetris", "index.html"
    )

    if os.path.exists(game_path):
        with open(game_path, "r", encoding="utf-8") as f:
            return HttpResponse(f.read(), content_type="text/html")

    return render(request, "jogos/neon-tetris/index.html")
