import json
import urllib.parse
import urllib.request

from django import forms
from django.conf import settings

from .models import ContactMessage


def verify_turnstile(token, remote_ip=''):
    if not (settings.TURNSTILE_SECRET_KEY and settings.TURNSTILE_SITE_KEY):
        return True
    if not token:
        return False
    try:
        data = urllib.parse.urlencode({'secret': settings.TURNSTILE_SECRET_KEY, 'response': token, 'remoteip': remote_ip}).encode()
        with urllib.request.urlopen('https://challenges.cloudflare.com/turnstile/v0/siteverify', data=data, timeout=6) as resp:
            return bool(json.loads(resp.read().decode()).get('success'))
    except Exception:
        return False


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors leave it empty, simple bots fill every field.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ['name', 'contact', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name', 'maxlength': 120}),
            'contact': forms.TextInput(attrs={'autocomplete': 'tel email', 'maxlength': 160}),
            'message': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, labels=None, turnstile_token='', remote_ip='', **kwargs):
        super().__init__(*args, **kwargs)
        self.turnstile_token = turnstile_token
        self.remote_ip = remote_ip
        for name, label in (labels or {}).items():
            if name in self.fields:
                self.fields[name].label = label
                self.fields[name].widget.attrs['placeholder'] = label

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('spam')
        if not verify_turnstile(self.turnstile_token, self.remote_ip):
            raise forms.ValidationError('turnstile')
        return data
