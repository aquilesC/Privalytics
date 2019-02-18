from django import forms

from backend.models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('user_email', 'message')
