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


# --- NOVO MODEL: REPLANEJAMENTO ESCOLAR (EDUMETRICS PRO) ---
class RegistroReplanejamento(models.Model):
    """Guarda os dados importados via ETL de disciplinas técnicas e Mapões da SED"""

    TIPO_CHOICES = [
        ("DISCIPLINA_TECNICA", "Disciplina Técnica"),
        ("MAPAO_CONSELHO", "Mapão do Conselho (FGB)"),
    ]

    escola = models.CharField(max_length=255, verbose_name="Nome da Escola")
    tipo_documento = models.CharField(
        max_length=50, choices=TIPO_CHOICES, default="DISCIPLINA_TECNICA"
    )
    bimestre = models.CharField(
        max_length=50, default="3º Bimestre", verbose_name="Bimestre"
    )
    disciplina = models.CharField(max_length=150, verbose_name="Disciplina / Aba")

    numero = models.IntegerField(
        null=True, blank=True, verbose_name="Número da Chamada"
    )
    situacao = models.CharField(max_length=50, default="Ativo", verbose_name="Situação")
    nome_aluno = models.CharField(
        max_length=255, db_index=True, verbose_name="Nome do Estudante"
    )

    # Notas das avaliações
    trabalho = models.FloatField(default=0.0, verbose_name="Nota Trabalho")
    atividades = models.FloatField(default=0.0, verbose_name="Nota Atividades")
    prova = models.FloatField(default=0.0, verbose_name="Nota Prova")
    prova_paulista = models.FloatField(default=0.0, verbose_name="Nota Prova Paulista")
    media_final = models.FloatField(
        default=0.0, db_index=True, verbose_name="Média Final"
    )

    # Presença / Absenteísmo
    faltas_totais = models.FloatField(default=0.0, verbose_name="Total Faltas")
    frequencia_pct = models.CharField(
        max_length=20, default="100%", verbose_name="Frequência (%)"
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Replanejamento"
        verbose_name_plural = "Registros de Replanejamento"

    def __str__(self):
        return f"{self.nome_aluno} - {self.disciplina} ({self.escola}): Média {self.media_final}"
