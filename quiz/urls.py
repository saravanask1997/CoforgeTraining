# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Step 1: Minimal participant registration
    path('participant/register/', views.register_participant, name='register_participant'),

    # Step 2: Choose quiz after registration (collect quiz_id here)
    path('participant/choose-quiz/', views.choose_quiz, name='choose_quiz'),

    # Quiz flow
    path('quiz/<int:quiz_id>/<int:participant_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/<int:participant_id>/take/', views.take_quiz, name='take_quiz'),

    # Optional/others
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('complete/', views.quiz_complete, name='quiz_complete'),
    path('export/', views.export_quiz_data, name='export_quiz_data'),
]
