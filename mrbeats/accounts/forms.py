from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User

INPUT_CLASSES = "my-4 w-full p-3 bg-gray-900/50 border border-purple-700/80 rounded-lg !text-white focus:ring-purple-500 focus:border-purple-500 transition duration-150"
SELECT_CLASSES = "my-4 w-full p-3 bg-gray-900/50 border border-purple-700/80 rounded-lg !text-white focus:ring-purple-500 focus:border-purple-500 transition duration-150 appearance-none pr-8"


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "role"
        ]

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': SELECT_CLASSES,
        }),
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Confirm your password'
        })
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your password (min 8 chars)'
        })
    )


