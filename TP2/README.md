# tp2-intro-distribuidos

## Grupo 3:

| Integrante           | Padrón | Correo              | 
|----------------------|--------|---------------------| 
| Agustín Pérez Leiras | 100972 | aperezl@fi.uba.ar   |    
| Fernando Sinisi      | 99139  | fsinisi@fi.uba.ar   |
| Juan Ignacio Díaz    | 103488 | jidiaz@fi.uba.ar    | 
| Lucas Veron          | 89341  | lveron@fi.uba.ar    | 
| Pablo Inoriza        | 94986  | pinoriza@fi.uba.ar  | 

## POX Controller

Poner el archivo `firewall.py` en `pox/ext`:

```sh
ln -f firewall.py /ruta/a/pox/ext
```

Si no se está utilizando la _development branch_ de pox (i.e: `halosaur`) o una más nueva:

Poner el archivo `dns.py` en `pox/pox/lib/packet` reemplazando el existente - soluciona problema python2/3

```sh
cp -f dns.py /ruta/a/pox/pox/lib/packet
```

Ubicarse en directorio que contenga `rules.toml` o pasar el argumento `--config` con la ruta a las reglas.
Correr controller con:

```sh
/ruta/a/pox.py firewall --switch=<nombre switch firewall> --config=/ruta/a/rules.toml
```

## Mininet

Levantar mininet con:

```sh
sudo mn --custom topo.py --topo topoTP,<cantidad switches> --arp --mac --switch ovsk --controller remote
```

## iperf

Para probar el funcionamiento de las reglas, lo más cómodo es levantar terminales xterm para cada host que se vaya a usar
`mininet> xterm h1 h2 h3 h4`

Luego en la terminal de cada host, se puede levantar un server TCP/UDP (flag -u) con:
`iperf -s -p <port> [-u]`

Y para un cliente TCP/UDP (flag -u):
`iperf -c <server_ip> -p <server_port> [-u]`
