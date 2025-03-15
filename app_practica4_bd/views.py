from django.http import JsonResponse
from .models import Biblioteca, Usuario, Libro, Prestamo
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

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

@csrf_exempt
def listarBibliotecas(request):
    bibliotecas = list(Biblioteca.objects.values("direccion"))
    return JsonResponse(bibliotecas, safe=False)

@csrf_exempt
def detalleBiblioteca(request, id_biblioteca):
    try:
        biblioteca = Biblioteca.objects.values("direccion").get(id=id_biblioteca)
        return JsonResponse(biblioteca)
    except Biblioteca.DoesNotExist:
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


@csrf_exempt
def listarLibrosEnBiblioteca(request, id_biblioteca):
    try:
        biblioteca = Biblioteca.objects.get(id=id_biblioteca)
    except Biblioteca.DoesNotExist:
        return JsonResponse({"error": "Biblioteca no encontrada"}, status=404)

    # Obtener parámetros opcionales de la URL (si existen)
    disponible = request.GET.get('disponible')  # Puede ser "true" o "false"

    # Filtrar libros por biblioteca
    libros = Libro.objects.filter(biblioteca=biblioteca)

    # Extra: Filtrar por disponibilidad (si el parámetro está presente en la solicitud)
    if disponible is not None:
        if disponible.lower() == "true":
            libros = libros.exclude(prestamo__fecha_devolucion__isnull=True)
        elif disponible.lower() == "false":
            libros = libros.filter(prestamo__fecha_devolucion__isnull=True)

    libros = libros.values("id", "titulo", "autor")

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
