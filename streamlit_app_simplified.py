# imports for needed packages
import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import streamlit as st  # 🎈 data web app development
from datetime import datetime
import os
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="LNG Dashboard",
    page_icon="✅",
    layout="wide",
)



# initializare datarames din fisiere
df_ccd = pd.read_excel('input/Comenzi clienti deschise - lucru.xlsx', skipfooter=1)
df_cfd = pd.read_excel('input/Comenzi furnizori deschise - lucru.xlsx',skiprows=1)
df_ccf = pd.read_excel('input/Confirmari comenzi furnizori.xlsx', skiprows=1)
df_stock = pd.read_excel('input/Stock value_RO.xlsx', skiprows=1)
df_stocmin = pd.read_excel('input/Stocuri minime dep. principale.xlsx', skiprows=1)
df_ka = pd.read_excel('input/Clienti - KA.xlsx')


################### A NEW GRID DISPLAY #######################
def niceGrid(dataset):
    gb = GridOptionsBuilder.from_dataframe(dataset)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=1000) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_default_column(groupable=True)
    gb.configure_grid_options(allowContextMenuWithControlKey=True)
    #gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    gridOptions = gb.build()

    grid_response = AgGrid(
        dataset,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        columns_auto_size_mode=True,
        theme='alpine', #Add theme color to the table
        enable_enterprise_modules=True,
        height=400, 
        width='100%',
        reload_data=False
    )

    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected)
    return df

##############################################################

st.title("LNG Dashboard")

############## Comenzi clienti deschise  df_ccd ###############
#%%=======================================================

df_ccd.loc[(df_ccd['Nr. intern comanda client (text)'].isnull()) & (df_ccd['Numar pozitie'].isnull()) & df_ccd['Lieferartikel'].isnull(), 'NumeF'] = df_ccd['Label']

cc = df_ccd['Cod client'].iloc[0]
numef = df_ccd['NumeF'].iloc[0]
for i, row in df_ccd.iterrows():
    if df_ccd.at[i,'Cod client']==cc:
        df_ccd.at[i,'NumeF']=numef
    else:
        numef=df_ccd.at[i,'NumeF']
        cc=df_ccd.at[i,'Cod client']
#elimin liniile cu 'Lieferartikel' <NA>
df_ccd = df_ccd.dropna(subset=['Lieferartikel'])
#convert first from float to int than to string
df_ccd['Nr. intern comanda client (text)'] = df_ccd['Nr. intern comanda client (text)'].astype(int)
df_ccd['Cod client'] = df_ccd['Cod client'].astype(int)
df_ccd['Numar pozitie'] = df_ccd['Numar pozitie'].astype(int)
# define the dtype conversion of columns 
convert_dict ={'Grupa client':np.str_, 'Cod client':np.str_, 'Nr. intern comanda client (text)':np.str_,
                      'Numar pozitie':np.int8, 'Lieferartikel':np.str_, 'Label': np.str_, 'Tip comanda client':np.str_, 'Depozit':np.str_, 
                    'Validare generare dispozitie livrare':np.str_, 'Validare comanda client':np.str_, 'Cod termen livrare':np.str_,
                      'Data livrare':np.datetime64, 'Cantitate pozitie':np.float32, 'Cantitate livrata':np.float32, 'Cantitate restanta':np.float32,
                      'Valoare restanta':np.float32, 'DB':np.float32, 'DB in %':np.str_, 'User':np.str_, 'Data inregistrare':np.datetime64,
                      'Cod curs valutar':np.str_,'Livrare partiala permisa 1=DA':np.int8, 'Unitate masura':np.str_, 'Cod produs client':np.str_,
                      'Nr. comanda client':np.str_, 'Data comanda client':np.datetime64, 'Nr. comanda furnizor atribuit':np.str_, 
                      'Confirmare comanda furnizor':np.float32, 'Ansprechpartner':np.str_}
df_ccd = df_ccd.astype(convert_dict)

df_ccd = df_ccd[[
 'Grupa client',
 'Cod client',
 'NumeF',
 'Nr. intern comanda client (text)',
 'Numar pozitie',
 'Lieferartikel',
 'Label',
 'Tip comanda client',
 'Depozit',
 'Validare generare dispozitie livrare',
 'Validare comanda client',
 'Cod termen livrare',
 'Data livrare',
 'Cantitate pozitie',
 'Cantitate livrata',
 'Cantitate restanta',
 'Valoare restanta',
 'DB',
 'DB in %',
 'User',
 'Data inregistrare',
 'Cod curs valutar',
 'Livrare partiala permisa 1=DA',
 'Unitate masura',
 'Cod produs client',
 'Nr. comanda client',
 'Data comanda client',
 'Nr. comanda furnizor atribuit',
 'Confirmare comanda furnizor',
 'Ansprechpartner']]
