from django.contrib import admin
from django.urls import path
from app_practica4_bd.views import crearBiblioteca, listarBibliotecas, detalleBiblioteca, crearLibro, listarLibrosEnBiblioteca, detalleLibro, actualizarLibro, eliminarLibro, crearUsuario,listarUsuarios, detalleUsuario, crearPrestamo, listarPrestamosActivos,  prestamosUsuario, devolverPrestamo

urlpatterns = [
    path('libraries/', crearBiblioteca, name='crearBiblioteca'),
    path('libraries/listar', listarBibliotecas, name='listarBibliotecas'),
    path('libraries/<int:id_biblioteca>', detalleBiblioteca, name='detalleBiblioteca'),
    path('books/', crearLibro, name='crearLibro'),
    path('books/listar/<int:id_biblioteca>/', listarLibrosEnBiblioteca, name='listarLibrosEnBiblioteca'),
    path('books/<int:id_libro>', detalleLibro, name='detalleLibro'),
    path('books/put/<int:id_libro>', actualizarLibro, name='actualizarLibro'),
    path('books/delete/<int:id_libro>', eliminarLibro, name='eliminarLibro'),
    path('users/', crearUsuario, name="crearUsuario"),
    path('users/listar', listarUsuarios, name="listarUsuarios"),
    path('users/<int:id_usuario>', detalleUsuario, name="detalleUsuario"),
    path('loans/', crearPrestamo, name="crearPrestamo"),
    path('loans/listar/', listarPrestamosActivos, name="listarPrestamosActivos"),
    path('users/<int:id_usuario>/loans', prestamosUsuario, name="prestamosUsuario"),
    path('loans/<int:id_prestamo>/', devolverPrestamo, name="devolverPrestamo"),
]
