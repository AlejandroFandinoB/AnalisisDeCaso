# -*- coding: utf-8 -*-
"""
Created on Sun May 10 15:29:53 2020

@author: Sebastian Cruz
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

#Leyendo la data desde la carpeta origen 

os.chdir(r'C:\Users\Sebastian Cruz\Desktop\Especializacion\Proyecto Analisis de Caso')
os.listdir()

#Abriendo las bases de dats 
emb=pd.read_csv('variables_adicionales_hogar_v3.txt', sep = ";")

viv=pd.read_table('viviendas_2017_v2_03092018.txt', sep = ",",
                  encoding='latin1')

per = pd.read_table('variables_adicionales_personas_v2.txt', sep = ",")

personas = pd.read_table('Personas_2017_V2_03092018.txt', sep = ",",
                  encoding='latin1')


#Evaluando duplicados y removiendolos 
emb['DIRECTORIO_HOG'].duplicated().value_counts()
viv['DIRECTORIO'].duplicated().value_counts()
per['directorio_per'].duplicated().value_counts()
personas['DIRECTORIO_PER'].duplicated().value_counts()
#No hay hogares duplicados, ni directorios ni personas repetidas en estas tres bases de datos


#Filtrando las bases de datos  con las variables deseadas, segun nuestras hipotesis preliminares
viv_1=viv[['DIRECTORIO', 'DPTOMPIO','LOCALIDAD_TEX', 'CLASE',
               'COD_UPZ', 'ESTRATO_TEX','ESTRATO', 'FEX_P','NVCBP10', 'NVCBP11A', 'NVCBP11AA', 'NVCBP11C','NVCBP14B', 'NVCBP14E', 'NVCBP14G','NVCBP14I']]

personas_db = personas[['DIRECTORIO', 'DIRECTORIO_HOG','DIRECTORIO_PER', 'NPCEP4',
               'NPCEP5']]

#Peganda bases de vivienda con variables deseadas y base de datos hogares
emb_1= emb.merge(viv_1, on = 'DIRECTORIO', how='inner')
#Constantando que no hayan hogares repetidos con esta manera de pegar los datos. 
emb_1['DIRECTORIO_HOG'].duplicated().value_counts()
#Finalmente se observa que de los 109111 registros ninguno quedo con hogar repetido. 

#Filtrar solo Bogota, con las siguientes caracteristicas DPTOMPIO == 11001 (Bogota), y CLASE == 1 (Urbana) 
condicion_bog_urb = emb_1.DPTOMPIO.isin([11001]) & emb_1.CLASE.isin([1])
db_bog_urb =emb_1.loc[condicion_bog_urb,]
db_bog_urb.DPTOMPIO.value_counts()
db_bog_urb['DPTOMPIO'].duplicated().value_counts()
#Una vez filtrada la data, se comprueba que solamente estemos trabajando con datos de Bogota Urbana segun las caracteristicas anteriormente mencionadas. 


#Filtrando por los estratos de interes 4,5 y 6 (Estratos medios-atos de Bogota)
condicion_estratos = db_bog_urb.ESTRATO_VIV.isin([4,5,6])
db_bog_estratos = db_bog_urb.loc[condicion_estratos,]

#Calculando el ingreso por estrato - sin tener en cuenta los factores de expansion 
Ingresos_estratos =db_bog_estratos.groupby('ESTRATO_VIV', as_index = False).agg({'INGRESOS_HOG':'mean'})

##Calculando el ingreso por estrato - teniendo en cuenta los factores de expansion 
#definicion Formula 
def total_est(df, y_i, w_i):
    d=df[y_i]
    w=df[w_i]
    return(sum(d*w)/sum(w))

#Calculando con expansion 
db_bog_estratos.groupby('ESTRATO_VIV',as_index = False).apply(total_est, 'INGRESOS_HOG', 'FEX_C') 

#Creando una base de datos para comparar ambos ingresos
Ingresos_estratos['INGRESOS_HOG_EXP'] =[7.161870e+06,9.676284e+06,1.230490e+07]

#Grafico de los ingresos
plt.barh(range(3), Ingresos_estratos['INGRESOS_HOG'], edgecolor='black')
plt.yticks(range(3), Ingresos_estratos['ESTRATO_VIV'], rotation=0)
plt.title("Ingresos por Estrato - Sin Expansion")
plt.show()

plt.barh(range(3), Ingresos_estratos['INGRESOS_HOG_EXP'], edgecolor='black')
plt.yticks(range(3), Ingresos_estratos['ESTRATO_VIV'], rotation=0)
plt.title("Ingresos por Estrato - Con Expansion")
plt.show()


# A continuacion, se realizaran unos estadisticos basicos a las variables Ingresos e Ingresos per Capita

db_bog_estratos['INGRESOS_HOG'].describe().round(1)
db_bog_estratos['INGRESOS_PER_CAPITA'].describe().round(1)
#Boxplot de los ingresos 
fig1, ax1 = plt.subplots()
ax1.set_title('Distribucion de Ingresos en Bogota')
ax1.boxplot(db_bog_estratos['INGRESOS_HOG'])

fig1, ax1 = plt.subplots()
ax1.set_title('Distribucion de Ingresos per Capita en Bogota')
ax1.boxplot(db_bog_estratos['INGRESOS_PER_CAPITA'])
#FALTA ANALISIS DE LOS ESTADISTICOS BASICOS

_____________________________________________________________________________
#Trayendo tabla con las localidades de Bogota
#EJEMPLO WIKIPEDIA - TABLA
from bs4 import BeautifulSoup
import requests 
import pandas as pd
#Llamo la URL   que quiero visualizar 
URL = "https://es.wikipedia.org/wiki/Anexo:Localidades_de_Bogot%C3%A1"
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')
#idntifico todo el codigo html 
print(soup)

#busco la tabla especifica que quiero traer
table = soup.find('table',{'class':'sortable wikitable'})
print(table)

#selecciono todas las filas, que se identifican como tr en el codigo
rows = table.find_all('tr')
#las columnas se identifican como th
columns = [v.text.replace('\n','') for v in rows[0].find_all('th')]
print(columns)
#Creando el data frame con las columnas que traje 
bogota_localidades_wiki = pd.DataFrame(columns = columns)

for i in range(1, len(rows)):
    tds = rows[i].find_all('td')
        
    if len(tds)  == 4:
        values = [tds[0].text, tds[1].text, '', tds[2].text, tds[3].text.replace('\n','').replace('\xa0','')]
    else: 
        values = [td.text.replace('\n','').replace('\xa0','') for td in tds]
    
    bogota_localidades_wiki = bogota_localidades_wiki.append(pd.Series(values, index=columns), ignore_index=True)
    print(bogota_localidades_wiki)

_____________________________________________________________________________
#POBREZA OCULTA 

#Con estos estadisticos basicos, se pudo observar que el valor minimo era de 0, asi que se decide filtrar por este valor.
db_bog_estratos_sin_ingreso =db_bog_estratos.query('INGRESOS_HOG == 0')
db_bog_estratos_LP =db_bog_estratos.query('HOGAR_LP == 1')

db_bog_estratos_LP['INGRESOS_HOG'].describe().round(1)
db_bog_estratos_LP['INGRESOS_PER_CAPITA'].describe().round(1)


# Hogares por estratos totales 
hogares_estrato = db_bog_estratos.groupby(['LOCALIDAD_TEX'], as_index = False).agg({'DIRECTORIO_HOG':'count'})
hogares_estrato_selec = db_bog_estratos_LP.groupby(['LOCALIDAD_TEX'], as_index = False).agg({'DIRECTORIO_HOG':'count'})

#Creando la proporcion de Hogares en Linea de Pobreza vs el Total de Hogares 
hogares_prop = hogares_estrato.merge(hogares_estrato_selec, on = 'LOCALIDAD_TEX')
hogares_prop['PROP_HOG_LP'] = hogares_prop['DIRECTORIO_HOG_y']/hogares_prop['DIRECTORIO_HOG_x']

#Hogares por estrato 
hogares_gru_int = db_bog_estratos_LP.groupby(['ESTRATO_VIV'], as_index = False).agg({'DIRECTORIO_HOG':'count'})
#Pie chart - Division estratos
labels = '4', '5', '6'
fig1, ax1 = plt.subplots()
ax1.pie(hogares_gru_int['DIRECTORIO_HOG'],  labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')# Equal aspect ratio ensures that pie is drawn as a circle.
ax1.set_title('Distribucion Hogares en Linea de Pobreza por Estrato')
plt.show()

#Contando los hogares con el factor de expansion 
a = sum(db_bog_estratos_LP.FEX_C)
b = sum(db_bog_estratos.FEX_C)
a/b
#Se revisan los hogares para ver en que tipo de vivienda estan estas personas 
#Hogares en Linea de Pobreza, agrupados por UPZ, tipo de vivienda y Estrato
tipo_hogar_upz=db_bog_estratos_LP.groupby(['NVCBP10', 'COD_UPZ','ESTRATO_VIV'], as_index = False).agg({'DIRECTORIO_HOG':'count'})
table = pd.pivot_table(tipo_hogar_upz, values='DIRECTORIO_HOG', index=['NVCBP10'],
                    columns=['ESTRATO_VIV'], aggfunc=np.sum)
table['TIPO_VIV'] = ['Casa','Apartamento','Cuarto(s)']

#Graficando su distribucion por tipo de vivienda (Pie chart)
labels = 'Casa', 'Apto', 'Cuarto'
sizes = [60,573,9]
explode = (0, 0.1, 0.1) 
fig1, ax1 = plt.subplots()
ax1.pie(sizes,explode=explode,  labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')# Equal aspect ratio ensures that pie is drawn as a circle.
ax1.set_title('Distribucion por Tipo de Vivienda - Hogares en Linea de Pobreza')
plt.show()

#Graficando su distribucion por tipo de vivienda y estrato (Stacked chart)
labels = ['4','5','6']
Casa = [52,6,2]
Apartamento = [436,79,58]
Cuarto =[8,0,1]
width = 0.7      # the width of the bars: can also be len(x) sequence

fig, ax = plt.subplots()

ax.bar(labels, Casa, width, label='Casa')
ax.bar(labels, Apartamento, width, bottom=Casa,
       label='Apartamento')
ax.bar(labels, Cuarto, width, bottom=Casa,
       label='Cuarto(s)')

ax.set_ylabel('# de Hogares')
ax.set_title('Hogares por Tipo y Estrato en Linea de Pobreza')
ax.legend()
plt.show()

# Distribucion por UPZ 
upz_hog_LP = db_bog_estratos_LP.groupby(['ESTRATO_TEX'], as_index = False).agg({'DIRECTORIO_HOG':'count'})
test = db_bog_estratos_LP.groupby(['ESTRATO_TEX','ESTRATO_VIV'], as_index = False).agg({'DIRECTORIO_HOG':'count'})

upz_hog_sel = db_bog_estratos_LP.groupby(['ESTRATO_TEX'], as_index = False).agg({'TOTAL_PUNTAJE':'mean'})

#Uniendo las bases
hogares_selec = upz_hog_LP.merge(upz_hog_sel, on = 'ESTRATO_TEX')

# Hogares y su puntaje de calidad de vida 
db_bog_estratos_LP.groupby(['ESTRATO_VIV'], as_index = False).agg({'TOTAL_PUNTAJE':'mean'})
#Haciendo el Grafico de esta variable
Puntaje = [96.99, 98.41, 98.60]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x, Puntaje, width)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Calidad de Vida')
ax.set_title('Puntaje Calidad de Vida por Estrato')
ax.set_xticks(x)
ax.set_xticklabels(labels)



def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 0),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


autolabel(rects1)


fig.tight_layout()

plt.show()

#Hogares sin Ingreso 
db_bog_estratos_sin_ingreso.groupby('NVCBP10', as_index = False).agg({'DIRECTORIO_HOG':'count'})

#De este agrupamiento podemos ver que toda las personas viven en casa, apartamento o en su defecto en un cuarto, ninguno habita en Otro tipo de vivienda (carpa, tienda, vagón, embarcación, refugio natural, etc.).
#Luego de realizar estos filtros vemos que estas dos bases de datos pueden llegar a portar conclusiones interesantes y seran apartir de este momento objeto de estudio.

#Pegando la data de personas a la base filtrada de interes para conocer informacion de edad y miembros de los hogares
estratos_LP_personas= db_bog_estratos_LP.merge(personas_db, on = 'DIRECTORIO', how='left')

#Box plot y describe de la edad 
estratos_LP_personas['NPCEP4'].describe().round(1)

fig1, ax1 = plt.subplots()
ax1.set_xlabel('Edad')
ax1.set_title('Distribucion de Edad en los Hogares con Pobreza Oculta')
ax1.boxplot(estratos_LP_personas['NPCEP4'])


#Viendo como es la edad por estrato 
#Distribucion de la Edad por estrato
edad_estratos = estratos_LP_personas.groupby(['ESTRATO_VIV'], as_index = False).agg({'NPCEP4':'mean'})

#Evaluando el numero de miembros de los hogares seleccionados
miembros_hog=estratos_LP_personas.groupby(['DIRECTORIO_HOG_y','ESTRATO_VIV'], as_index = False).agg({'DIRECTORIO_PER_y':'count'})
#Distribucion por estratos
miembros_hog['DIRECTORIO_PER_y'].describe().round(1)
miembros_hog_estratos=miembros_hog.groupby(['ESTRATO_VIV'], as_index = False).agg({'DIRECTORIO_PER_y':'mean'})
#Graficando el # de miembros
plt.barh(range(3), miembros_hog_estratos['DIRECTORIO_PER_y'], edgecolor='black')
plt.yticks(range(3), miembros_hog_estratos['ESTRATO_VIV'], rotation=0)
plt.title("Numero de Miembros por Hogar y Estrato")
plt.show()

#HASTA AQUI EL SCRIPT ---- HASTA AQUI -------- HASTA AQUI --------- HASTA AQUI ---------------

_________________________________________________________________________________________________________
#Proporcion de hogares en LP vs el total por estrato. 
_______________________________________________________________________________________
#Sacando los ingresos iguales a 0
db_bog_estratos_con_ingreso =db_bog_estratos.query('INGRESOS_HOG > 1500000')

#Filtrando bases por estrato
db_bog_estrato_4 =db_bog_estratos_con_ingreso.query('ESTRATO_VIV == 4')
db_bog_estrato_5 =db_bog_estratos_con_ingreso.query('ESTRATO_VIV == 5')
db_bog_estrato_6 =db_bog_estratos_con_ingreso.query('ESTRATO_VIV == 6')

#Analizando Estrato 4
db_bog_estrato_4['INGRESOS_HOG'].describe().round(1)
db_bog_estrato_4['INGRESOS_PER_CAPITA'].describe().round(1)

#Analizando Estrato 5
db_bog_estrato_5['INGRESOS_HOG'].describe().round(1)
db_bog_estrato_5['INGRESOS_PER_CAPITA'].describe().round(1)

#Analizando Estrato 6
db_bog_estrato_6['INGRESOS_HOG'].describe().round(1)
db_bog_estrato_6['INGRESOS_PER_CAPITA'].describe().round(1)

___

#Sacando los ingresos Percentil1 estrato 4
db_bog_estratos_con_ingreso_p1 =db_bog_estratos.query('INGRESOS_HOG <  1712500')
db_bog_estratos_con_ingreso_p2 =db_bog_estratos.query('INGRESOS_HOG <  2750000')
db_bog_estratos_con_ingreso_p3 =db_bog_estratos.query('INGRESOS_HOG <  4380555')


#Filtrando bases por estrato 4 percentil 1
db_bog_estrato_4_p1 =db_bog_estratos_con_ingreso_p1.query('ESTRATO_VIV == 4')
db_bog_estrato_4_p2 =db_bog_estratos_con_ingreso_p2.query('ESTRATO_VIV == 4')
db_bog_estrato_4_p3 =db_bog_estratos_con_ingreso_p3.query('ESTRATO_VIV == 4')
_______

___

#Sacando los ingresos Percentil estrato 5
db_bog_estratos_con_ingreso_p1_5 =db_bog_estratos.query('INGRESOS_HOG <  2358736')
db_bog_estratos_con_ingreso_p2_5 =db_bog_estratos.query('INGRESOS_HOG <  3750000')
db_bog_estratos_con_ingreso_p3_5 =db_bog_estratos.query('INGRESOS_HOG <  5800000')


#Filtrando bases por estrato 5 percentil 
db_bog_estrato_5_p1 =db_bog_estratos_con_ingreso_p1.query('ESTRATO_VIV == 5')
db_bog_estrato_5_p2 =db_bog_estratos_con_ingreso_p2.query('ESTRATO_VIV == 5')
db_bog_estrato_5_p3 =db_bog_estratos_con_ingreso_p3.query('ESTRATO_VIV == 5')
_______

#Sacando los ingresos Percentil estrato 6
db_bog_estratos_con_ingreso_p1_6 =db_bog_estratos.query('INGRESOS_HOG <  3000000')
db_bog_estratos_con_ingreso_p2_6 =db_bog_estratos.query('INGRESOS_HOG <  5000000')
db_bog_estratos_con_ingreso_p3_6 =db_bog_estratos.query('INGRESOS_HOG <  8500000')


#Filtrando bases por estrato 5 percentil 
db_bog_estrato_6_p1 =db_bog_estratos_con_ingreso_p1.query('ESTRATO_VIV == 6')
db_bog_estrato_6_p2 =db_bog_estratos_con_ingreso_p2.query('ESTRATO_VIV == 6')
db_bog_estrato_6_p3 =db_bog_estratos_con_ingreso_p3.query('ESTRATO_VIV == 6')
