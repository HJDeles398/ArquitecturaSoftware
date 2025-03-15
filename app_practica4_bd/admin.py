from django.contrib import admin

from .models import Biblioteca, Usuario, Libro, Prestamo
admin.site.register(Biblioteca)
admin.site.register(Usuario)
admin.site.register(Libro)
admin.site.register(Prestamo)
