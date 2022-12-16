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

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'blue' if val > 90 else 'black'
    return 'color: % s' % color

# initializare datarames din fisiere
df_ccd = pd.read_excel('input/Comenzi clienti deschise - lucru.xlsx')
df_cfd = pd.read_excel('input/Comenzi furnizori deschise - lucru.xlsx',skiprows=1)
df_ccf = pd.read_excel('input/Confirmari comenzi furnizori.xlsx', skiprows=1, skipfooter=1)
df_stock = pd.read_excel('input/Stock value_RO.xlsx', skiprows=1, skipfooter=1)
df_stocmin = pd.read_excel('input/Stocuri minime dep. principale.xlsx', skiprows=1, skipfooter=1)
df_ka = pd.read_excel('input/Clienti - KA.xlsx')
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
# AgGrid(df_ccdModified)

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
        height=500, 
        width='100%',
        reload_data=False
    )

    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected)
    return df

##############################################################
#niceGrid(df_ccdModified)

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
df_StocActual['Legatura'] = df_StocActual['Depozit'].str.strip()+df_StocActual['Cod produs'].str.strip()
#st.dataframe(df_StocActual)
df_StocActual_todisplay=df_StocActual.copy()
niceGrid(df_StocActual_todisplay)


st.header("Stocuri minime")
df_StocuriMinime = df_stocminModified.copy()
df_StocuriMinime.columns = ['Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal']
df_StocuriMinime['Legatura'] = ''
df_StocuriMinime['Legatura'] = df_StocuriMinime['Depozit'].str.strip()+df_StocuriMinime['Cod produs'].str.strip()
today = datetime.now().date()
luna_curenta = datetime.now().month
year_start = datetime(datetime.now().year, 1,1).date()
df_StocuriMinime['Medie zilnica an curent'] = round(df_StocuriMinime['Cantitate an curent']/(today-year_start).days,4)
df_StocuriMinime['Medie lunara an curent'] = round(df_StocuriMinime['Cantitate an curent']/luna_curenta,4)
df_StocuriMinime['Medie lunara an precedent'] = round(df_StocuriMinime['Cantitate an precedent']/12,4)
#st.dataframe(df_StocuriMinime)
df_StocuriMinime_todisplay=df_StocuriMinime.copy()
niceGrid(df_StocuriMinime_todisplay)


st.header("Comenzi clienti ordonate dupa data de livrare O2N")
df_cco = df_ccdModified.copy()
df_cco.columns = ['Grupa client', 'Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact', 'NumeF']
#df_cco.applymap(lambda x: x.strip() if isinstance(x, str) else x)
df_cco['Legatura CC'] = ''
df_cco['Legatura CC'] = df_cco['Depozit'].str.strip()+df_cco['Lieferartikel'].str.strip()
df_cco['Data livrare'] = pd.to_datetime(df_cco['Data livrare'])
df_cco.sort_values(by='Data livrare', inplace=True)
#st.dataframe(df_cco)
df_cco_todisplay=df_cco.copy()
niceGrid(df_cco_todisplay)

st.header("RAPORT SENIOR MANAGEMENT - Comenzi Clienti - cantitati restante")
pivot_cc = df_cco.pivot_table(index =['Legatura CC'], values =['Cantitate restanta'], aggfunc ='sum')
pivot_cc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
pivot_cc.loc["GRAND TOTAL"] = pivot_cc['Cantitate restanta'].sum()
#st.dataframe(pivot_cc)
pivot_cc.to_excel("output/Pivot CC pt SM.xlsx")
# ia inapoi in dataframe pentru ca nu mai am cheia... - alternativa ar fi sa incerc cu groupby sa vad ce iese
pcc=pd.read_excel('output/Pivot CC pt SM.xlsx')
#pivot_cc_todisplay=pivot_cc.copy()
#niceGrid(pivot_cc_todisplay)

st.header("Confirmari Comenzi Furnizori")
df_ccf2 = df_ccfModified.copy()
df_ccf2['Numar pozitie'] = df_ccf2['Numar pozitie'].astype(float).astype(int).astype(str)
df_ccf2['Legatura CF'] = ''
#df_ccf2['Legatura CF'] = df_ccf2['Numar intern comanda client'].astype(str)+df_ccf2['Numar pozitie'].astype(str)
df_ccf2['Legatura CF'] = df_ccf2['Numar intern comanda client'].astype('string')+(df_ccf2['Numar pozitie']).astype('string')
#st.dataframe(df_ccf2)
df_ccf2_todisplay=df_ccf2.copy()
niceGrid(df_ccf2_todisplay)

