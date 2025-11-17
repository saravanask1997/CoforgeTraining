from django.db import models

# Create your models here.
class Quiz(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.CharField(max_length=5000)
    image = models.ImageField(upload_to='quiz_questions/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    points = models.PositiveIntegerField(default=1)
    option_one = models.CharField(max_length=5000)
    option_two = models.CharField(max_length=5000)
    option_three = models.CharField(max_length=5000, blank=True, null=True)
    option_four = models.CharField(max_length=5000, blank=True, null=True)
    option_five = models.CharField(max_length=5000, blank=True, null=True)
    option_six = models.CharField(max_length=5000, blank=True, null=True)
    option_seven = models.CharField(max_length=5000, blank=True, null=True)
    option_eight = models.CharField(max_length=5000, blank=True, null=True)
    option_nine = models.CharField(max_length=5000, blank=True, null=True)
    option_ten = models.CharField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return self.question

class Participant(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    team_lead_name = models.CharField(max_length=100)
    manager_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"

class QuizAttempt(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts', default=1)
    created_at = models.DateTimeField(auto_now_add=True)



class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.TextField()  # storing actual text as you planned
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = "User Answer Question"
