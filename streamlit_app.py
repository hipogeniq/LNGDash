# imports for needed packages
import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
from tabulate import tabulate
from datetime import datetime
import os

st.set_page_config(
    page_title="LNG Dashboard",
    page_icon="✅",
    layout="wide",
)

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'blue' if val > 90 else 'black'
    return 'color: % s' % color

# initializare datarames din fisiere
df_ccd = pd.read_excel('C:/Personal/Lingemann/LNG/input/Comenzi clienti deschise - lucru.xlsx')
df_cfd = pd.read_excel('C:/Personal/Lingemann/LNG/input/Comenzi furnizori deschise - lucru.xlsx',skiprows=1)
df_ccf = pd.read_excel('C:\Personal\Lingemann\LNG\input\Confirmari comenzi furnizori.xlsx', skiprows=1, skipfooter=1)
df_stock = pd.read_excel('C:\Personal\Lingemann\LNG\input\Stock value_RO.xlsx', skiprows=1, skipfooter=1)
df_stocmin = pd.read_excel('C:\Personal\Lingemann\LNG\input\Stocuri minime dep. principale.xlsx', skiprows=1, skipfooter=1)
print(os.listdir())
st.title("LNG Dashboard")

#st.header("Comenzi clienti deschise")

# displaying the DataFrame
#df_ccd.style.applymap(color_negative_red)
#st.dataframe(df_ccd)
#print(tabulate(df_ccd, headers = 'keys', tablefmt = 'pretty'))


#st.header("Comenzi clienti deschise - prelucrat")
df_ccdModified = df_ccd.copy()
#df_ccdModified['NumeF'] = ''

#pune in coloana Nume F numele furnizorului din Label din df_ccd
# df_ccdModified.merge(df_ccd, on='Cod client', how='left')
#df_ccdModified.set_index('Cod client', append=True).join(df_ccd.set_index('Cod client', append=True)['Label'], lsuffix='_left', rsuffix='_right').reset_index('Cod client')
df_ccdModified.loc[(df_ccdModified['Nr. intern comanda client (text)'].isnull()) & (df_ccdModified['Numar pozitie'].isnull()) & df_ccdModified['Lieferartikel'].isnull(), 'NumeF'] = df_ccdModified['Label']
cc = df_ccdModified['Cod client'].iloc[0]
numef = df_ccdModified['NumeF'].iloc[0]
for index in range(len(df_ccdModified)): 
    if (df_ccdModified['Cod client'].iloc[index]==cc):
        df_ccdModified['NumeF'].iloc[index] = numef
    else:
        numef = df_ccdModified['NumeF'].iloc[index]
        cc = df_ccdModified['Cod client'].iloc[index]
#df_ccdModified.reset_index(inplace=True)
#st.dataframe(df_ccdModified)

#st.header("Comenzi clienti deschise - doar ce trebe")
#elimin liniile cu 'Lieferartikel' <NA>
df_ccdModified = df_ccdModified.dropna(subset=['Lieferartikel'])
#f_ccdModified.reset_index(inplace=True)
#st.dataframe(df_ccdModified)

#st.header("Comenzi furnizori deschise")
df_cfdModified = df_cfd.copy()
df_cfdModified = df_cfdModified.dropna(subset=['Lieferartikel'])
#df_cfdModified.reset_index(inplace=True)
#st.dataframe(df_cfdModified)


#st.header("Confirmari comenzi furnizori")
#remove first line that contains a title
#df_ccf.drop(df_ccf.index[:1])
#remove last line that contains a total
#df_ccf.drop(df_ccf.index[-1:])
df_ccfModified = df_ccf.copy()
#elimina rows cu Numar pozitie necompletat
df_ccfModified = df_ccfModified.dropna(subset=['Numar pozitie'])
#df_ccfModified.reset_index(inplace=True)
#st.dataframe(df_ccfModified)

#st.header("Valori stocuri")
#remove first line that contains a title
#df_stock.drop(df_stock.index[:1])
#remove last line that contains a total
#df_stock.drop(df_stock.index[-1:])
df_stockModified = df_stock.copy()
#elimina rows cu Cod produs necompletat
df_stockModified = df_stockModified.dropna(subset=['Artikelnummer'])
#df_stockModified.reset_index(inplace=True)
#st.dataframe(df_stockModified)

#st.header("Stocuri minime")
#remove first line that contains a title
#df_stocmin.drop(df_stocmin.index[:1])
#remove last line that contains a total
#df_stocmin.drop(df_stocmin.index[-1:])
df_stocminModified = df_stocmin.copy()
#elimina rows cu Cod produs necompletat
df_stocminModified = df_stocminModified.dropna(subset=['Cod produs'])
#df_stocminModified.reset_index(inplace=True)
#st.dataframe(df_stocminModified)

