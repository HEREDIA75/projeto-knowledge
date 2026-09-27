from django.urls import path
from django.views.generic import TemplateView
from .views import (
    dashboard_view,
    lesson_detail_view,
    jogos_view,
    neon_tetris_view,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path(
        "course/<slug:slug>/lesson/<int:lesson_id>/",
        lesson_detail_view,
        name="lesson_detail",
    ),
    path("jogos/", jogos_view, name="jogos_list"),
    path("jogos/neon-tetris/", neon_tetris_view, name="neon_tetris"),
    path("jogos/neon-tetris/index.html", neon_tetris_view),
    path(
        "jogos/psicologia/",
        TemplateView.as_view(template_name="jogos/psicologia/psicologo.html"),
        name="psicologo",
    ),
]
