# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.db import transaction
from django.contrib import messages
from .forms import ParticipantForm, ChooseQuizForm
from .models import Quiz, Question, Participant, QuizAttempt, UserAnswer
import openpyxl
import random



def home(request):
    # No unsafe links needed; template handles safe/unsafe via participant_id
    quizzes = Quiz.objects.all()
    return render(request, "index.html",{'quizzes':quizzes})


def home_quiz_list(request, participant_id=None):
    """
    HOME: Show quiz list. If we know participant_id (from session), pass it to enable 'Start Now' buttons.
    """
    participant_id = participant_id or request.session.get("participant_id")
    quizzes = Quiz.objects.all()
    # IMPORTANT: use the correct template path where your file actually resides
    return render(request, 'quiz/quiz_list.html', {
        'participant_id': participant_id,
        'quizzes': quizzes
    })



def register_participant(request):
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()                # ensure saved
            request.session['participant_id'] = participant.id  # store in session
            messages.success(request, "Registration successful. Please choose a quiz.")
            return redirect('choose_quiz')          # no kwargs needed
        return render(request, 'participants/register.html', {'form': form})
    else:
        form = ParticipantForm()
    return render(request, 'participants/register.html', {'form': form})





def choose_quiz(request):
    participant_id = request.session.get('participant_id')
    if not participant_id:
        # session expired or user jumped directly here, send them back to register
        return redirect('register_participant')

    participant = get_object_or_404(Participant, id=participant_id)


    if request.method == 'POST':
        form = ChooseQuizForm(request.POST)
        if form.is_valid():
            quiz = form.cleaned_data['quiz']
            return redirect('start_quiz', quiz_id=quiz.id, participant_id=participant.id)
    else:
        form = ChooseQuizForm()

    return render(request, 'participants/choose_quiz.html', {
        'form': form,
        'participant': participant,
    })




def start_quiz(request, quiz_id, participant_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    participant = get_object_or_404(Participant, id=participant_id)

    # Create or reuse an attempt for this participant+quiz
    attempt, _ = QuizAttempt.objects.get_or_create(
        quiz=quiz,
        participant=participant,
    )

    # Build question order
    qids = list(Question.objects.filter(quiz=quiz).values_list('id', flat=True))
    random.shuffle(qids)  # optional

    # Initialize session state for this run
    request.session['attempt_id'] = attempt.id
    request.session['question_order'] = qids
    request.session['current_index'] = 0
    request.session['options_order'] = {}   # per-question shuffled options order

    return redirect('take_quiz', quiz_id=quiz.id, participant_id=participant.id)





def take_quiz(request, quiz_id, participant_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    participant = get_object_or_404(Participant, id=participant_id)

    # --- Get attempt from session ---
    attempt_id = request.session.get('attempt_id')
    if not attempt_id:
        # Session expired or user jumped in; re-init
        return redirect('start_quiz', quiz_id=quiz.id, participant_id=participant.id)

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, quiz=quiz, participant=participant)

    # --- Get question order & current index ---
    order = request.session.get("question_order", [])
    index = request.session.get("current_index", 0)
    if not order:
        return redirect('start_quiz', quiz_id=quiz.id, participant_id=participant.id)

    if index < 0:
        index = 0
        request.session["current_index"] = 0
    if index >= len(order):
        return redirect("quiz_complete")

    question_id = order[index]
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    # --- Stable options order per question (stored in session) ---
    base_opts = [
        question.option_one, question.option_two, question.option_three,
        question.option_four, question.option_five, question.option_six,
        question.option_seven, question.option_eight, question.option_nine,
        question.option_ten,
    ]
    base_opts = [t for t in base_opts if t]

    options_map = request.session.get("options_order", {})
    qkey = str(question.id)
    if qkey in options_map and set(options_map[qkey]) == set(base_opts):
        options_texts = options_map[qkey]
    else:
        options_texts = base_opts[:]
        random.shuffle(options_texts)
        options_map[qkey] = options_texts
        request.session["options_order"] = options_map

    # --- Load previously saved answer using the attempt ---
    existing_answer = UserAnswer.objects.filter(attempt=attempt, question=question).first()
    preselected_text = existing_answer.selected_option if existing_answer else None

    if request.method == "POST":
        # Detect navigation intent
        is_prev = 'prev' in request.POST
        is_next = 'next' in request.POST

        selected_text = request.POST.get("answer")

        # Allow Previous without validation
        if is_prev:
            request.session["current_index"] = max(index - 1, 0)
            return redirect("take_quiz", quiz_id=quiz.id, participant_id=participant.id)

        # For Next/Finish, require an answer
        if is_next and not selected_text:
            messages.error(request, "Please select an answer before continuing.")
            # Do not change current index; re-render same question
            return render(request, "quiz/question_page.html", {
                "quiz": quiz,
                "participant": participant,
                "question": question,
                "options_texts": options_texts,
                "preselected_text": preselected_text,
                "index": index + 1,
                "total": len(order),
                "is_first": index == 0,
                "is_last": index == len(order) - 1,
            })

        # Save selection (if provided)
        if selected_text:
            with transaction.atomic():
                UserAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={"selected_option": selected_text},
                )

        # Advance forward
        if is_next:
            request.session["current_index"] = index + 1

        # If finished, go to completion page
        if request.session["current_index"] >= len(order):
            return redirect("quiz_complete")

        return redirect("take_quiz", quiz_id=quiz.id, participant_id=participant.id)

    # GET
    return render(request, "quiz/question_page.html", {
        "quiz": quiz,
        "participant": participant,
        "question": question,
        "options_texts": options_texts,
        "preselected_text": preselected_text,
        "index": index + 1,
        "total": len(order),
        "is_first": index == 0,
        "is_last": index == len(order) - 1,
    })




def quiz_list(request, participant_id):
    """
    Dedicated quiz list route (with participant_id in URL). If your templates are under templates/quiz/,
    render 'quiz/quiz_list.html'. Otherwise, change to your actual path.
    """
    quizzes = Quiz.objects.all()

    participant_id = request.session.get("participant_id")
    if not participant_id:
        # You can send them to participant setup or show a message
        return redirect("participant_details", quiz_id=1)
    # fetch quizzes based on participant_id if needed
    return render(request, "quiz_list.html", {})

    return render(request, 'quiz/quiz_list.html', {
        'participant_id': participant_id,
        'quizzes': quizzes
    })



def quiz_complete(request):
    return render(request, "quiz/quiz_complete.html")


@user_passes_test(lambda u: u.is_staff)
def export_quiz_data(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Quiz Responses"

    ws.append([
        "Participant ID", "Participant Name", "Designation", "Team Lead",
        "Manager", "Quiz Title", "Attempt Time", "Question ID",
        "Question", "Selected Option"
    ])

    attempts = QuizAttempt.objects.select_related('participant', 'quiz')
    for attempt in attempts:
        answers = UserAnswer.objects.select_related('question').filter(attempt=attempt)
        for a in answers:
            ws.append([
                attempt.participant.employee_id,
                attempt.participant.name,
                attempt.participant.designation,
                attempt.participant.team_lead_name,
                attempt.participant.manager_name,
                attempt.quiz.title,
                attempt.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                a.question.id,
                a.question.question,  # <-- use the correct field name
                a.selected_option
            ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=quiz_responses.xlsx"
    wb.save(response)
    return response