st.header("Comenzi Furnizori ordonate dupa data de inregistrare O2N")
df_cfo = df_cfdModified.copy()
df_cfo.drop(['Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Label'], axis=1, inplace=True)
df_cfo['Legatura'] = ''
df_cfo['Legatura'] = df_cfo['Numar intern comanda client.1'].map(str)+df_cfo['Numar pozitie.1'].map(str)+df_cfo['Lieferartikel'].map(str)
df_cfo.sort_values(by=['Data inregistrare'], inplace=True)
df_cfo_todisplay=df_cfo.copy()
#st.dataframe(df_cfo)
niceGrid(df_cfo_todisplay)

st.header("Status comenzi furnizori intarziat")
df_cfi = df_cfo.copy()
df_cfi.drop(['Cod client.1', 'Abgangs-Datum', 'Tip comanda furnizor', 'Pret manual', 'Cod curs valutar', 'Stoc disponibil', 'Confirmare rezervare', 'Confirmare comanda furnizor', 'Valoare comenda  furnizor', 'Data livrare - dorita'], axis=1, inplace=True)
df_cfi['Legatura depozit'] = ''
df_cfi['Legatura depozit'] = df_cfi['Depozit'].str.strip()+df_cfi['Lieferartikel'].str.strip()
df_cfi['Zi referinta'] = pd.to_datetime(today)
df_cfi['KW data referinta'] = today.isocalendar().week
df_cfi['An referinta'] = datetime.now().year
df_cfi['KW data livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.isocalendar().week)
df_cfi['An livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.year)
df_cfi['Zile intarziere'] = (df_cfi['Zi referinta']-df_cfi['Data livrare']).apply(lambda x: x.days)

# join cu df_cco pt Data livrare('Cel mai vechi termen de livrare catre client') si NumeF('Client') dupa Legatura (CC) cu Legatura Depozit 
df_cfim1 = df_cfi.join(df_cco.set_index('Legatura CC'), on=['Legatura depozit'], how='left', rsuffix='_df_cco')
# join cu df_stocuriMinime pt Stoc minim('Stoc Minim') dupa Legatura (SM) cu Legatura Depozit  
df_cfim2 = df_cfim1.join(df_StocuriMinime.set_index('Legatura'), on=['Legatura depozit'], how='left', rsuffix='_df_sm')

#drop excessive columns
# 'Legatura', 'Grupa client', 'Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel_df_cco', 'Text produs', 'Tip comanda client', 'Depozit_df_cco', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare_df_cco', 'Cantitate pozitie_df_cco', 'Cantitate livrata', 'Cantitate restanta_df_cco', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Dtaa inregistrare_df_cco', 'Cod curs valutar', 'Livrare partiala permisa 1=DA', 'Unitate masura_df_cco','Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact', 'Depozit_df_sm', 'Cod produs', 'Label', 'Descriere produs_df_sm', 'UM', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent'
df_cfim2.drop(['Grupa client', 'Cod client', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel_df_cco', 'Text produs', 'Tip comanda client', 'Depozit_df_cco', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Cantitate pozitie_df_cco', 'Cantitate livrata', 'Cantitate restanta_df_cco', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Cod curs valutar', 'Livrare partiala permisa 1=DA', 'Unitate masura_df_cco','Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact', 'Depozit_df_sm', 'Cod produs', 'Label', 'Descriere produs_df_sm', 'UM', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent'], axis=1, inplace=True)

#rename columns 
# Adresa 1 -> Furnizor
# Numar intern comanda client.1 -> Nr comanda
# Numar pozitie.1 -> Pozitie
# Lieferartikel -> Cod Lingemann
# Furnizori / produs -> Cod Furnizori / produs
# Descriere produs -> Denumire produs
# Unitate masura -> UM
# Data ingregistrare -> Data comenzii
# Cantitate pozitie -> Cantitate comanda
df_cfim2.rename(columns={'Adresa 1':'Furnizor', 'Numar intern comanda client.1':'Nr comanda', 'Numar pozitie.1':'Pozitie', 'Lieferartikel':'Cod Lingemann', 'Furnizori / produs':'Cod Furnizori / produs', 'Descriere produs':'Denumire produs', 'Unitate masura':'UM', 'Data inregistrare_df_cco': 'Data comenzii', 'Data livrare_df_cco':'Cel mai vechi termen de livrare catre client', 'Cantitate pozitie':'Cantitate comanda', 'NumeF':'Client'}, inplace=True)

#fill N/A values with corresponding words on added columns 
df_cfim2.fillna(value={'Cel mai vechi termen de livrare catre client': "FARA COMANDA CLIENT", 'Client': " ", 'Stoc minim': "FARA STOC MINIM"}, inplace=True)

# adauga Status Comanda -> in functie de Data livrare vs zi/luna/an referinta
conditions = [
    df_cfim2['Zi referinta'] >= df_cfim2['Data livrare'],
    df_cfim2['An livrare'] > df_cfim2['An referinta'],
    df_cfim2['KW data livrare'] == df_cfim2['KW data referinta'],
    df_cfim2['KW data livrare'] == df_cfim2['KW data referinta']+1
]

#define results
results = ['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']

#create new column based on conditions in column1 and column2
df_cfim2['Status comanda'] = np.select(conditions, results)
df_cfim2.fillna(value={'Status comanda': "IN TERMEN"}, inplace=True)

#st.dataframe(df_cfim2)
df_cfim2_todisplay=df_cfim2.copy()
niceGrid(df_cfim2_todisplay)
df_cfim2.sort_values(by=['Status comanda'], inplace=True)
df_cfim2.to_excel('output/Comenzi furnizori - completa.xlsx')


st.header("Pt. CC O2N si situatie CF ordonat dupa data comenzii")
df_cfcc = df_cfim2.copy()
df_cfcc['Cod PIO'] = df_cfcc['Cod Lingemann']
df_cfcc['Legatura CF'] = df_cfcc['Nr comanda'].map(str)+df_cfcc['Pozitie'].map(str)
df_cfcc1 = df_cfcc.join(df_ccf2.set_index('Legatura CF'), on=['Legatura CF'], how='left', rsuffix='_df_ccf')
df_cfcc1.rename(columns={'Data iesire 1':'DC1', 'Data livrare 1':'TL1', 'Data iesire 2':'DC2', 'Data livrare 2':'TL2','Data iesire 3':'DC3', 'Data livrare 3':'TL3'}, inplace=True)
df_cfcc1.fillna(value={'DC1': pd.to_datetime("1990-01-01"), 'TL1': pd.to_datetime("1990-01-01"), 'DC2': pd.to_datetime("1990-01-01"), 'TL2': pd.to_datetime("1990-01-01"), 'DC3': pd.to_datetime("1990-01-01"), 'TL3': pd.to_datetime("1990-01-01")}, inplace=True)

df_cfcc1.drop(['Numar intern comanda client', 'Numar pozitie', 'Label', 'Nr. confirmare 1', 'Nr. confirmare 2','Nr. confirmare 3', 'Nr. poz. cod compus'], axis=1, inplace=True)
# pentru coloana Status
df_cfcc1['Status'] = 'FARA CONFIRMARE'
for index in range(len(df_cfcc1)): 
    if (pd.to_datetime(df_cfcc1['DC3'].iloc[index])>pd.to_datetime("1990-01-01")):
        df_cfcc1['Status'].iloc[index] = df_cfcc1['DC3'].iloc[index]
    else:
        if (pd.to_datetime(df_cfcc1['DC2'].iloc[index])>pd.to_datetime("1990-01-01")):
            df_cfcc1['Status'].iloc[index] = df_cfcc1['DC2'].iloc[index]
        else:
            if (pd.to_datetime(df_cfcc1['DC1'].iloc[index])>pd.to_datetime("1990-01-01")):
                df_cfcc1['Status'].iloc[index] = df_cfcc1['DC1'].iloc[index]
            else:
                df_cfcc1['Status'].iloc[index] = "FARA CONFIRMARE"
#df_cfcc1.fillna(value={'Status': "FARA CONFIRMARE"}, inplace=True)
#df_cfcc1['Status'] = np.where(df_cfcc1['Status']>pd.to_datetime("1900-01-01"), pd.to_datetime(df_cfcc1['Status']), 'FARA CONFIRMARE')
df_cfcc1['Data Confirmare CF'] = df_cfcc1['Status']
#df_cfcc1['Data Comenzii'] = df_cfcc['Data comenzii']
df_cfcc1.sort_values(by=['Data inregistrare'], inplace=True)
#st.dataframe(df_cfcc1)
df_cfcc1_todisplay=df_cfcc1.copy()
niceGrid(df_cfcc1_todisplay)

st.header("RAPORT SENIOR MANAGEMENT - Comenzi Furnizori - cantitati restante")
pivot_cf = df_cfcc1.pivot_table(index =['Legatura depozit'],aggfunc ={'Nr comanda': lambda x: len(x.unique()),'Cantitate restanta':'sum'})
pivot_cf.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
pivot_cf.loc["GRAND TOTAL"] = [pivot_cf['Cantitate restanta'].sum(), pivot_cf['Nr comanda'].sum()]
st.dataframe(pivot_cf)
#pivot_cf_to_display=pivot_cf.copy()
#niceGrid(pivot_cf_to_display)
pivot_cf.to_excel("output/Pivot CF pt SM.xlsx")
# ia inapoi in dataframe pentru ca nu mai am cheia... - alternativa ar fi sa incerc cu groupby sa vad ce iese
pcf=pd.read_excel('output/Pivot CF pt SM.xlsx')

st.header("Lucru CC - !De gasit un nume mai destept!")
df_lcc = df_cco.copy()
df_lcc['Zi referinta'] = pd.to_datetime(today)
df_lcc['Legatura depozit'] = df_lcc['Depozit'].str.strip()+df_lcc['Lieferartikel'].str.strip()
df_lcc['KW livrare'] = pd.to_datetime(df_lcc['Data livrare']).apply(lambda x: x.isocalendar().week)
df_lcc['Year livrare'] = pd.to_datetime(df_lcc['Data livrare']).apply(lambda x: x.year)
df_lcc['Zile intarziere'] = (df_lcc['Zi referinta']-df_lcc['Data livrare']).apply(lambda x: x.days)
df_lcc['Currency'] = df_lcc['Cod curs valutar']
df_lcc['TIP TL'] = np.where(df_lcc['Cod termen livrare']=="B", "APROXIMATIV","FIX")

df_lcc1 = df_lcc.join(df_cfcc1.set_index('Legatura depozit'), on=['Legatura depozit'], how='left', rsuffix='_df_cfcc1')
#replace Currency RON for empty values
df_lcc1.fillna(value={'Currency': "RON"}, inplace=True)
df_lcc1.fillna(value={'Furnizor': ""}, inplace=True)
# fill new column "RESTRICTII"
conditionsl = [
    df_lcc1['Validare comanda client'] == "N",
    df_lcc1['Validare generare dispozitie livrare'] == "N",
    np.isclose(df_lcc1['Livrare partiala permisa 1=DA'].round(1), 0.0)
]
#define results
resultsl = ['ORDER RELEASE: NO', 'KOMMFREIGABE: NEIN', 'COMANDA SE LIVREAZA INTEGRAL']

#create new column based on conditions in column1 and column2
df_lcc1['RESTRICTII'] = np.select(conditionsl, resultsl)
df_lcc1.fillna(value={'RESTRICTII': "FARA RESTRICTII"}, inplace=True)
df_lcc1.fillna(value={'Status Comanda': "INTARZIATE"}, inplace=True)

df_lcc1['Cea mai veche CF'] = df_lcc1['Data comenzii']
df_lcc1.fillna(value={'Cea mai veche CF': "FARA CF"}, inplace=True)
#df_lcc1['Data confirmare CF'] = df_lcc1['Status']
df_lcc1.fillna(value={'Data Confirmare CF': ""}, inplace=True)
df_lcc1['Data livrare CF'] = df_lcc1['Data livrare']
df_lcc1.fillna(value={'Data livrare': ""}, inplace=True)
#rename columns
df_lcc1.drop(['Legatura CC', 'Currency', 'TIP TL', 'Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'Data inregistrare_df_cfcc1', 'Cantitate comanda', 'Cantitate restanta_df_cfcc1', 'Depozit_df_cfcc1', 'Data livrare_df_cfcc1', 'Adresa e-mail', 'Legatura', 'Zi referinta_df_cfcc1', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Zile intarziere_df_cfcc1', 'Cel mai vechi termen de livrare catre client', 'Data comenzii', 'Client', 'Stoc minim', 'Cod PIO', 'Legatura CF', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status'], axis=1, inplace=True)
df_lcc1.rename(columns={'Grupa client':'Grup', 'NumeF':'Nume client', 'Numar intern comanda client':'Nr. intern CC', 'Lieferartikel':'Cod produs', 'Text produs':'Denumire', 'Validare generare dispozitie livrare':'Se pot emite DL', 'Validare comanda client':'Order Release', 'Cod termen livrare':'Termen de livrare', 'Cantitate pozitie':'Cantitate comanda', 'Reprezentant principal':'Key Account', 'Data inregistrare':'Data creere', 'Cod curs valutar':'Moneda', 'Nr. comanda client':'NR. extern CC', '':''}, inplace=True)
#drop columns
df_lcc2 = df_lcc1.join(df_ka.set_index('Client'), on=['Nume client'], how='left', rsuffix='_df_cfcc1')
df_lcc2.drop(['Grup_df_cfcc1'], axis=1, inplace=True)
df_lcc2.sort_values(by=['Zile intarziere'], ascending=False, inplace=True)
#st.dataframe(df_lcc2)
df_lcc2_to_display=df_lcc2.copy()
niceGrid(df_lcc2_to_display)

#st.header("Status CC de copiat - !De gasit un nume mai destept! - se copiaza acum in excel in output folder")
#pivot_statcc = df_lcc2.pivot_table(index =['KA'], columns=['Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'UM', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor'], 
#aggfunc = np.sum, margins=False, margins_name='GRAND TOTAL')
#pivot_statcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
#pivot_statcc.loc["GRAND TOTAL"] = [pivot_cf['Cantitate restanta'].sum(), pivot_cf['Valoare restanta'].sum()]
#st.dataframe(pivot_statcc)
groupedcc = df_lcc2.groupby(['KA','Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'UM', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor']).aggregate({'Cantitate restanta':'sum', 'Valoare restanta':'sum'})
groupedcc.to_excel("output/GroupBy Test.xlsx")
#incearca sa-i faci afisare in tabele mai destepte
#st.dataframe(groupedcc)
#st.table(groupedcc)
#groupedcc_to_display=groupedcc.copy()
#niceGrid(groupedcc_to_display)


st.header("Verificare SM de copiat")
df_smc = df_StocuriMinime.copy()
df_smc.drop(['Label', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal'], axis=1, inplace=True)
df_smc.rename(columns={'Cod produs':'Cod PIO', 'Stoc minim':'Stoc minim / depozit'}, inplace=True)

df_smc1=df_smc.join(df_cfcc1.set_index('Legatura depozit'), on=['Legatura'], how='left', rsuffix='_df_cfcc1')
df_smc1.drop(['Nr comanda', 'Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM_df_cfcc1', 'Data inregistrare', 'Cantitate comanda', 'Cantitate restanta', 
'Depozit_df_cfcc1', 'Adresa e-mail', 'Legatura_df_cfcc1', 'Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Zile intarziere', 'Cel mai vechi termen de livrare catre client', 
'Client', 'Stoc minim', 'Status comanda', 'Cod PIO_df_cfcc1', 'Legatura CF', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Data Confirmare CF'], axis=1, inplace=True)
df_smc1.fillna(value={'Data comenzii': ""}, inplace=True)
df_smc1.fillna(value={'Status': ""}, inplace=True)
df_smc1.fillna(value={'Data livrare': ""}, inplace=True)
df_smc1.fillna(value={'Furnizor': ""}, inplace=True)
df_smc1.rename(columns={'Data comenzii':'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC', 'Status':'Data confirmare cea mai veche CF - din lucru supplier - status pt. CC', 'Data livrare':'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC', 'Furnizor':'Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'}, inplace=True)

#join cu pivot
df_smc2=df_smc1.join(pcc.set_index('Legatura CC'), on=['Legatura'], how='left', rsuffix='_pcc')
df_smc2.fillna(value={'Cantitate restanta': 0}, inplace=True)
df_smc2.rename(columns={'Cantitate restanta':'Cant deschisa in CC - din CC deschise'}, inplace=True)

df_smc3=df_smc2.join(pcf.set_index('Legatura depozit'), on=['Legatura'], how='left', rsuffix='_pcf')
df_smc3.fillna(value={'Cantitate restanta': 0}, inplace=True)
df_smc3.rename(columns={'Cantitate restanta':'Cantitate in CF - din CF deschise'}, inplace=True)
df_smc3.fillna(value={'Nr comanda': ""}, inplace=True)
df_smc3.rename(columns={'Nr comanda':'Numar CF deschise - din CF deschise'}, inplace=True)

df_smc4=df_smc3.join(df_StocActual.set_index('Legatura'), on=['Legatura'], how='left', rsuffix='_pcf')
df_smc4.drop(['Depozit_pcf', 'Cod produs', 'Descriere', 'UM_pcf', 'Stoc disponibil', 'Cant. Rezervata', 'Cantitate in Comenzi clienti','Cantitate in Comenzi furnizori', 'Categ. Pret vanzare',
'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica',  'Categorie pret / descriere', 'Pret lista', 
'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse'], axis=1, inplace=True)
df_smc4.fillna(value={'Stoc fizic': 0}, inplace=True)
df_smc4.rename(columns={'Stoc fizic':'Stoc actual / depozit din stocuri'}, inplace=True)

df_smc4['Zile acoperite de stoc'] = np.where(df_smc4['Medie zilnica an curent']!=0, 
np.round((df_smc4['Stoc actual / depozit din stocuri']-df_smc4['Cantitate in CF - din CF deschise'])/df_smc4['Medie zilnica an curent']),"FARA RULAJ AN CURENT")

df_smc4['Zile pana la livrare CF'] = np.where(df_smc4['Cantitate in CF - din CF deschise']!=0, 
(df_smc4['data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC']-pd.to_datetime(today)).apply(lambda x: x.days),-1000)

df_smc4['Status']=''
for index in range(len(df_smc4)): 
    if (df_smc4['Cant deschisa in CC - din CC deschise'].iloc[index] > 0):
        if (df_smc4['Stoc actual / depozit din stocuri'].iloc[index] == 0):
            df_smc4['Status'].iloc[index] = "00 - Produs cu CC si fara stoc"
        else: 
            if (df_smc4['Stoc actual / depozit din stocuri'].iloc[index] >= df_smc4['Cant deschisa in CC - din CC deschise'].iloc[index]+df_smc4['Stoc minim / depozit'].iloc[index]):
                df_smc4['Status'].iloc[index] = "10-SA acopera CC si SM"
            else: 
                if (df_smc4['Stoc actual / depozit din stocuri'].iloc[index] >= df_smc4['Cant deschisa in CC - din CC deschise'].iloc[index]):
                    df_smc4['Status'].iloc[index] = "02-SA acopera CC dar nu acopera SM"
                else:
                    df_smc4['Status'].iloc[index] = "01-SA nu acopera CC"
    else:
        if (df_smc4['Stoc actual / depozit din stocuri'].iloc[index] >= df_smc4['Stoc minim / depozit'].iloc[index]):
            df_smc4['Status'].iloc[index] = "09-SA acopera SM"
        else: 
            if (df_smc4['Stoc actual / depozit din stocuri'].iloc[index] == 0):
                if (df_smc4['Zile pana la livrare CF'].iloc[index] < 0):
                    df_smc4['Status'].iloc[index] = "03-Fara SA si CF intarziate sau fara CF"
                else: 
                    df_smc4['Status'].iloc[index] = "04-Fara SA si CF in termen"
            else:
                df_smc4['Status'].iloc[index] = "05- SA nu acopera SM - Verificare zile acoperite de stoc"



#st.dataframe(df_smc4)
df_smc4_to_display=df_smc4.copy()
niceGrid(df_smc4_to_display)
df_smc4.sort_values(by=['Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'], ascending=False, inplace=True)
df_smc4.to_excel("output/Situatie SM final.xlsx")


st.header("Centralizator comenzi clienti - copiat in excel")
pivot_centralizator = groupedcc.groupby(['Cod client', 'Nume client', 'Status comanda']).aggregate({'Valoare restanta':'sum'})
pivot_centralizator.to_excel("output/Status comenzi clienti Centralizator.xlsx")
st.table(pivot_centralizator)
#pivot_centralizator_to_display=pivot_centralizator.copy()
#niceGrid(pivot_centralizator_to_display)
