from datetime import datetime
from datetime import time

class Empresa:

    def __init__(self, nom_empresa = None, desc_empresa = None, NIT = None):
        self._nom_empresa = nom_empresa
        self._desc_empresa = desc_empresa
        self._NIT = NIT

    def __str__(self):
        return f'''
        Nombre de empresa = {self._nom_empresa}
        Descripcion = {self._desc_empresa}
        NIT = {self._NIT}
        '''


    @property
    def nom_empresa(self):
        return self._nom_empresa

    @nom_empresa.setter
    def nom_empresa(self,nom_empresa):
        self._nom_empresa = nom_empresa

    @property
    def descripcion(self):
        return self._desc_empresa

    @descripcion.setter
    def descripcion(self, desc_empresa):
        self._desc_empresa = desc_empresa

    @property
    def NIT(self):
        return self._NIT

    @NIT.setter
    def NIT(self, NIT):
        self._NIT = NIT

if __name__ == '__main__':
    empresa1 = Empresa('SYS', 'Tecnologias de la Informacion', '1234324')

    print(empresa1)
    print(datetime.now())

class casa123:
    pass