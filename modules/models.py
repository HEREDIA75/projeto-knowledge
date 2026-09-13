from django.db import models


class Course(models.Model):
    """Representa uma trilha de conhecimento (ex: Redes, C++, SQL, Cibersegurança)"""

    title = models.CharField(max_length=150, verbose_name="Título do Curso")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Descrição")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Representa um módulo ou lição dentro de um curso"""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=150, verbose_name="Título da Lição")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordem")
    content = models.TextField(verbose_name="Conteúdo Teórico / Instruções")

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Challenge(models.Model):
    """Representa um desafio prático de código ou quiz dentro da lição"""

    LANGUAGE_CHOICES = [
        ("python", "Python"),
        ("cpp", "C++"),
        ("sql", "SQL"),
        ("quiz", "Múltipla Escolha / Quiz"),
    ]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="challenges"
    )
    title = models.CharField(max_length=150, verbose_name="Título do Desafio")
    instructions = models.TextField(verbose_name="Enunciado do Desafio")
    language = models.CharField(
        max_length=20, choices=LANGUAGE_CHOICES, default="python"
    )
    initial_code = models.TextField(
        blank=True, verbose_name="Código Inicial (Boilerplate)"
    )
    expected_output = models.TextField(
        blank=True, verbose_name="Saída ou Resposta Esperada"
    )
    points = models.IntegerField(default=10, verbose_name="Pontuação/XP")

    def __str__(self):
        return f"{self.lesson.title} - Desafio: {self.title}"


class UserProgress(models.Model):
    """Armazena o progresso e XP acumulado pelos alunos nos desafios"""

    firebase_uid = models.CharField(
        max_length=128, db_index=True, verbose_name="UID Firebase do Aluno"
    )
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False, verbose_name="Concluído")
    submitted_code = models.TextField(blank=True, verbose_name="Código Submetido")
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("firebase_uid", "challenge")

    def __str__(self):
        return f"Aluno {self.firebase_uid} - Desafio {self.challenge_id} (Concluído: {self.completed})"
