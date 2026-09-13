from django.shortcuts import render, get_object_or_404
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
        {"course": course, "lesson": lesson, "challenges": lesson.challenges.all()},
    )
