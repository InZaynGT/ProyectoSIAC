from main import log
from psycopg2 import pool
import sys


class Conexion:
    _DATABSE = 'test_oficina'
    _USERNAME = 'postgres'
    _PASSWORD = 'admin'
    _DB_PORT = '5432'
    _HOST = '127.0.0.1'
    _MIN_CON = 1
    _MAX_CON = 10
    _pool = None

    @classmethod
    def ObtenerPool(cls):
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(cls._MIN_CON, cls._MAX_CON,
                                                      host=cls._HOST,
                                                      user=cls._USERNAME,
                                                      password=cls._PASSWORD,
                                                      port=cls._DB_PORT,
                                                      database=cls._DATABSE)
                return cls._pool
            except Exception as e:
                log.error(f'Ocurrió un error al obtener el pool de tipo: {e}')
                sys.exit()
        else:
            return cls._pool

    @classmethod
    def ObtenerConexion(cls):
        conexion = cls.ObtenerPool().getconn()
        return conexion

    @classmethod
    def LiberarCOnexion(cls, conexion):
        cls.ObtenerPool().putconn(conexion)

    @classmethod
    def CerrarConexiones(cls):
        cls.ObtenerPool().closeall()


if __name__ == '__main__':
    conexion1 = Conexion.ObtenerConexion()
