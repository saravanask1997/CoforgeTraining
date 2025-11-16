from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from quiz.models import Quiz, Question, Participant, QuizAttempt, UserAnswer
from django.urls import path


class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "export_button")

    def export_button(self, obj):
        url = reverse("export_quiz_data")
        return format_html(f"<a class='button' href='{url}'>Export Excel</a>")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'order', 'question', 'points')
    list_filter = ('quiz',)
    search_fields = ('question',)
    ordering = ('quiz', 'order')
    fieldsets = (
        (None, {
            'fields': ('quiz', 'order', 'question', 'points')
        }),
        ('Media', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image OR provide an external image URL.'
        }),
    )


# Register your models here.
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question)
admin.site.register(Participant)
admin.site.register(QuizAttempt)
admin.site.register(UserAnswer)