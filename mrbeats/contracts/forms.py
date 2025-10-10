from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateTimeInput
from contracts.models import ContractWork
from django.utils import timezone
from django.core.exceptions import ValidationError

current_datetime = timezone.now()

INPUT_CLASSES = "my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-150"
TEXTAREA_CLASSES = "break-words my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-150"
DATE_CLASSES = "my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-150"



class ContractWorkForm(ModelForm):
    class Meta:
        model = ContractWork
        exclude = ["client", "contractor", "status"]

    title = forms.CharField(
        label="Job Title",
        widget=TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Enter job title"
        })
    )

    details = forms.CharField(
        label="Job Details",
        widget=Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "placeholder": "Enter a requirements"
        })
    )

    wages = forms.DecimalField(
        label="Wages",
        max_digits=12,
        decimal_places=2,
        widget=TextInput(attrs={
            "class": INPUT_CLASSES,
            "type": "number",
            "placeholder": "Enter wages"
        })
    )

    deadline = forms.DateTimeField(
        label="Deadline",
        widget=DateTimeInput(attrs={
            "type": "datetime-local",
            "class": DATE_CLASSES,
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get('deadline')
        wages = cleaned_data.get('wages')
        if wages < 0:
            raise ValidationError (
                "Wages cannot be negative"
            )   
        if deadline < current_datetime:
            raise ValidationError (
                "deadline must more than time now"
            )
           
        return cleaned_data
    

