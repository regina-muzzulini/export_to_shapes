import numpy as np

from lxml import etree
from vincenty import vincenty

import geopy
import geopy.distance

import os.path as path

import shapefile as shp
import sys

def main():
    # Archivo donde están todos los puntos georreferenciados de la linea original

    #file = str(input("Ingrese el nombre del archivo .gps que contiene las coordenadas: ")) 
    file = 'data_input/009_N193_1'
    fileCoordenada = file + '.csv'
    if not(path.exists(fileCoordenada)):
        print("El nombre del archivo ingresado es incorrecto")
        sys.exit()
        
    data = np.loadtxt(fileCoordenada, delimiter=",", usecols=range(23))
    latitud = np.unique(data[:, 2])
    longitud = np.unique(data[:, 3])
    cantPtos = len(latitud)

    coordOriginal = ""
    ahueLeft_x = []
    ahueLeft_y = []
    ahueLeft_e = []
    ahueRight_x = []
    ahueRight_y = []
    ahueRight_e = []

    for i in range(0, cantPtos):
        coordOriginal = coordOriginal + str(longitud[i]) + "," + str(latitud[i]) + ",0 "
        pto = (latitud[i], longitud[i])
        
        # Define a general distance object, initialized with a distance of 1 m.
        d = geopy.distance.geodesic(meters = 1)
        
        # Vamos a calcular 1m para la derecha para la huella derecha
        # Use the 'destination' method with a bearing of 0 degrees (which is north)
        # in order to go from point 'start' 1 km to north.
        ptoLeft = d.destination(point=pto, bearing=90)    
        ptoRight = d.destination(point=pto, bearing=0)    

        indLcm = str(i).rjust(6, '0')
        file = 'data_input/LcmsResult_' + str(indLcm) + '.xml'
        
        if not(path.exists(file)):
            break
        
        doc = etree.parse(file)
        
        # Ejemplo: <p>To find out <em>more</em>, see the <a href="http://www.w3.org/XML">standard</a>.</p>
        # .tag => nombre de la etiqueta => p 
        # .text => texto guardado dentro de la etiqueta => To find out
        # .tail => texto de un elemento, que está a continuación de otro elemento
        # .attrib => diccionario python que contiene los nombres y valores de los atributos del elemento
        
        #################################
        # Arrancamos con el ahuellamiento
        laneSide=doc.findall("RutInformation/RutMeasurement/LaneSide") 
        cantLaneSide = len(laneSide)
        
        depth=doc.findall("RutInformation/RutMeasurement/Depth")  # Abrimos el archivo .gps con las coordenadas y buscamos el puntito
        
        for i in range(0, cantLaneSide):
            if laneSide[i].text=="Left":
                ahueLeft_x.append(ptoLeft[1]) 
                ahueLeft_y.append(ptoLeft[0])
                ahueLeft_e.append(depth[i].text)
            else:
                ahueRight_x.append(ptoRight[1])
                ahueRight_y.append(ptoRight[0])
                ahueRight_e.append(depth[i].text)


    # Preparamos el archivo shp para escribir
    logic = [True,False,True]


    # AHUELLAMIENTO IZQUIERDO Y DERECHO
    w = shp.Writer(str(shp.POINT))
    w.autoBalance = 1       #ensures gemoetry and attributes match
    w.field('depth', 'F', 10, 5)

    for j, k in enumerate(ahueLeft_x):
        w.point(k, ahueLeft_y[j])       #write the geometry
        w.record(ahueLeft_e[j])
    
    for j, k in enumerate(ahueRight_x):
        w.point(k, ahueRight_y[j])      #write the geometry    
        w.record(ahueRight_e[j])

    #w.close()
    #w.Save('ooo.shp')    



    # Creamos el archivo shape
    out_file = '1'

    # creando el archivo prj.
    prj = open(out_file +'.prj', 'w')
    proyeccion      ='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
    prj.write(proyeccion)


if __name__ == '__main__':
    main()