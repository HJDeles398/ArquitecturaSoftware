from django.http import JsonResponse
from .models import Biblioteca, Usuario, Libro, Prestamo
from django.views.decorators.csrf import csrf_exempt
from .forms import BibliotecaForm, LibroForm, UsuarioForm, PrestamoForm
from django.shortcuts import render, redirect, get_object_or_404
import json
import datetime
from django.db.models import Prefetch
from django.utils import timezone
from django.contrib import messages

def inicio(request):
    contexto = {'mensaje': '¡Bienvenid@ a mi Biblioteca Virtual de Hilario Javier Del Valle Escolar!'}
    return render(request, 'inicio.html', contexto)


#PETICIONES JSON
#Biblioteca
@csrf_exempt
def crearBiblioteca(request):
    if request.method == 'POST':
        
        try:
            data = json.loads(request.body)
            biblioteca = Biblioteca.objects.create( direccion = data['direccion'] )
            return JsonResponse({"mensaje": "Biblioteca registrada con exito", "id": biblioteca.id ,"direccion": biblioteca.direccion})
        except:
            return JsonResponse({"error": "Error al crear la biblioteca"}, status=400)
        
    return JsonResponse({"error": "Método no permitido"}, status=405)


def obtener_bibliotecas():
    return list(Biblioteca.objects.values("id", "direccion"))
@csrf_exempt
def listarBibliotecas(request):
    return JsonResponse(obtener_bibliotecas(), safe=False)


def obtener_biblioteca_detalle(id_biblioteca):
    try:
        return Biblioteca.objects.get(id=id_biblioteca)
    except Biblioteca.DoesNotExist:
        return None
@csrf_exempt
def detalleBiblioteca(request, id_biblioteca):
    biblioteca = obtener_biblioteca_detalle(id_biblioteca)
    if biblioteca:
        return JsonResponse({'direccion': biblioteca.direccion})
    else:
        return JsonResponse({"error": "Biblioteca no encontrada"}, status=404)
    

#Libro
@csrf_exempt
def crearLibro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_biblioteca = data.get('biblioteca')
            titulo = data.get('titulo', '').strip()# Eliminar espacios en blanco, para que no haya problemas en la verificacion

            # Extra: Verificar que el título no esté vacío
            if not titulo:
                return JsonResponse({"error": "El título del libro no puede estar vacío"}, status=400)

            try:
                biblioteca = Biblioteca.objects.get(id=id_biblioteca)
            except Biblioteca.DoesNotExist:
                return JsonResponse({"error": "Biblioteca no encontrada"}, status=404)

            libro = Libro.objects.create(
                titulo=titulo,
                autor=data['autor'],
                biblioteca=biblioteca
            )

            return JsonResponse({
                "mensaje": "Libro registrado con éxito",
                "id_libro": libro.id
            })

        except KeyError:
            return JsonResponse({"error": "Datos incompletos"}, status=400)
        
    return JsonResponse({"error": "Método no permitido"}, status=405)


def obtener_libros_en_biblioteca(id_biblioteca, disponible=None):
    try:
        biblioteca = Biblioteca.objects.get(id=id_biblioteca)
    except Biblioteca.DoesNotExist:
        return None, []

    libros = Libro.objects.filter(biblioteca=biblioteca)

    if disponible is not None:
        if disponible.lower() == "true":
            libros = libros.exclude(prestamo__fecha_devolucion__isnull=True)
        elif disponible.lower() == "false":
            libros = libros.filter(prestamo__fecha_devolucion__isnull=True)

    return biblioteca, libros
@csrf_exempt
def listarLibrosEnBiblioteca(request, id_biblioteca):
    disponible = request.GET.get('disponible')
    biblioteca, libros_queryset = obtener_libros_en_biblioteca(id_biblioteca, disponible)

    if biblioteca is None:
        return JsonResponse({"error": "Biblioteca no encontrada"}, status=404)

    libros = libros_queryset.values("id", "titulo", "autor")
    if not libros.exists():
        return JsonResponse({"mensaje": "No hay libros en esta biblioteca con el criterio seleccionado"}, status=200)

    return JsonResponse(list(libros), safe=False)



