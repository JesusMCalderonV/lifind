import os

#Configuraciones de la apicacion, como las cookies, sesiones y base de datos
#1. configuracion de la direción de base de datos
	#Primero obtenemos la ruta absoulta donde estamos trabajando para alojar nuestra base de datos en esa misma
ruta = os.path.abspath(os.getcwd())

#configuramos la clave secreta para darle algo de seguridad a nustro proyecto
secret_key = 'Ah_@.-1|68)(kd¿?djdssgtybhdghey532&28782=ddb/d'