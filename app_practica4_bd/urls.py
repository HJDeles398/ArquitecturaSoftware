from django.urls import path
from .views import *

urlpatterns = [

    path('inicio/', inicio, name='inicio'),
    # PETICIONES JSON   
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

    #FORMULARIOS Y PAGINAS
    path('libraries/new/', nuevaBiblioteca, name="nuevaBiblioteca"),
    path('libraries/BibliotecaPagina', paginaBiblioteca, name="paginaBiblioteca"),
    path('libraries/detalleBibliotecaPagina/<int:id_biblioteca>/', detalleBibliotecaPagina, name='detalleBibliotecaPagina'),

    path('books/new/', nuevoLibro, name="nuevoLibro"),
    path('books/LibroPagina', paginaLibro, name="paginaLibro"),
    path('books/detalleLibroPagina/<int:id_libro>/', detalleLibroPagina, name='detalleLibroPagina'),
    path('books/detalleLibroPagina/put/<int:id_libro>/', editarLibro, name='putDetalleLibroPagina'),
    path('books/detalleLibroPagina/delete/<int:id_libro>/', eliminarLibro, name='deleteDetalleLibroPagina'),


]
