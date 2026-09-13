from django.contrib import admin
from .models import Course, Lesson, Challenge, UserProgress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class ChallengeInline(admin.TabularInline):
    model = Challenge
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [ChallengeInline]


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "language", "points")
    list_filter = ("language", "lesson__course")


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("firebase_uid", "challenge", "completed", "completed_at")
    list_filter = ("completed",)
