from django import forms
from .models import Biblioteca, Libro, Usuario, Prestamo

class BibliotecaForm(forms.ModelForm):
    class Meta:
        model = Biblioteca
        fields = '__all__'

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'        