from django import forms
from .models import UserProfileInfo

class UserForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        exclude = ['latitude','longitude']
