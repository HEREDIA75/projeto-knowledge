from django.test import TestCase
from modules.models import Course, Lesson, Challenge, UserProgress


class ModuleModelsTestCase(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title="Redes de Computadores",
            slug="redes-de-computadores",
            description="Trilha de Arquitetura de Redes e Protocolos",
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Modelo OSI e TCP/IP",
            order=1,
            content="Instruções sobre as 7 camadas do modelo OSI.",
        )
        self.challenge = Challenge.objects.create(
            lesson=self.lesson,
            title="Identificar Porta SSH",
            instructions="Escreva um script ou informe a porta padrão do serviço SSH.",
            language="python",
            points=20,
        )

    def test_course_creation(self):
        self.assertEqual(str(self.course), "Redes de Computadores")
        self.assertTrue(self.course.is_active)

    def test_challenge_creation(self):
        self.assertEqual(self.challenge.points, 20)
        self.assertEqual(self.challenge.lesson.course.slug, "redes-de-computadores")

    def test_user_progress_creation(self):
        progress = UserProgress.objects.create(
            firebase_uid="usr_test_firebase_123",
            challenge=self.challenge,
            completed=True,
            submitted_code="PORT = 22",
        )
        self.assertTrue(progress.completed)
        self.assertEqual(progress.challenge.points, 20)
