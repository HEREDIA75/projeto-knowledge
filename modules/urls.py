from django.urls import path
from .views import dashboard_view, lesson_detail_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path(
        "course/<slug:slug>/lesson/<int:lesson_id>/",
        lesson_detail_view,
        name="lesson_detail",
    ),
]
