from django import forms

from .models import ContactMessage


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

    def __init__(self, *args, labels=None, **kwargs):
        super().__init__(*args, **kwargs)
        for name, label in (labels or {}).items():
            if name in self.fields:
                self.fields[name].label = label
                self.fields[name].widget.attrs['placeholder'] = label

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('spam')
        return data
