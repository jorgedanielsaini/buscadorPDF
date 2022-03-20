import requests, bs4, os, time, msvcrt, gspread 
from datetime import datetime


#CREANDO ENLACE Y DANDO CREDENCIALES DE ACCESO A API GOOGLE SHEETS
googleCredencial = gspread.service_account(filename="scrapping-acuerdos-d210589e3544.json")
googleSheets = googleCredencial.open("buscador-acuerdos")

#ENLAZANDO CON CADA HOJA O PESTAÑA DE GOOGLE SHHETS
hoja_uno= googleSheets.get_worksheet(0) #Nuevos enlaces PDF
hoja_dos = googleSheets.get_worksheet(1) #Lista enlaces
hoja_tres = googleSheets.get_worksheet(2) #Lista URL

def copiarEnlaces(hoja, enlace):
	ubicacion = len(hoja.col_values(2)) + 1
	fecha = datetime.now().strftime("%d/%m/%Y")
	hoja.update("A"+str(ubicacion), fecha)
	time.sleep(0.5)
	hoja.update("B"+str(ubicacion), enlace)
	time.sleep(1)

while True: #Bucle infinito para que no se cierre despues de la ejecución de la opción 1
	#DEFINIENTO VARIABLES
	opcion = "0"
	listaNuevosEnlaces = []
	contador = 0
	contadorEnlacesNuevos = 0
	contadorErroneos = 0

#INICIO DEL PROGRAMA - LISTADO DE OPCIONES
	while (opcion != "1") and (opcion != "2"): 
		print("      **********************************")
		print("      ****** BUSCADOR DE ACUERDOS ******")
		print("      **********************************\n")
		print("  1: Agregar nueva URL")
		print("  2: Realizar busqueda de nuevos documentos\n")
		opcion = input("  Ingrese el número de la opción que desee realizar: ")
		if (opcion != "1") and (opcion != "2"): 
			print("\n****** OPCIÓN INCORRECTA, INTENTE DE NUEVO *******")
			time.sleep(2)
			os.system ("cls")

#EJECUCIÓN OPCIÓN 1
	if opcion == "1":
		nuevaURL = input("\nIngrese la nueva URL: ")
		listaURL = hoja_tres.col_values(2)
		if nuevaURL in listaURL:
			print("\n****** La URL ingresada ya existe en el registro ******")
			time.sleep(3)
			os.system ("cls")
			continue
		else:
			try:
				print("Obteniendo estructura de URL...")
				pet = requests.get(nuevaURL)
				sopa = bs4.BeautifulSoup(pet.content, "html.parser")
				print("Obteniendo etiquetas...")
				etiqueta = sopa.select("a")
				print("Buscando y copiando archivos pdf...")
				time.sleep(2)
				for a in etiqueta:
					enlace = a.get("href")
					if ".pdf" in enlace:
						copiarEnlaces(hoja_dos, enlace)
				print("Los enlaces pdf fueron copiados con exito")
				print("Guardando la nueva URL...")
				copiarEnlaces(hoja_tres, nuevaURL)
				print("URL guardada correctamente")
				time.sleep(2)
				os.system ("cls")	
				continue
			except requests.exceptions.MissingSchema:
				os.system ("cls")
				print("   ***ALERTA***\n   La URL '" + nuevaURL +"' no es valida")
				time.sleep(3)
				os.system ("cls")
				continue
			except:
				print("   ***ALERTA***\n   No se ha podido acceder a la URL '" + nuevaURL +"'")
				print("Presione una tecla para continuar...")
				msvcrt.getch()

#EJECUCIÓN OPCIÓN 2
	elif opcion == "2":
		listaEnlacesPdf = hoja_dos.col_values(2)
		listaURL = hoja_tres.col_values(2)
		listaURLAnalizadas = []
		print("INICIANDO BUSQUEDA DE ENLACES...")
		for url in listaURL:
			try:
				contador +=1
				print("\nBuscando en " + url)
				pet = requests.get(url)
				sopa = bs4.BeautifulSoup(pet.content, "html.parser")
				etiqueta = sopa.select("a")
				print("Comparando resultados...")
				for a in etiqueta:
					enlace = a.get("href")
					if ".pdf" in enlace:
						if enlace not in listaEnlacesPdf:
							print("Nuevo resultado!")
							contadorEnlacesNuevos += 1
							copiarEnlaces(hoja_dos, enlace)
							if "https" in enlace:
								listaNuevosEnlaces.append(enlace)
								listaURLAnalizadas.append(url)
							else:
								listaNuevosEnlaces.append(url+enlace)
								listaURLAnalizadas.append(url)
			except:
				print("No se ha podido ingresar a: " + url)
				contadorErroneos +=1
				print("Presione una tecla para continuar...")
				msvcrt.getch()
				continue
	break

#COPIAR ENLECES NUEVOS EN GOOGLE SHEETS
for e in listaNuevosEnlaces:
	copiarEnlaces(hoja_uno, e)
	

for u in listaURLAnalizadas:
	ubicacion= len(hoja_uno.col_values(3)) + 1
	hoja_uno.update("C"+str(ubicacion), u)
	time.sleep(1)

#MOSTRAR RESULTADOS DE ANALISIS
print("\n Busqueda terminada\n\n RESULTADOS:\n **********\n")
print("   * Total urls analizadas: ", contador)
print("   * Total sitios erroneos: ", contadorErroneos)
print("   * Total de nuevos enlaces encontrados: ", contadorEnlacesNuevos)
print("\n\n****** Presione una tecla para cerrar ******")
msvcrt.getch()
