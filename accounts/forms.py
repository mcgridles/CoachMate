from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# User forms

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        label='f_name',
        widget=forms.TextInput(attrs={
            'placeholder': 'First Name',
            'class': 'form-control',
        }),
    )
    last_name = forms.CharField(
        max_length=30,
        label='l_name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Last Name',
            'class': 'form-control',
        }),
    )
    email = forms.EmailField(
        max_length=256,
        label='email',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control',
        }),
    )
    username = forms.CharField(
        max_length=30,
        label='username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )
    # initial password prompt
    password1 = forms.CharField(
        max_length=256,
        label='password1',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
        }),
    )
    # password confirmation prompt
    password2 = forms.CharField(
        max_length=256,
        label='password2',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        }),
    )

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password1',
            'password2',
        )


class LogInForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='username',
        widget=forms.TextInput(attrs={
            'placeholder': 'Email/Username',
            'class': 'form-control',
        }),
    )
    password = forms.CharField(
        max_length=256,
        label='password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class SettingsForm(forms.Form):
    # original password prompt
    old_passwd = forms.CharField(
        max_length=256,
        label='old password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Old Password',
            'class': 'form-control',
        }),
        required=True
    )
    # initial password prompt
    new_passwd1 = forms.CharField(
        max_length=256,
        label='new password1',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password',
            'class': 'form-control',
        }),
        required=True
    )
    # password confirmation prompt
    new_passwd2 = forms.CharField(
        max_length=256,
        label='new password2',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        }),
        required=True
    )

    class Meta:
        fields = (
            'old_passwd',
            'new_passwd1',
            'new_passwd2',
        )
