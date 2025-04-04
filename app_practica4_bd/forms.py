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

class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ['usuario', 'libro']
    #Extra
    def clean_libro(self):
        libro = self.cleaned_data['libro']

        if Prestamo.objects.filter(libro=libro, fecha_devolucion__isnull=True).exists():
            raise forms.ValidationError("Este libro está siendo prestado actualmente.")

        return libro