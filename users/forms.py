from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import ModelForm


User = get_user_model()


class LoginForm(AuthenticationForm):
    pass


class SignupForm(UserCreationForm, ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Email을 반드시 기입해 주세요"}),
    )
    profile_image = forms.ImageField(required=False)
    short_description = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "profile_image",
            "short_description",
        ]

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.profile_image = self.cleaned_data["profile_image"]
        user.short_description = self.cleaned_data["short_description"]
        if commit:
            user.save()
        return user
