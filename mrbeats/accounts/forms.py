from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django.core.exceptions import ValidationError
from .models import *

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
            'class': INPUT_CLASSES,
            'placeholder': 'Enter yout username'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Enter your password (min 8 chars)'
        })
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ("created_at", "username", "password", "date_joined", "is_active")
        widgets = {
            "role": forms.TextInput(attrs={"class": "w-full px-4 py-2 rounded bg-gray-700 border border-gray-600 text-gray-100 focus:ring-purple-500 focus:border-purple-500"}),
            "artist_name": forms.TextInput(attrs={"class": "w-full px-4 py-2 rounded bg-gray-700 border border-gray-600 text-gray-100 focus:ring-purple-500 focus:border-purple-500"}),
            "bio": forms.Textarea(attrs={"class": "w-full px-4 py-2 rounded bg-gray-700 border border-gray-600 text-gray-100 focus:ring-purple-500 focus:border-purple-500 h-32 resize-none"}),
            "profile_image": forms.ClearableFileInput(attrs={"class": "w-full px-4 py-2 rounded bg-gray-700 border border-gray-600 text-gray-100 focus:ring-purple-500 focus:border-purple-500 h-32 resize-none opacity-0 absolute inset-0"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # คืนค่า password เดิม ไม่เปลี่ยน
        user.password = self.instance.password
        # คืนค่า is_active เดิม ไม่เปลี่ยน
        user.is_active = self.instance.is_active
        if commit:
            user.save()
        return user


class AccountEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500", "placeholder": "ปล่อยว่างไว้หากคุณไม่ต้องการเปลี่ยนรหัสผ่าน"}),
        label="Password"
    )

    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500",
            "placeholder": "ยืนยันรหัสผ่านอีกครั้ง"
        }),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

        widgets = {
            "username": forms.TextInput(attrs={"class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"}),
            "first_name": forms.TextInput(attrs={"class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"}),
            "last_name": forms.TextInput(attrs={"class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"}),
            "email": forms.EmailInput(attrs={"class":"w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # คืนค่า is_active เดิม ไม่เปลี่ยน
        user.is_active = self.instance.is_active
        new_password = self.cleaned_data.get("password")
        if new_password:
            user.set_password(new_password)   # เข้ารหัสใหม่ให้เรียบร้อย

        if commit:
            user.save()
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
        return cleaned_data

