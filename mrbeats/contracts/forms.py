from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateTimeInput
from contracts.models import ContractWork
from django.utils import timezone
current_datetime = timezone.now()
INPUT_CLASSES = (
    "my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 "
    "rounded-lg text-white placeholder-gray-400 focus:ring-2 "
    "focus:ring-purple-500 focus:border-purple-500 transition duration-150"
)

TEXTAREA_CLASSES = (
    "break-words my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 "
    "rounded-lg text-white placeholder-gray-400 focus:ring-2 "
    "focus:ring-purple-500 focus:border-purple-500 transition duration-150"
)

DATE_INPUT_CLASSES = (
    "my-3 w-full p-3 bg-gray-900/50 border border-purple-700/70 "
    "rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-150"
)


class ContractWorkForm(ModelForm):
    class Meta:
        model = ContractWork
        exclude = ["client", "contractor", "status"]

    title = forms.CharField(
        label="Job Title",
        widget=TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Enter job title (e.g. Mixing Engineer, Beat Producer)"
        })
    )

    details = forms.CharField(
        label="Job Details",
        widget=Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "placeholder": "Describe the project details, requirements, and goals..."
        })
    )

    wages = forms.DecimalField(
        label="Wages",
        max_digits=12,
        decimal_places=2,
        widget=TextInput(attrs={
            "class": INPUT_CLASSES,
            "type": "number",
            "placeholder": "Enter budget (e.g. 500.00)"
        })
    )

    deadline = forms.DateTimeField(
        label="Deadline",
        widget=DateTimeInput(attrs={
            "type": "datetime-local",
            "class": DATE_INPUT_CLASSES,
        })
    )
    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get('deadline')
        print("Print : ",deadline)
        print("Print : ",current_datetime)
        if deadline < current_datetime:
            self.add_error("deadline",
                "deadline must more than time now"
            )
        return cleaned_data
    # role = forms.ChoiceField(
    #     choices=User.ROLE_CHOICES,
    #     widget=forms.Select(attrs={
    #         'class': SELECT_CLASSES,
    #     }),
    # )

    # password2 = forms.CharField(
    #     label="Confirm password",
    #     widget=forms.PasswordInput(attrs={
    #         'class': INPUT_CLASSES,
    #         'placeholder': 'Confirm your password'
    #     })
    # )
    # username = forms.CharField(
    #     label="Username",
    #     widget=forms.TextInput(attrs={
    #         'class': INPUT_CLASSES,
    #         'placeholder': 'Enter yout username'
    #     })
    # )
    # password1 = forms.CharField(
    #     label="Password",
    #     widget=forms.PasswordInput(attrs={
    #         'class': INPUT_CLASSES,
    #         'placeholder': 'Enter your password (min 8 chars)'
    #     })
    # )