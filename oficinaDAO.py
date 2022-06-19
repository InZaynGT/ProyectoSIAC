from CursorDelPool import CursorDelPool
from oficina import Oficina

opcion = 0


class OficinaDAO:
    _SELECCIONAR = 'SELECT * FROM oficina3 ORDER BY no_id'
    _INSERTAR = 'INSERT INTO oficina3(no_id, nombres, apellidos, fecha, dpi, telefono, direccion, imagen) VALUES(%s, ' \
                '%s, %s, %s,%s, %s, %s, %s)'
    _ACTUALIZAR = 'UPDATE oficina3 SET nombres = %s, apellidos = %s, fecha = %s, ' \
                  'dpi = %s, Telefono = %s, Direccion = %s, imagen= %s WHERE no_id = %s'
    _ELIMINAR = 'DELETE from oficina3 WHERE no_id = %s'

    @classmethod
    def seleccionar(cls):
        with CursorDelPool() as cursor:
            cursor.execute(cls._SELECCIONAR)
            registros = cursor.fetchall()
            usuarios = []
            for registro in registros:
                usuario = Oficina(registro[0], registro[1], registro[2], registro[3], registro[4], registro[5], registro[6], registro[7])
                usuarios.append(usuario)
            return usuarios


    @classmethod
    def insertar(cls, oficina):
        with CursorDelPool() as cursor:
            valores = (oficina.NIT, oficina.Nombres, oficina.apellidos, oficina.fecha, oficina.dpi, oficina.Telefono, oficina.Direccion, oficina.imagen)
            cursor.execute(cls._INSERTAR, valores)
            return cursor.rowcount

    @classmethod
    def actualizar(cls, oficina):
        with CursorDelPool() as cursor:
            valores = (oficina.Nombres, oficina.apellidos, oficina.fecha, oficina.dpi, oficina.Telefono, oficina.Direccion, oficina.imagen, oficina.NIT)
            cursor.execute(cls._ACTUALIZAR, valores)
            return cursor.rowcount

    @classmethod
    def eliminar(cls, oficina):
        with CursorDelPool() as cursor:
            valor = (oficina.NIT,)
            cursor.execute(cls._ELIMINAR, valor)
            return cursor.rowcount


if __name__ == '__main__':

    while opcion != 5:
        opcion = 1
        m = 'BASES DE DATOS - OFICINA'
        print(m.center(40, '-'))
        print(f'Opciones:')
        print(f'1. Listar Usuarios ')
        print(f'2. Agregar Usuario ')
        print(f'3. Modificar Usuario ')
        print(f'4. Eliminar Usuario ')
        print(f'5. Salir')
        opcion = int(input(f'Ingrese la opción (1-5): '))

        if opcion == 1:
            usuarios = OficinaDAO.seleccionar()
            for usuario in usuarios:
                print(usuario)

        elif opcion == 2:
            nuevo_nit = input(f'Ingrese el NIT del usuario: ')
            nuevo_nombres = input(f'Ingrese los nombres del usuario: ')
            nuevo_apellidos = input(f'Ingrese los apellidos del usuario: ')
            nuevo_fecha = input(f'Ingrese la fecha de nacimiento: ')
            nuevo_dpi = input(f'Ingrese el DPI del usuario: ')
            nuevo_imagen = input(f'Ingrese la imagen del usuario: ')
            nuevo_telefono = input(f'Ingrese el telefono del usuario: ')
            nueva_direccion = input(f'Ingrese la direccion del usuario: ')
            usuario0 = Oficina(NIT=nuevo_nit, Nombres=nuevo_nombres, Apellidos=nuevo_apellidos,
                               Fecha_Nacimiento=nuevo_fecha, DPI=nuevo_dpi, Telefono=nuevo_telefono, Direccion= nueva_direccion, Imagen=nuevo_imagen)
            usuarios_insertados = OficinaDAO.insertar(usuario0)
            print(f'Usuarios insertados: {usuarios_insertados}')

        elif opcion == 3:
            nit_nuevo = input(f'Ingrese el NIT del usuario que desea modifiacar: ')
            nombres_nuevo = input(f'Ingrese los nuevos nombres del usuario: ')
            apellido_nuevo = input(f'Ingrese los nuevos apellidos del usuario: ')
            fecha_nuevo = input(f'Ingrese la fecha de nacimiento: ')
            dpi_nuevo = input(f'Ingrese el dpi del usuario: ')
            imagen_nuevo = input(f'Ingrese la imagen del usuario: ')
            nuevo_telefono = input(f'Ingrese el telefono del usuario: ')
            nueva_direccion = input(f'Ingrese la direccion del usuario: ')
            usuario1 = Oficina(nit_nuevo, nombres_nuevo, apellido_nuevo, fecha_nuevo, dpi_nuevo, nueva_direccion, nuevo_telefono,imagen_nuevo)
            usuarios_actualizados = OficinaDAO.actualizar(usuario1)
            if usuarios_actualizados >= 1:
                print(f'Usuarios actualizados: {usuarios_actualizados}')
            else:
                print('Usuario no encontrado')

        elif opcion == 4:
            nit_nuevo = input(f'Ingrese el id del usuario que desea eliminar ')
            usuario2 = Oficina(NIT=nit_nuevo)
            usuario_eliminado = OficinaDAO.eliminar(usuario2)
            print(f'Usuarios eliminados: {usuario_eliminado}')

        elif opcion == 5:
            print(f'Terminaron consultas CRUD')

        else:
            print(f'Ingrese una opción valida')