#selectie coloane
df_ccd.columns = ['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']
df_ccd.sort_values(by='Data livrare', inplace=True)
#ordine coloane
df_ccd = df_ccd[['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']]

#%%#############################################################

############## RAPORT SENIOR MANAGEMENT - Comenzi Clienti - cantitati restante  rcc ###############
#%%=======================================================

st.header("RAPORT SENIOR MANAGEMENT - Comenzi Clienti - cantitati restante")
#pivot_cc = df_cco.groupby('Legatura')['Cantitate restanta'].sum()
rcc=df_ccd.groupby(['Depozit','Lieferartikel'])
rcc=rcc.apply(lambda x: x) 
rcc=rcc.loc[:, ['Depozit','Lieferartikel','Cantitate restanta']]
rcc=rcc.groupby(['Depozit','Lieferartikel']).sum()
rcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
rcc.loc['total']= rcc.sum(numeric_only=True)
#st.dataframe(rcc)
rcc.to_excel("output/Raport Comenzi Clienti - Cantitati Restante.xlsx")
#niceGrid(pivot_cc.to_frame())

##############################################################
st.header("Comenzi clienti deschise - df_ccd")
#Ordoneaza comenzi clienti O2N
df_ccd.columns = ['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Cod produs', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']
df_ccd.sort_values(by='Data livrare', inplace=True)
df_ccd = df_ccd[['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Cod produs', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']]
st.write(df_ccd)
#%%#######################################################
############## Comenzi furnizori deschise  df_cfd ###############
#%%=======================================================
st.header("Comenzi furnizori deschise - df_cfd")
df_cfd = df_cfd.dropna(subset=['Lieferartikel'])
df_cfd['Numar intern comanda client'] = df_cfd['Numar intern comanda client'].astype(int)
df_cfd['Numar pozitie'] = df_cfd['Numar pozitie'].astype(int)

convert_dict={
 'Cod client':np.str_,
 'Numar intern comanda client':np.str_,
 'Numar pozitie':np.int8,
 'Label':np.str_,
 'Cod client.1':np.str_,
 'Adresa 1':np.str_,
 'Numar intern comanda client.1':np.str_,
 'Numar pozitie.1':np.int8,
 'Lieferartikel':np.str_,
 'Furnizori / produs':np.str_,
 'Descriere produs':np.str_,
 'Unitate masura':np.str_,
 'Abgangs-Datum':np.datetime64,
 'Tip comanda furnizor':np.str_,
 'Data inregistrare':np.datetime64,
 'Cantitate pozitie':np.float32,
 'Cantitate restanta':np.float32,
 'Pret manual':np.float32,
 'Cod curs valutar':np.str_,
 'Valoare comenda  furnizor':np.float32,
 'Stoc disponibil':np.float32,
 'Confirmare rezervare':np.float32,
 'Confirmare comanda furnizor':np.float32,
 'Depozit':np.str_,
 'Data livrare - dorita':np.datetime64,
 'Data livrare':np.datetime64,
 'Adresa e-mail':np.str_
}

df_cfd = df_cfd.astype(convert_dict)
df_cfd['Numar pozitie'] = df_cfd['Numar pozitie'].astype(int)
df_cfd.drop(['Cod client', 'Numar intern comanda client.1', 'Numar pozitie.1', 'Label'], axis=1, inplace=True)
#selectie coloane
df_cfd.columns = [
 'Numar intern comanda client',
 'Numar pozitie',
 'Cod furnizor',
 'Nume furnizor',
 'Cod produs',
 'Furnizori / produs',
 'Descriere produs',
 'Unitate masura',
 'Abgangs-Datum',
 'Tip comanda furnizor',
 'Data inregistrare',
 'Cantitate pozitie',
 'Cantitate restanta',
 'Pret manual',
 'Cod curs valutar',
 'Valoare comenda  furnizor',
 'Stoc disponibil',
 'Confirmare rezervare',
 'Confirmare comanda furnizor',
 'Depozit',
 'Data livrare dorita',
 'Data livrare',
 'Adresa e-mail']
#ordine coloane
df_cfd.sort_values(by=['Data inregistrare'], inplace=True)
df_cfd=df_cfd[[
 'Cod furnizor',
 'Nume furnizor',
 'Numar intern comanda client',
 'Numar pozitie',
 'Cod produs',
 'Furnizori / produs',
 'Descriere produs',
 'Unitate masura',
 'Abgangs-Datum',
 'Tip comanda furnizor',
 'Data inregistrare',
 'Cantitate pozitie',
 'Cantitate restanta',
 'Pret manual',
 'Cod curs valutar',
 'Valoare comenda  furnizor',
 'Stoc disponibil',
 'Confirmare rezervare',
 'Confirmare comanda furnizor',
 'Depozit',
 'Data livrare dorita',
 'Data livrare',
 'Adresa e-mail']]
st.write(df_cfd)
#%%#############################################################


############## Confirmari Comenzi Furnizori df_ccf ###############
#%%=======================================================
st.header("Confirmari Comenzi Furnizori - df_ccf")
#elimina rows cu Numar pozitie necompletat
df_ccf = df_ccf.dropna(subset=['Numar pozitie'])
#df_ccfModified.reset_index(inplace=True)
#st.dataframe(df_ccfModified)
convert_dict={
 'Numar intern comanda client':np.str_,
 'Numar pozitie':np.float32,
 'Label':np.str_,
 'Nr. confirmare 1':np.str_,
 'Data iesire 1':np.datetime64,
 'Data livrare 1':np.datetime64,
 'Nr. confirmare 2':np.str_,
 'Data iesire 2':np.datetime64,
 'Data livrare 2':np.datetime64,
 'Nr. confirmare 3':np.str_,
 'Data iesire 3':np.datetime64,
 'Data livrare 3':np.datetime64,
 'Nr. poz. cod compus':np.int8
}
df_ccf['Numar intern comanda client'] = df_ccf['Numar intern comanda client'].astype(float).astype(int).astype(str)
df_ccf = df_ccf.astype(convert_dict)
df_ccf['Numar pozitie'] = df_ccf['Numar pozitie'].astype(int)
df_ccf.columns = [ 'Numar intern comanda furnizor', 'Numar pozitie', 'Label', 'Nr. confirmare 1', 'Data iesire 1', 'Data livrare 1', 'Nr. confirmare 2', 'Data iesire 2', 'Data livrare 2', 'Nr. confirmare 3','Data iesire 3', 'Data livrare 3', 'Nr. poz. cod compus']
st.write(df_ccf)

#%%#############################################################


############## Valori stocuri df_stock ###############
#%%=======================================================
st.header("Valori stocuri - df_stock")
#elimina rows cu Cod produs necompletat
df_stock = df_stock.dropna(subset=['Artikelnummer'])
convert_dict={
 'erweiterter Lagerbegriff':np.str_,
 'Artikelnummer':np.str_,
 'Bezeichnung':np.str_,
 'Mengeneinheit':np.str_,
 'Physischer Best.':np.float32,
 'Verfügbarer Bestand':np.float32,
 'Reserv. Best.':np.float32,
 'Auftrags-Best.':np.float32,
 'Bestell-Best.':np.float32,
 'Durchschnitts-EKP':np.float32,
 'Lagerwert':np.float32,
 'Wert Physischer Best.':np.float32,
 'Preismengeneinheit Verkauf':np.float32,
 'Preismengeneinheit Verkauf (übersetzt)':np.str_,
 'Verkaufspreis':np.float32,
 'Datum letzter Abgang':np.datetime64,
 'Datum letzter Zugang':np.datetime64,
 'Standardlieferant':np.str_,
 'Artikel Hauptgruppe':np.str_
}

df_stock = df_stock.astype(convert_dict)
df_stock.columns = ['Depozit' ,'Cod produs', 'Descriere' ,	'UM', 'Stoc fizic',	'Stoc disponibil', 'Cant. Rezervata', 'Cantitate in Comenzi clienti', 'Cantitate in Comenzi furnizori', 'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica', 'Categ. Pret vanzare', 'Categorie pret / descriere', 'Pret lista', 'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse'] 
df_stock = df_stock[['Depozit' ,'Cod produs', 'Descriere' , 'UM', 'Stoc fizic', 'Stoc disponibil', 'Cant. Rezervata', 'Cantitate in Comenzi clienti', 'Cantitate in Comenzi furnizori', 'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica', 'Categ. Pret vanzare', 'Categorie pret / descriere', 'Pret lista', 'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse']]
st.write(df_stock)
#%%#############################################################


############## Stocuri Minime Depozite Principale df_stocmin ###############
#%%=======================================================

st.header("Stocuri minime - df_stocmin")
#elimina rows cu Cod produs necompletat
df_stocmin = df_stocmin.dropna(subset=['Cod produs'])
convert_dict={
 'Depozit':np.str_,
 'Cod produs':np.str_,
 'Label':np.str_,
 'Descriere produs':np.str_,
 'Unitate masura':np.str_,
 'Stoc minim':np.float32,
 'Unitate ambalare':np.str_,
 'Comanda minima':np.float32,
 'Cantitate luna precedenta':np.float32,
 'Cantitate an precedent':np.float32,
 'Cantitate an curent':np.float32,
 'Furnizor principal':np.str_
}
#!!!GOOD!!!
df_stocmin = df_stocmin.astype(convert_dict)
df_stocmin.columns = ['Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal']
today = datetime.now().date()
luna_curenta = datetime.now().month
year_start = datetime(datetime.now().year, 1,1).date()
df_stocmin['Medie zilnica an curent'] = round(df_stocmin['Cantitate an curent']/(today-year_start).days,4)
df_stocmin['Medie lunara an curent'] = round(df_stocmin['Cantitate an curent']/luna_curenta,4)
df_stocmin['Medie lunara an precedent'] = round(df_stocmin['Cantitate an precedent']/12,4)
df_stocmin = df_stocmin[['Medie zilnica an curent', 'Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal', 'Medie lunara an curent', 'Medie lunara an precedent']]
st.write(df_stocmin)
#%%#############################################################


############## Status comenzi furnizori intarziat ###############
#=======================================================
st.header("Status comenzi furnizori intarziat")
df_cfi = df_cfd.copy(deep=True)
df_cfi.drop(['Cod furnizor', 'Abgangs-Datum', 'Tip comanda furnizor', 'Pret manual', 'Cod curs valutar', 'Stoc disponibil', 'Confirmare rezervare', 
'Confirmare comanda furnizor', 'Valoare comenda  furnizor', 'Data livrare dorita'], axis=1, inplace=True)
df_cfi['Zi referinta'] = pd.to_datetime(today)
df_cfi['KW data referinta'] = today.isocalendar().week
df_cfi['An referinta'] = datetime.now().year
df_cfi['KW data livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.isocalendar().week)
df_cfi['An livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.year)
df_cfi['Zile intarziere'] = (df_cfi['Zi referinta']-df_cfi['Data livrare']).apply(lambda x: x.days)

#define keys for join
df_ccd.set_index('Depozit', 'Cod produs')
df_cfi.set_index('Depozit', 'Cod produs')
df_stocmin.set_index('Depozit', 'Cod produs')

# join cu df_cco pt Data livrare('Cel mai vechi termen de livrare catre client') si NumeF('Client') dupa Legatura (CC) cu Legatura Depozit 
df_cfi=df_cfi.join(df_ccd,rsuffix='_df_ccd')
# join cu df_stocuriMinime pt Stoc minim('Stoc Minim') dupa Legatura (SM) cu Legatura Depozit  
df_cfi = df_cfi.join(df_stocmin, rsuffix='_df_sm')
print(df_cfi.columns.to_list())


df_cfi.drop(['Grupa client', 'Cod client', 'Numar intern comanda client_df_ccd', 'Numar pozitie_df_ccd', 'Cod produs_df_ccd', 'Text produs', 'Tip comanda client', 'Depozit_df_ccd', 
'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare','Cantitate pozitie_df_ccd', 'Cantitate livrata', 'Cantitate restanta_df_ccd', 
'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal','Cod curs valutar', 'Livrare partiala permisa 1=DA', 'Unitate masura_df_ccd', 'Cod produs client', 
'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor','Persoana de contact', 'Depozit_df_sm', 'Data inregistrare_df_ccd', 'Cod produs_df_sm', 
'Label', 'Descriere produs_df_sm', 'UM', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 
'Furnizor principal', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent'], axis=1, inplace=True)
df_cfi.rename(columns={'Nume furnizor':'Furnizor', 'Numar intern comanda client':'Nr comanda', 'Numar pozitie':'Pozitie', 'Cod produs':'Cod Lingemann', 
'Furnizori / produs':'Cod Furnizori / produs', 'Descriere produs':'Denumire produs', 'Unitate masura':'UM', 'Data inregistrare': 'Data comenzii', 
'Data livrare':'Cel mai vechi termen de livrare catre client', 'Data livrare_df_ccd':'Data livrare', 'Cantitate pozitie':'Cantitate comanda', 'NumeF':'Client', 'Adresa e-mail':'Adresa contact'}, inplace=True)
df_cfi.fillna(value={'Cel mai vechi termen de livrare catre client': "FARA COMANDA CLIENT", 'Client': " ", 'Stoc minim': "FARA STOC MINIM"}, inplace=True)

conditions = [
    df_cfi['Zi referinta'] >= df_cfi['Cel mai vechi termen de livrare catre client'],
    df_cfi['An livrare'] > df_cfi['An referinta'],
    df_cfi['KW data livrare'] == df_cfi['KW data referinta'],
    df_cfi['KW data livrare'] == df_cfi['KW data referinta']+1
]

#define results
results = ['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']

#create new column based on conditions in column1 and column2
df_cfi['Status comanda'] = np.select(conditions, results)
df_cfi.fillna(value={'Status comanda': "IN TERMEN"}, inplace=True)
df_cfi=df_cfi[['Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status comanda', 'Furnizor', 'Nr comanda', 'Pozitie', 
'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta',  'Data comenzii', 'Data livrare', 
'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit']]
st.write(df_cfi)

#%%#########################################################

############## Pt. CC O2N si situatie CF ordonat dupa data comenzii ###############
#%%=======================================================



#%%#########################################################