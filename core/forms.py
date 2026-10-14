import json
import random
import urllib.parse
import urllib.request

from django import forms
from django.conf import settings

from .models import ContactMessage


def new_captcha(session):
    """Store a fresh arithmetic question in the session; return its text."""
    a, b = random.randint(2, 9), random.randint(1, 9)
    session['captcha_answer'] = a + b
    return f'{a} + {b}'


def verify_turnstile(token, remote_ip=''):
    if not settings.TURNSTILE_SECRET_KEY:
        return True
    if not token:
        return False
    try:
        data = urllib.parse.urlencode({'secret': settings.TURNSTILE_SECRET_KEY, 'response': token, 'remoteip': remote_ip}).encode()
        with urllib.request.urlopen('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data, timeout=8) as resp:
            return bool(json.loads(resp.read().decode()).get('success'))
    except Exception:
        return False


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors leave it empty, simple bots fill every field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    # Arithmetic captcha; the expected answer lives in the session.
    captcha = forms.IntegerField(widget=forms.NumberInput(attrs={'inputmode': 'numeric', 'autocomplete': 'off'}))

    class Meta:
        model = ContactMessage
        fields = ['name', 'contact', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name', 'maxlength': 120}),
            'contact': forms.TextInput(attrs={'autocomplete': 'tel email', 'maxlength': 160}),
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, labels=None, session=None, turnstile_token='', remote_ip='', **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session if session is not None else {}
        self.turnstile_token = turnstile_token
        self.remote_ip = remote_ip
        for name, label in (labels or {}).items():
            if name in self.fields:
                self.fields[name].label = label
                if name != 'captcha':
                    self.fields[name].widget.attrs['placeholder'] = label

    def clean_captcha(self):
        expected = self.session.get('captcha_answer')
        if expected is None or self.cleaned_data['captcha'] != expected:
            raise forms.ValidationError('wrong answer')
        return self.cleaned_data['captcha']

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('spam')
        if not verify_turnstile(self.turnstile_token, self.remote_ip):
            raise forms.ValidationError('turnstile')
        return data
