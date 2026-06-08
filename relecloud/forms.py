from django import forms
from .models import Review, InfoRequest


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la reseña'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu opinión...',
                'rows': 4
            }),
        }


class InfoRequestForm(forms.ModelForm):
    class Meta:
        model = InfoRequest
        fields = ['name', 'email', 'cruise', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Tu email'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu consulta', 'rows': 4}),
            'cruise': forms.Select(attrs={'class': 'form-control'}),
        }