@csrf_exempt
def detalleLibro(request, id_libro):
    try:
        libro = Libro.objects.values("titulo", "autor", "biblioteca").get(id=id_libro)
        return JsonResponse(libro)
    except Libro.DoesNotExist:
        return JsonResponse({"error": "Libro no encontrado"}, status=404)

@csrf_exempt
def actualizarLibro(request, id_libro):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)  
            libro = Libro.objects.get(id=id_libro)
            id_biblioteca = data.get('biblioteca')
            new_titulo = data.get('titulo')
            new_autor = data.get('autor')

            libro.titulo = new_titulo
            libro.autor = new_autor

            if id_biblioteca:
                try:
                    biblioteca = Biblioteca.objects.get(id=id_biblioteca)
                    libro.biblioteca = biblioteca 
                except Biblioteca.DoesNotExist:
                    return JsonResponse({"error": "Biblioteca no encontrada"}, status=404)

            libro.save()

            return JsonResponse({
                "id": libro.id,
                "titulo": libro.titulo,
                "autor": libro.autor,
                "biblioteca": {
                    "id": libro.biblioteca.id,
                    "direccion": libro.biblioteca.direccion
                }
            })

        except Libro.DoesNotExist:
            return JsonResponse({"error": "Libro no encontrado"}, status=404)
        
        except KeyError:
            return JsonResponse({"error": "Datos incompletos"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def eliminarLibro(request, id_libro):
    if request.method == 'DELETE':
        try:
            libro = Libro.objects.get(id=id_libro)
            libro.delete()
            return JsonResponse({"mensaje":"Libro borrado", "titulo": libro.titulo})
        except Libro.DoesNotExist:
            return JsonResponse({"error": "Libro no encontrado"}, status=404)  
    return JsonResponse({"error": "Método no permitido"}, status=405) 
    

#Usuario

@csrf_exempt
def crearUsuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            usuario = Usuario.objects.create(
                nombre=data['nombre'],
                apellido=data['apellido']
            )
            return JsonResponse({
                "mensaje": "Usuario registrado con éxito", 
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido
            })
        except KeyError:
            return JsonResponse({"error": "Datos incompletos."}, status=400)
        except Exception as e:
            #Es mas explicito con el error
            return JsonResponse({"error": f"Error al crear el usuario: {str(e)}"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def listarUsuarios(request):
    usuarios = list(Usuario.objects.values("nombre"))
    return JsonResponse(usuarios, safe=False)

@csrf_exempt
def detalleUsuario(request, id_usuario):    
    try:
        usuario = Usuario.objects.values("nombre", "apellido").get(id=id_usuario)
        return JsonResponse(usuario)
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

#Prestamo
@csrf_exempt
def crearPrestamo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id_usuario = data.get('usuario')
            id_libro = data.get('libro')

            try:
                usuario = Usuario.objects.get(id=id_usuario)
            except Usuario.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)

            try:
                libro = Libro.objects.get(id=id_libro)
            except Libro.DoesNotExist:
                return JsonResponse({"error": "Libro no encontrado"}, status=404)

            # Extra: Miro a ver si el libro ya está prestado
            if Prestamo.objects.filter(libro=libro, fecha_devolucion__isnull=True).exists():
                return JsonResponse({"error": "El libro ya está prestado"}, status=400)

            prestamo = Prestamo.objects.create(
                fecha_prestamo=datetime.date.today(),
                fecha_devolucion=None,
                usuario=usuario,
                libro=libro
            )

            return JsonResponse({
                "mensaje": "Préstamo registrado con éxito",
                "id_prestamo": prestamo.id,
                "usuario": {
                    "id": usuario.id,
                    "nombre": usuario.nombre
                },
                "libro": {
                    "id": libro.id,
                    "titulo": libro.titulo
                },
                "fecha_prestamo": prestamo.fecha_prestamo.isoformat(),
                "fecha_devolucion": prestamo.fecha_devolucion
            })
        
        except KeyError:
            return JsonResponse({"error": "Datos incompletos"}, status=400)
    
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def listarPrestamosActivos(request):    
    prestamos = list(Prestamo.objects.filter(fecha_devolucion__isnull=True)
                                    .values("usuario", "libro", "fecha_prestamo"))
    
    if prestamos:
        return JsonResponse(prestamos, safe=False)
    
    return JsonResponse({"error": "No hay préstamos activos"}, status=404)

@csrf_exempt
def prestamosUsuario(request, id_usuario):

    if not Usuario.objects.filter(id=id_usuario).exists():
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

    prestamos = list(Prestamo.objects.filter(usuario_id=id_usuario)
                                     .values("fecha_prestamo", 
                                             "fecha_devolucion", 
                                             #doble para acceder a los campos de las tablas relacionadas
                                             "libro__titulo")) 

    if not prestamos:  
        return JsonResponse({"error": "No hay préstamos para este usuario"}, status=404)

    return JsonResponse(prestamos, safe=False)

@csrf_exempt
def devolverPrestamo(request, id_prestamo):
    if request.method == 'PUT':
        try:
            prestamo = Prestamo.objects.get(id=id_prestamo)
            
            # Verifico si el préstamo ya ha sido devuelto
            if prestamo.fecha_devolucion is not None:
                return JsonResponse({"error": "El préstamo ya ha sido devuelto"}, status=400)
            
            prestamo.fecha_devolucion = datetime.date.today()  # Fecha actual como fecha de devolución
            prestamo.save()

            return JsonResponse({
                "id": prestamo.id,
                "usuario": {
                    "id": prestamo.usuario.id,
                    "nombre": prestamo.usuario.nombre
                },
                "libro": {
                    "id": prestamo.libro.id,
                    "titulo": prestamo.libro.titulo
                },
                "fecha_prestamo": prestamo.fecha_prestamo,
                "fecha_devolucion": prestamo.fecha_devolucion
            })

        except Prestamo.DoesNotExist:
            return JsonResponse({"error": "Préstamo no encontrado"}, status=404)

    return JsonResponse({"error": "Método no permitido"}, status=405)


# Formularios // Páginas Practica Evaluable 2
def nuevaBiblioteca(request):
    if request.method == 'POST':
        form = BibliotecaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Biblioteca creada con éxito.")
            return redirect('paginaBiblioteca')
        else:
            messages.error(request, "❌ Error al crear la biblioteca.")
    else:
        form = BibliotecaForm()
    return render(request, 'biblioteca/formCrearBiblioteca.html', {'form': form, 'titulo': 'Nueva Biblioteca'})


def paginaBiblioteca(request):
    return render(request, 'biblioteca/biblioteca.html', {'lista': obtener_bibliotecas()})

def detalleBibliotecaPagina(request, id_biblioteca):
    disponible = request.GET.get('disponible') 
    biblioteca, libros = obtener_libros_en_biblioteca(id_biblioteca, disponible)

    if biblioteca is None:
        return render(request, 'biblioteca/detalleBibliotecaPagina.html', {
            'error': "Biblioteca no encontrada"
        })

    return render(request, 'biblioteca/detalleBibliotecaPagina.html', {
        'biblioteca': biblioteca,
        'libros': libros
    })


def nuevoLibro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Libro creado con éxito.")
            return redirect('paginaLibro')
        else:
            messages.error(request, "❌ Error al crear el libro.")
    else:
        form = LibroForm()
    return render(request, 'libro/formCrearLibro.html', {'form': form, 'titulo': 'Nuevo Libro'})

def paginaLibro(request):
    bibliotecas = Biblioteca.objects.prefetch_related(
        Prefetch('libro_set', queryset=Libro.objects.all())
    )
    return render(request, 'libro/libro.html', {
        'bibliotecas': bibliotecas
    })

def detalleLibroPagina(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    
    esta_prestado = libro.prestamo_set.filter(fecha_devolucion__isnull=True).exists()

    return render(request, 'libro/detalleLibroPagina.html', {
        'libro': libro,
        'disponible': not esta_prestado
    })

def editarLibro(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    if request.method == 'POST':
        form = LibroForm(request.POST, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Libro actualizado con éxito.")
            return redirect('detalleLibroPagina', id_libro=libro.id)
        else:
            messages.error(request, "❌ Error al actualizar el libro.")
    else:
        form = LibroForm(instance=libro)
    return render(request, 'libro/formEditarLibro.html', {'form': form, 'titulo': 'Editar Libro'})

def eliminarLibro(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    if request.method == 'POST':
        libro.delete()
        messages.success(request, "Libro eliminado con éxito.")
        return redirect('paginaLibro')
    return render(request, 'libro/formEliminarLibro.html', {'libro': libro})


def nuevoUsuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Usuario creado con éxito.")
            return redirect('paginaUsuario')
        else:
            messages.error(request, "❌ Error al crear el usuario.")
    else:
        form = UsuarioForm()
    return render(request, 'usuario/formCrearUsuario.html', {'form': form, 'titulo': 'Nuevo Usuario'})

def paginaUsuario(request):
    return render(request, 'usuario/usuario.html', {'lista': Usuario.objects.all()})

def detalleUsuarioPagina(request, id_usuario):
    usuario = get_object_or_404(Usuario, id=id_usuario)
    prestamos = usuario.prestamo_set.all()
    
    return render(request, 'usuario/detalleUsuarioPagina.html', {
        'usuario': usuario,
        'prestamos': prestamos
    })


def nuevoPrestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Préstamo creado con éxito.")
            return redirect('paginaPrestamo')
        else:
            messages.error(request, "❌ Error al crear el préstamo.")
    else:
        form = PrestamoForm()
    return render(request, 'prestamo/formCrearPrestamo.html', {'form': form, 'titulo': 'Nuevo Préstamo'})

# EXTRA
def paginaPrestamo(request):
    disponible = request.GET.get('disponible')

    prestamos = Prestamo.objects.select_related('usuario', 'libro')

    if disponible == 'true':
        prestamos = prestamos.filter(fecha_devolucion__isnull=False)
    elif disponible == 'false':
        prestamos = prestamos.filter(fecha_devolucion__isnull=True)

    prestamos = prestamos.order_by('-fecha_prestamo')

    return render(request, 'prestamo/prestamo.html', {
        'lista': prestamos,
        'filtro': disponible
    })

def historialPrestamoUsuario(request):
    id_usuario = request.POST.get('usuario') if request.method == 'POST' else request.GET.get('usuario')
    
    if id_usuario:
        usuario = get_object_or_404(Usuario, id=id_usuario)
        prestamos = usuario.prestamo_set.all()
    else:
        usuario = None
        prestamos = None

    usuarios = Usuario.objects.all()

    return render(request, 'prestamo/historialPrestamoUsuarioPagina.html', {
        'usuario': usuario,
        'prestamos': prestamos,
        'usuarios': usuarios
    })

def prestamoADevuelto(request, id_prestamo):
    from .models import Prestamo
    prestamo = get_object_or_404(Prestamo, id=id_prestamo)

    if prestamo.fecha_devolucion is None:
        prestamo.fecha_devolucion = timezone.now()
        prestamo.save()
        messages.success(request, "Préstamo marcado como devuelto.")
    else:
        messages.info(request, "Este préstamo ya había sido devuelto.")

    return redirect('paginaPrestamo')
