from main import log
from Conexion import Conexion


class CursorDelPool():
    def __init__(self):
        self._conexion = None
        self._cursor = None

    def __enter__(self):
        self._conexion = Conexion.ObtenerConexion()
        self._cursor = self._conexion.cursor()
        return self._cursor

    def __exit__(self, tipo_except, valor_except, detalle_except):
        if valor_except:
            self._conexion.rollback()
            log.error(f'Ocurrió una excepción, se hizo rollback {valor_except} {tipo_except} {detalle_except}')
        else:
            self._conexion.commit()
        self._cursor.close()
        Conexion.LiberarCOnexion(self._conexion)


if __name__ == '__main__':
    with CursorDelPool() as cursor:
        cursor.execute('SELECT * from oficina3')
        log.debug(cursor.fetchall())