st.header("Stoc actual")
#df_stockModified.loc[:, df_stockModified.columns != '']
df_StocActual=df_stockModified.copy()
#st.dataframe(df_StocActual)
#df_StocActual.reset_index(inplace=True)
df_StocActual.columns = ['Depozit' ,'Cod produs', 'Descriere' ,	'UM', 'Stoc fizic',	'Stoc disponibil', 'Cant. Rezervata', 'Cantitate in Comenzi clienti', 'Cantitate in Comenzi furnizori', 'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica', 'Categ. Pret vanzare', 'Categorie pret / descriere', 'Pret lista', 'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse']
df_StocActual['Legatura'] = ''
df_StocActual['Legatura'] = df_StocActual['Depozit'].map(str)+df_StocActual['Cod produs'].map(str)
st.dataframe(df_StocActual)


st.header("Stocuri minime")
df_StocuriMinime = df_stocminModified.copy()
df_StocuriMinime.columns = ['Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal']
df_StocuriMinime['Legatura'] = ''
df_StocuriMinime['Legatura'] = df_StocuriMinime['Depozit'].map(str)+df_StocuriMinime['Cod produs'].map(str)
today = datetime.now().date()
luna_curenta = datetime.now().month
year_start = datetime(datetime.now().year, 1,1).date()
df_StocuriMinime['Medie zilnica an curent'] = round(df_StocuriMinime['Cantitate an curent']/(today-year_start).days,4)
df_StocuriMinime['Medie lunara an curent'] = round(df_StocuriMinime['Cantitate an curent']/luna_curenta,4)
df_StocuriMinime['Medie lunara an precedent'] = round(df_StocuriMinime['Cantitate an precedent']/12,4)
st.dataframe(df_StocuriMinime)


st.header("Comenzi clienti ordonate dupa data de livrare O2N")
df_cco = df_ccdModified.copy()
df_cco.columns = ['Grupa client', 'Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact', 'NumeF']
df_cco.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_cco['Legatura'] = ''
df_cco['Legatura'] = df_cco['Depozit'].map(str)+df_cco['Lieferartikel'].map(str)+" "
df_cco['Data livrare'] = pd.to_datetime(df_cco['Data livrare'])
df_cco.sort_values(by='Data livrare', inplace=True)
st.dataframe(df_cco)

st.header("Comenzi Clienti - cantitati restante")
pivot_cc = df_cco.pivot_table(index =['Legatura'], values =['Cantitate restanta'], aggfunc ='sum')
pivot_cc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
pivot_cc.loc["GRAND TOTAL"] = pivot_cc['Cantitate restanta'].sum()
st.dataframe(pivot_cc)

st.header("Confirmari Comenzi Furnizori")
df_ccf2 = df_ccfModified.copy()
df_ccf2['Legatura CF'] = ''
df_ccf2['Legatura CF'] = df_ccf2['Numar intern comanda client'].map(str)+df_ccf2['Numar pozitie'].map(str)
st.dataframe(df_ccf2)

st.header("Comenzi Furnizori ordonate dupa data de inregistrare O2N")
df_cfo = df_cfdModified.copy()
df_cfo.drop(['Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Label'], axis=1, inplace=True)
df_cfo['Legatura'] = ''
df_cfo['Legatura'] = df_cfo['Numar intern comanda client.1'].map(str)+df_cfo['Numar pozitie.1'].map(str)+df_cfo['Lieferartikel'].map(str)
st.dataframe(df_cfo)


st.header("Status comenzi furnizori intarziat")
df_cfi = df_cfo.copy()
df_cfi.drop(['Cod client.1', 'Abgangs-Datum', 'Tip comanda furnizor', 'Pret manual', 'Cod curs valutar', 'Stoc disponibil', 'Confirmare rezervare', 'Confirmare comanda furnizor', 'Valoare comenda  furnizor', 'Data livrare - dorita'], axis=1, inplace=True)
df_cfi['Legatura depozit'] = ''
df_cfi['Legatura depozit'] = df_cfi['Depozit'].map(str)+df_cfi['Lieferartikel'].map(str)
df_cfi['Zi referinta'] = pd.to_datetime(today)
df_cfi['KW data referinta'] = today.isocalendar().week
df_cfi['An referinta'] = datetime.now().year
df_cfi['KW data livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.isocalendar().week)
df_cfi['An livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.year)
df_cfi['Zile intarziere'] = (df_cfi['Zi referinta']-df_cfi['Data livrare']).apply(lambda x: x.days)
# join cu df_cco pt Data livrare('Cel mai vechi termen de livrare catre client') si NumeF('Client') dupa Legatura (CC) cu Legatura Depozit 


# join cu df_stocuriMinime pt Stoc minim('Stoc Minim') dupa Legatura (SM) cu Legatura Depozit  


st.dataframe(df_cfi)
