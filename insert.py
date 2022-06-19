import subprocess


def cmd(comando):
    resultado = subprocess.run(comando, shell=True)

cmd('pg_dump -U postgres -F c test_oficina > test_oficina1005')
