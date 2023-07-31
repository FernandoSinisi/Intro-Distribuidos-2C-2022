# TP1-Introducción-a-sistemas-distribuidos

## Grupo 3:

| Integrante           | Padrón | Correo              | 
|----------------------|--------|---------------------| 
| Agustín Pérez Leiras | 100972 | aperezl@fi.uba.ar   |    
| Fernando Sinisi      | 99139  | fsinisi@fi.uba.ar   |
| Juan Ignacio Díaz    | 103488 | jidiaz@fi.uba.ar    | 
| Lucas Veron          | 89341  | lveron@fi.uba.ar    | 
| Pablo Inoriza        | 94986  | pinoriza@fi.uba.ar  | 

## Ejecutar Servidor

```
$./start-server
usage: start-server [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH] [-P PROTOCOL]

FTP over UDP server

options:
  -h, --help        show this help message and exit
  -v, -verbose      increase output verbosity
  -q, -quiet        decrease output verbosity
  -H , --host       service IP address
  -p , --port       service port
  -s , --storage    storage dir path
  -P , --protocol   rdt protocol to use

```
#### Referencia
--protocol debe ser: udp-saw|udp-gbn

Las rutas son relativas a donde se ejecuta el servidor

## Ejecutar Cliente

```
$./upload
usage: upload [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

FTP over UDP upload client

options:
  -h, --help    show this help message and exit
  -v, -verbose  increase output verbosity
  -q, -quiet    decrease output verbosity
  -H , --host   server IP address
  -p , --port   server port
  -s , --src    source file path
  -n , --name   file name

```
#### Referencia
Las rutas son relativas a donde se ejecuta el cliente
```
$./download -h
usage: download [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME]

FTP over UDP download client

options:
  -h, --help    show this help message and exit
  -v, -verbose  increase output verbosity
  -q, -quiet    decrease output verbosity
  -H , --host   server IP address
  -p , --port   server port
  -d , --dst    destination file path
  -n , --name   file name
```
#### Referencia
Las rutas son relativas a donde se ejecuta el cliente

## Ejecutar comcast de la siguiente forma
```
./comcast --device=lo --packet-loss=10% --target-addr=127.0.0.0/8 --target-proto=udp --target-port=1024:65535
```
```
