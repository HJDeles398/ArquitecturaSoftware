from django.db import models

class Libro(models.Model):
    titulo = models.CharField(max_length=100)
    autor = models.CharField(max_length=100)
    biblioteca = models.ForeignKey('Biblioteca', on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo
    

class Biblioteca(models.Model):
    direccion = models.CharField(max_length=100)

    def __str__(self):  
        return self.direccion

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Prestamo(models.Model):
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE) 

    def __str__(self):
        return f"{self.libro.titulo} fue prestado a {self.usuario.nombre} el {self.fecha_prestamo}"


