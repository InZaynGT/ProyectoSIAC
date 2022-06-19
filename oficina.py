from main import log


class Oficina:

    def __init__(self, NIT=None, Nombres=None, Apellidos=None, Fecha_Nacimiento=None, DPI=None, Telefono=None,
                 Direccion=None, fecha_dpi=None, Imagen=None, Password = None):
        self._NIT = NIT
        self._nombres = Nombres
        self._apellidos = Apellidos
        self._fecha = Fecha_Nacimiento
        self._DPI = DPI
        self._Imagen = Imagen
        self._Telefono = Telefono
        self._Direccion = Direccion
        self._fecha_dpi = fecha_dpi
        self._password = Password

    def __str__(self):
        return f'''
        NIT = {self._NIT}
        Nombres = {self._nombres}
        Apellidos = {self._apellidos}
        Fecha Nacimiento= {self._fecha}
        DPI = {self._DPI}
        Imagen = {self._Imagen}
        Telefono = {self._Telefono}
        Direccion = {self._Direccion}
        Fecha Vencimiento= {self._fecha_dpi}
        Password = {self._password}
        '''

    @property
    def NIT(self):
        return self._NIT

    @NIT.setter
    def NIT(self, NIT):
        self._NIT = NIT

    @property
    def Nombres(self):
        return self._nombres

    @Nombres.setter
    def nombres(self, nombres):
        self._nombres = nombres

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, apellidos):
        self._apellidos = apellidos

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = fecha

    @property
    def dpi(self):
        return self._DPI

    @dpi.setter
    def dpi(self, dpi):
        self._DPI = dpi

    @property
    def imagen(self):
        return self._Imagen

    @imagen.setter
    def imagen(self, imagen):
        self._Imagen = imagen

    @property
    def Telefono(self):
        return self._Telefono

    @Telefono.setter
    def Telefono(self, telefono):
        self._Telefono = telefono

    @property
    def Direccion(self):
        return self._Direccion

    @Direccion.setter
    def Direccion(self, direccion):
        self._Direccion = direccion

    @property
    def Fecha_dpi(self):
        return self._fecha_dpi

    @Fecha_dpi.setter
    def Fecha_dpi(self, fecha_dpi):
        self._fecha_dpi = fecha_dpi

    @property
    def Password(self):
        return self._password

    @Password.setter
    def Password(self, password):
        self._password = password


if __name__ == '__main__':
    oficina1 = Oficina('1450443-K', 'Carlos Andres', 'Miranda Mendez', '28/02/2022', '3158144381301', '58385781',
                       'Zona 9', '31/10/2030', 'imagen.jpg', '12345')

    print(oficina1)
