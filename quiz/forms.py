# forms.py
from django import forms
from .models import Participant, Quiz

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["employee_id", "name", "designation", "team_lead_name", "manager_name"]
        # Optional: placeholders/labels via widgets attrs
        widgets = {
            "employee_id": forms.TextInput(attrs={"placeholder": "e.g., EMP12345"}),
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "designation": forms.TextInput(attrs={"placeholder": "e.g., Senior Analyst"}),
            "team_lead_name": forms.TextInput(attrs={"placeholder": "Team Lead's name"}),
            "manager_name": forms.TextInput(attrs={"placeholder": "Manager's name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all visible fields
        for field_name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()




class ChooseQuizForm(forms.Form):
    quiz = forms.ModelChoiceField(
        queryset=Quiz.objects.all().order_by('title'),
        empty_label="-- Select a quiz --",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class AnswerForm(forms.Form):
    answer = forms.ChoiceField(
        choices=[],  # set dynamically per question
        widget=forms.RadioSelect,
        required=True,
        error_messages={"required": "Please select an answer before continuing."}
    )

    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options", [])
        super().__init__(*args, **kwargs)
        # options => list of strings; convert to (value, label) tuples
        self.fields["answer"].choices = [(opt, opt) for opt in options]
        # Add Bootstrap classes to radio items
        self.fields["answer"].widget.attrs.update({"class": "form-check-input"})
