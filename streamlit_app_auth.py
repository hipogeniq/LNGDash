# imports for needed packages
import math
import streamlit as st  # 🎈 data web app development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import streamlit_authenticator as stauth
import plotly as plotly 
import plotly.express as px # for simple plots like pie charts
import locale
import yaml
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="LNG Dashboard",
    page_icon="🧊",
    layout="wide",
 )

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)
    authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
    )

current_user = ""
current_role = ""

#################### Update user info ########################
def update_user_info():
    try:
        if authenticator.update_user_details(st.session_state.current_user, 'Update user details'):
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)


#################### Register user ########################
def register_user():
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

##################### Reset password #########################
def reset_password():
    try:
        if authenticator.reset_password(st.session_state.current_user, 'Reset password'):
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

#################### Forgot password #########################
def forgot_password():
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
        if username_forgot_pw:
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('New password sent securely')
            # Random password to be transferred to user securely
        elif username_forgot_pw == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)
    

################### Check user autorization and role #######################
def check_user():
    current_user =""
    name, authentication_status, username = authenticator.login('Login', 'main')
    if st.session_state["authentication_status"]:
        authenticator.logout('Logout', 'main')
        role = "Unknown"
        for id, info in authenticator.credentials.get("usernames").items():
            if id==username:
                for key in info:
                    if key == "role": role = info[key]
        st.write(f'Welcome *{name}* as *{role}*')
        #### RENDER MAIN PAGE ####
        
        col1, mid, col2 = st.columns([1,1,20])
        with col1:
            image = Image.open('lingemann-logo-service.jpg')
            st.image(image, width=100)
        with col2:
            st.title("LNG Dashboard")
        st.session_state.current_user = username
        current_role = role
        mainpage(role, name, username)
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] == None:
        st.warning('Please enter your username and password')
    return current_user
################### A NEW GRID DISPLAY #######################

def niceGrid(dataset):
    gb = GridOptionsBuilder.from_dataframe(dataset)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=1000) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_default_column(groupable=True)
    gb.configure_grid_options(allowContextMenuWithControlKey=True, enableCharts=True)
    #gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    gridOptions = gb.build()

    grid_response = AgGrid(
        dataset,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        columns_auto_size_mode=False,
        theme='material', #Add theme color to the table
        enable_enterprise_modules=True,
        height=500,
        width='50%',
        reload_data=False
    )

    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected)
    return df

#################### MAIN PAGE CONTENT ##########################################

def mainpage(role, name, username): 
    
    #this is for formatting the numeric fields to 999.999,99
    locale.setlocale(locale.LC_ALL, 'pt_br.utf-8')
    pd.set_option('display.float_format', lambda x: locale.format('%.2f', x, grouping=True))

    if role=="Unknown":
        st.header(name + " -> Fara un rol definit nu poti accesa date. Vorbeste cu Admin")
        return
 
    #pd.options.display.precision = 2
    #pd.options.display.float_format = '{:,.2f}'.format
    if (role=="ka"): 
        user = username.capitalize() 
    else: 
        user = username

    pageContent(role,name,user)

    # with st.form(key="form"):
    #     submit_button = st.form_submit_button(label="Incarca Datele/ Aplica Filtrele")

    # if submit_button:
    #      pageContent(role,name)
    # else:
    #     st.markdown("Foloseste butonul pentru a incarca datele")
   

def pageContent(role, name, username):
    data_referinta = st.date_input("Data de referinta pentru "+username + " :", value=pd.to_datetime("today"), max_value=pd.to_datetime("today"))
    
     ############## initializare datarames din fisiere ###############
    #%%=======================================================
    # 
    df_ccd = pd.read_excel('input/002_Comenzi clienti deschise - lucru.xlsx', skiprows=1, skipfooter=1, converters={'erweiterter Lagerbegriff': str, 'Kundenartikelnr.': str})
    df_cfd = pd.read_excel('input/002_Comenzi furnizori deschise - lucru.xlsx', skiprows=1, skipfooter=1, converters={'Lieferanten Artikelnummer': str, 'erweiterter Lagerbegriff': str})
    df_ccf = pd.read_excel('input/002_Confirmari comenzi furnizori - incepand cu anul precedent.xlsx', skiprows=1, skipfooter=1)
    df_stock = pd.read_excel('input/002_Stock value_RO.xlsx', skiprows=1, skipfooter=1, converters={'erweiterter Lagerbegriff': str})
    df_stocmin = pd.read_excel('input/002_Stocuri minime dep. principale.xlsx', skiprows=1, skipfooter=1, converters={'erweiterter Lagerbegriff': str, 'Bezeichnung': str, 'Verpackungseinheit': str})
    df_ka = pd.read_excel('input/002_Clienti - KA.xlsx')
    df_access = pd.read_excel('input/002_UseriAccess.xlsx')
    
    #%%=======================================================
    ############## [01] Comenzi clienti deschise  df_ccd ###############
    #%%=======================================================
    df_ccd.rename(columns= {'Kundengruppe':'Grupa client', 
    'Kundennummer':'Cod client', 
    'Auftragsnummer (Text)':'Nr. intern comanda client (text)', 
    'Positionsnummer':'Numar pozitie', 
    'Lieferartikel':'Lieferartikel', 
    'Bezeichnung':'Label', 
    'Auftragsschlüssel':'Tip comanda client', 
    'erweiterter Lagerbegriff':'Depozit', 
    'Komm.Freigabe':'Validare generare dispozitie livrare', 
    'Kz. Auftragsfreigabe':'Validare comanda client', 
    'Lieferterminschlüssel':'Cod termen livrare', 
    'Lieferdatum':'Data livrare', 
    'Positionsmenge':'Cantitate pozitie', 
    'Liefermenge':'Cantitate livrata', 
    'Restmenge':'Cantitate restanta', 
    'Restwert':'Valoare restanta', 
    'Deckungsbeitrag':'DB', 
    'DB in %':'DB in %', 
    'Sachbearbeiter':'User', 
    'Erfassungsdatum':'Data inregistrare', 
    'Währungsschlüssel':'Cod curs valutar', 
    'Teillieferung erlaubt 1=JA':'Livrare partiala permisa 1=DA', 
    'Mengeneinheit':'Unitate masura', 
    'Kundenartikelnr.':'Cod produs client', 
    'Kunden-Best.nr.':'Nr. comanda client', 
    'Kunden-Best.datum':'Data comanda client', 
    'zugeordnete Bestellnummer':'Nr. comanda furnizor atribuit', 
    'Bestell-Best.':'Confirmare comanda furnizor', 
    'Ansprechpartner':'Ansprechpartner'}, inplace=True)

    df_cfd.rename(columns=
    {'Kundennummer':'Cod client', 
    'Auftragsnummer':'Numar intern comanda client', 
    'Positionsnummer':'Numar pozitie', 
    'Bezeichnung':'Label', 
    'Kundennummer':'Cod client', 
    'Anschriftszeile1':'Adresa 1', 
    'Auftragsnummer':'Numar intern comanda client', 
    'Positionsnummer':'Numar pozitie', 
    'Lieferartikel':'Lieferartikel', 
    'Lieferanten Artikelnummer':'Furnizori / produs', 
    'Article description':'Descriere produs', 
    'Mengeneinheit':'Unitate masura', 
    'Abgangs-Datum':'Abgangs-Datum', 
    'Bestellschlüssel':'Tip comanda furnizor', 
    'Erfassungsdatum':'Data inregistrare', 
    'Positionsmenge':'Cantitate pozitie', 
    'Restmenge':'Cantitate restanta', 
    'Preis manuell':'Pret manual', 
    'Währungsschlüssel':'Cod curs valutar', 
    'Bestellwert':'Valoare comenda  furnizor', 
    'Verfügbarer Bestand':'Stoc disponibil', 
    'Reserv. Best.':'Confirmare rezervare', 
    'Bestell-Best.':'Confirmare comanda furnizor', 
    'erweiterter Lagerbegriff':'Depozit', 
    'Wunschlieferdatum':'Data livrare - dorita', 
    'Lieferdatum':'Data livrare', 
    'e-Mail-Adresse':'Adresa e-mail'
    }, inplace=True)

    df_ccf.rename(columns=
    {'Auftragsnummer':'Numar intern comanda client', 
    'Positionsnummer':'Numar pozitie', 
    'Bezeichnung':'Label', 
    'Bestätigungs-Nummer 1':'Nr. confirmare 1', 
    'Abgangs-Datum 1':'Data iesire 1', 
    'Lieferdatum 1':'Data livrare 1', 
    'Bestätigungs-Nummer 2':'Nr. confirmare 2', 
    'Abgangs-Datum 2':'Data iesire 2', 
    'Lieferdatum 2':'Data livrare 2',
    'Bestätigungs-Nummer 3':'Nr. confirmare 3', 
    'Abgangs-Datum 3':'Data iesire 3', 
    'Lieferdatum 3':'Data livrare 3',
    'Pos.-Nr. Stückliste':'Nr. poz. cod compus'
    }, inplace=True)

    df_stocmin.rename(columns=
    {'erweiterter Lagerbegriff':'Depozit', 
    'Artikelnummer':'Cod produs', 
    'Bezeichnung':'Label', 
    'Article description':'Descriere produs', 
    'Mengeneinheit':'Unitate masura', 
    'Mindestbestand':'Stoc minim', 
    'Verpackungseinheit':'Unitate ambalare', 
    'Mindestbestellmenge':'Comanda minima', 
    'Menge Vormonat':'Cantitate luna precedenta', 
    'Menge Vorjahr':'Cantitate an precedent', 
    'Menge akt. Jahr':'Cantitate an curent', 
    'Standardlieferant':'Furnizor principal', 
    }, inplace=True)
   
    df_ccd.loc[(df_ccd['Nr. intern comanda client (text)'].isnull()) & (df_ccd['Numar pozitie'].isnull()) & (df_ccd['Lieferartikel'].isnull()), 'NumeF'] = df_ccd['Label']

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

    #curate Depozit column
    df_ccd['Depozit'] =  df_ccd['Depozit'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    #selectie coloane
    df_ccd.columns = ['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB in percents', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']
    df_ccd.sort_values(by='Data livrare', inplace=True)
    #ordine coloane

    
    #%%#############################################################

    ############## [03] Comenzi furnizori deschise  df_cfd ###############
    #%%=======================================================
    #
    df_cfd = df_cfd.dropna(subset=['Lieferartikel'])
    df_cfd['Numar intern comanda client'] = df_cfd['Numar intern comanda client'].astype(int)
    df_cfd['Numar pozitie'] = df_cfd['Numar pozitie'].astype(int)

    convert_dict={
    'Cod client':np.str_,
    'Numar intern comanda client':np.str_,
    'Numar pozitie':np.int8,
    'Label':np.str_,
    'Kundennummer.1':np.str_,
    'Adresa 1':np.str_,
    'Auftragsnummer.1':np.str_,
    'Positionsnummer.1':np.int8,
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
    df_cfd.rename(columns={'Kundennummer.1':'Cod client.1',
    'Auftragsnummer.1':'Numar intern comanda client.1',
    'Positionsnummer.1':'Numar pozitie.1'
    }, inplace=True)

    df_cfd['Numar pozitie'] = df_cfd['Numar pozitie'].astype(int)
    df_cfd.drop(['Cod client', 'Numar intern comanda client.1', 'Numar pozitie.1', 'Label'], axis=1, inplace=True)
    #selectie coloane
    df_cfd.columns = [
    'Numar intern comanda client',
    'Numar pozitie',
    'Cod furnizor',
    'Nume_furnizor',
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
    'Nume_furnizor',
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
    #curate 'Depozit' column
    df_cfd['Depozit'] =  df_cfd['Depozit'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    #%%#############################################################


    ############## [04] Confirmari Comenzi Furnizori df_ccf ###############
    #%%=======================================================
    #
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
    
    

    #%%#############################################################


    ############## [05] Valori stocuri df_stock ###############
    #%%=======================================================
    #
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
    
    
    #%%#############################################################


    ############## [06] Stocuri Minime Depozite Principale df_stocmin ###############
    #%%=======================================================

    #
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

    df_stocmin = df_stocmin.astype(convert_dict)
    df_stocmin.columns = ['Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal']
    today = datetime.now().date()
    luna_curenta = datetime.now().month
    year_start = datetime(datetime.now().year, 1,1).date()
    df_stocmin['Medie zilnica an curent'] = round(df_stocmin['Cantitate an curent']/(today-year_start).days,4)
    df_stocmin['Medie lunara an curent'] = round(df_stocmin['Cantitate an curent']/luna_curenta,4)
    df_stocmin['Medie lunara an precedent'] = round(df_stocmin['Cantitate an precedent']/12,4)
    df_stocmin = df_stocmin[['Medie zilnica an curent', 'Depozit' ,'Cod produs', 'Label', 'Descriere produs' , 'UM', 'Stoc minim',	'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal', 'Medie lunara an curent', 'Medie lunara an precedent']]
    
    
    #%%#############################################################


    ############## [FILTERS] Create filters, apply and create first 6 formated views from above ###############
    #%%=======================================================
    
    #filtru_access_depozit = st.multiselect(ia din df_access si seteaza vizibilitatea pe false) - ia toate depozitele din df_ccd
    # if (role=="admin") or (role=="full_access"):
    #     list_whsAll = list(df_ccd.groupby('Depozit').groups.keys())
    #     list_clientiAll = list(df_ccd.groupby('NumeF').groups.keys())
    #     list_furnizoriAll = list(df_cfd.groupby('Nume_furnizor').groups.keys())
    #     MF01, MF02, MF03 = st.columns(3)
    #     with MF01:
    #         selectDepozit = st.multiselect("Depozite: ", options=list_whsAll, default=list_whsAll, label_visibility="collapsed", disabled=True)
    #     with MF02:
    #         selectClienti = st.multiselect("Clienti: ", options=list_clientiAll, default=list_clientiAll, label_visibility="collapsed", disabled=True)
    #     with MF03:
    #         selectFurnizori = st.multiselect("Furnizori: ", options=list_furnizoriAll, default=list_furnizoriAll, label_visibility="collapsed", disabled=True)
    
    
    # # apply filters on main dataframes for admin and full_access; achizitii and ka will have individual filters
    # if (role=="admin") or (role=="full_access"):
    #     df_ccd=df_ccd.query("Depozit == @selectDepozit & NumeF == @selectClienti")
    #     df_cfd=df_cfd.query("Depozit == @selectDepozit & Nume_furnizor == @selectFurnizori")
    #     df_stock=df_stock.query("Depozit == @selectDepozit")
    #     df_stocmin=df_stocmin.query("Depozit == @selectDepozit")

    #data frame formated for display - create a copy because it may also change the column types and mess up further calculations
    # formatat Comenzi Clienti Deschise
    df_ccd_formatted = df_ccd.copy(deep=True)
    df_ccd_formatted = df_ccd_formatted[['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Lieferartikel', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB in percents', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']]
    df_ccd_formatted['Valoare restanta'] = df_ccd_formatted['Valoare restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['DB'] = df_ccd_formatted['DB'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['DB in percents'] = df_ccd_formatted['DB in percents'].apply(lambda x: "{:,.2f}".format(float(x)) if x!='undefiniert' else x).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Cantitate pozitie'] = df_ccd_formatted['Cantitate pozitie'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Cantitate livrata'] = df_ccd_formatted['Cantitate livrata'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Cantitate restanta'] = df_ccd_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Data livrare'] = df_ccd_formatted['Data livrare'].dt.strftime('%d/%m/%Y')
    df_ccd_formatted['Data inregistrare'] = df_ccd_formatted['Data inregistrare'].dt.strftime('%d/%m/%Y')
    df_ccd_formatted['Data comanda client'] = df_ccd_formatted['Data comanda client'].dt.strftime('%d/%m/%Y')

    # formatat Comenzi Furnizori Deschise
    df_formatted = df_cfd.copy(deep=True)
    df_formatted['Valoare comenda  furnizor'] = df_formatted['Valoare comenda  furnizor'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Cantitate pozitie'] = df_formatted['Cantitate pozitie'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Cantitate restanta'] = df_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Pret manual'] = df_formatted['Pret manual'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Stoc disponibil'] = df_formatted['Stoc disponibil'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Confirmare rezervare'] = df_formatted['Confirmare rezervare'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Confirmare comanda furnizor'] = df_formatted['Confirmare comanda furnizor'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Abgangs-Datum'] = df_formatted['Abgangs-Datum'].dt.strftime('%d/%m/%Y')
    df_formatted['Data inregistrare'] = df_formatted['Data inregistrare'].dt.strftime('%d/%m/%Y')
    df_formatted['Data livrare dorita'] = df_formatted['Data livrare dorita'].dt.strftime('%d/%m/%Y')
    df_formatted['Data livrare'] = df_formatted['Data livrare'].dt.strftime('%d/%m/%Y')

    # formatat Confirmari Comenzi Furnizori 
    df_formatted_04 = df_ccf.copy(deep=True)
    df_formatted_04['Data iesire 1'] = df_formatted_04['Data iesire 1'].dt.strftime('%d/%m/%Y')
    df_formatted_04['Data livrare 1'] = df_formatted_04['Data livrare 1'].dt.strftime('%d/%m/%Y')
    df_formatted_04['Data iesire 2'] = df_formatted_04['Data iesire 2'].dt.strftime('%d/%m/%Y')
    df_formatted_04['Data livrare 2'] = df_formatted_04['Data livrare 2'].dt.strftime('%d/%m/%Y')
    df_formatted_04['Data iesire 3'] = df_formatted_04['Data iesire 3'].dt.strftime('%d/%m/%Y')
    df_formatted_04['Data livrare 3'] = df_formatted_04['Data livrare 3'].dt.strftime('%d/%m/%Y')

    # formatat Stocuri 
    df_formatted_05 = df_stock.copy(deep=True)
    df_formatted_05['Stoc fizic'] = df_formatted_05['Stoc fizic'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Stoc disponibil'] = df_formatted_05['Stoc disponibil'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Cant. Rezervata'] = df_formatted_05['Cant. Rezervata'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Cantitate in Comenzi clienti'] = df_formatted_05['Cantitate in Comenzi clienti'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Cantitate in Comenzi furnizori'] = df_formatted_05['Cantitate in Comenzi furnizori'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Pret mediu de achizitie'] = df_formatted_05['Pret mediu de achizitie'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Valoare marfa disponibila'] = df_formatted_05['Valoare marfa disponibila'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Valoare marfa fizica'] = df_formatted_05['Valoare marfa fizica'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Pret lista'] = df_formatted_05['Pret lista'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_05['Data ultima iesire'] = df_formatted_05['Data ultima iesire'].dt.strftime('%d/%m/%Y')
    df_formatted_05['Data ultima intrare'] = df_formatted_05['Data ultima intrare'].dt.strftime('%d/%m/%Y')

    # formatat Stocuri Minime
    df_formatted_06 = df_stocmin.copy(deep=True)
    df_formatted_06['Medie zilnica an curent'] = df_formatted_06['Medie zilnica an curent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Medie lunara an curent'] = df_formatted_06['Medie lunara an curent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Medie lunara an precedent'] = df_formatted_06['Medie lunara an precedent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Stoc minim'] = df_formatted_06['Stoc minim'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Comanda minima'] = df_formatted_06['Comanda minima'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Cantitate luna precedenta'] = df_formatted_06['Cantitate luna precedenta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Cantitate an precedent'] = df_formatted_06['Cantitate an precedent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted_06['Cantitate an curent'] = df_formatted_06['Cantitate an curent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")

    ############## [02] RAPORT Stocuri minime- Comenzi Clienti - cantitati restante  rcc ###############
    #%%=======================================================

    
    rcc= pd.pivot_table(df_ccd, values=['Cantitate restanta'], index=['Depozit','Lieferartikel'], aggfunc='sum',
                                    fill_value='').reset_index(level=-1)
    #rcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
    rcc.loc['total']= rcc.sum(numeric_only=True)

    #data frame formated for display - create a copy because it may also change the column types and mess up further calculations
    rcc_formatted = rcc.copy(deep=True)
    rcc_formatted['Cantitate restanta'] = rcc_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")

    #st.dataframe(rcc)
    #niceGrid(rcc)
    rcc.to_excel("output/Raport Comenzi Clienti - Cantitati Restante.xlsx")
    #niceGrid(pivot_cc.to_frame())
    pcc=pd.read_excel('output/Raport Comenzi Clienti - Cantitati Restante.xlsx')
    # adauga pie chart
    #pcc.sort_values('Cantitate restanta',ascending=False).head(10).plot(kind='pie', y='Cantitate restanta', autopct='%1.0f%%')
    pcc = pcc.dropna(subset=['Lieferartikel'])
    pcc1=pcc.sort_values('Cantitate restanta',ascending=False).head(10)

    

    #%%=======================================================


    if role=="admin": 
        #[01]
        st.header("Comenzi clienti deschise")
        niceGrid(df_ccd_formatted)

        #[02]
        st.header("Stocuri Minime - Comenzi Clienti - cantitati restante")
        col5, col6 = st.columns((1,1))
        with col5:
            niceGrid(rcc_formatted)
        with col6:
            fig = px.pie(pcc1, values='Cantitate restanta', names='Lieferartikel', title='Top 10 produse cu cantitati restante')
            st.plotly_chart(fig, use_container_width=True)

        #[03]
        st.header("Comenzi furnizori deschise")
        niceGrid(df_formatted)

        #[04]
        st.header("Confirmari Comenzi Furnizori")
        niceGrid(df_formatted_04)

        #[05]
        st.header("Valori stocuri")
        niceGrid(df_formatted_05)
        
        #[06]
        st.header("Stocuri minime")
        niceGrid(df_formatted_06)
    
    
    #%%=======================================================


    ############## [07] Status comenzi furnizori intarziate ###############
    #%%=======================================================
    
    df_cfi = df_cfd.copy(deep=True)
    df_cfi.drop(['Cod furnizor', 'Abgangs-Datum', 'Tip comanda furnizor', 'Pret manual', 'Cod curs valutar', 'Stoc disponibil', 'Confirmare rezervare', 
    'Confirmare comanda furnizor', 'Valoare comenda  furnizor', 'Data livrare dorita'], axis=1, inplace=True)
    df_cfi['Zi referinta'] = pd.to_datetime(data_referinta)
    df_cfi['KW data referinta'] = data_referinta.isocalendar().week
    df_cfi['An referinta'] = datetime.now().year
    df_cfi['KW data livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.isocalendar().week)
    df_cfi['An livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.year)
    df_cfi['Zile intarziere'] = (pd.to_datetime(df_cfi['Zi referinta']) -pd.to_datetime(df_cfi['Data livrare'])).apply(lambda x: x.days)
    df_cfi['Cod produs'] = df_cfi['Cod produs'].str.strip()
    
    df_ccd.fillna(value={'Depozit': ""}, inplace=True)
    df_cfi.fillna(value={'Depozit': ""}, inplace=True)
    df_stocmin.fillna(value={'Depozit': ""}, inplace=True)

    df_ccd['Legatura']=df_ccd['Depozit'].str.strip() + df_ccd['Lieferartikel'].str.strip()
    df_cfi['Legatura']=df_cfi['Depozit'].str.strip() + df_cfi['Cod produs'].str.strip()
    df_stocmin['Legatura']=df_stocmin['Depozit'].str.strip() + df_stocmin['Cod produs'].str.strip()
  

    #define keys for join
    
    df_ccd.set_index('Legatura')
    df_cfi.set_index('Legatura')
    df_stocmin.set_index('Legatura')

    # join cu df_cco pt Data livrare('Cel mai vechi termen de livrare catre client') si NumeF('Client') dupa Legatura (CC) cu Legatura Depozit 
    df_cfi=df_cfi.join(df_ccd.set_index('Legatura'), on='Legatura', rsuffix='_df_ccd')
    # join cu df_stocuriMinime pt Stoc minim('Stoc Minim') dupa Legatura (SM) cu Legatura Depozit  
    df_cfi = df_cfi.join(df_stocmin.set_index('Legatura'), on='Legatura', rsuffix='_df_sm')
    

    #df_cfi.to_excel("output/CFI dupa join SM.xlsx")
    #'Cod produs_df_ccd',
    df_cfi.drop(['Grupa client', 'Cod client', 'Numar intern comanda client_df_ccd', 'Numar pozitie_df_ccd', 'Text produs', 'Tip comanda client', 'Depozit_df_ccd', 
    'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare','Cantitate pozitie_df_ccd', 'Cantitate livrata', 'Cantitate restanta_df_ccd', 
    'Valoare restanta', 'DB', 'DB in percents', 'Reprezentant principal','Cod curs valutar', 'Livrare partiala permisa 1=DA', 'Unitate masura_df_ccd', 'Cod produs client', 
    'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor','Persoana de contact', 'Depozit_df_sm', 'Data inregistrare_df_ccd', 'Cod produs_df_sm', 
    'Label', 'Descriere produs_df_sm', 'UM', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 
    'Furnizor principal', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent', 'Legatura'], axis=1, inplace=True)
    df_cfi.rename(columns={'Nume_furnizor':'Furnizor', 'Numar intern comanda client':'Nr comanda', 'Numar pozitie':'Pozitie', 'Cod produs':'Cod Lingemann', 
    'Furnizori / produs':'Cod Furnizori / produs', 'Descriere produs':'Denumire produs', 'Unitate masura':'UM', 'Data inregistrare': 'Data comenzii', 
    'Data livrare_df_ccd':'Cel mai vechi termen de livrare catre client', 'Cantitate pozitie':'Cantitate comanda', 'NumeF':'Client', 'Adresa e-mail':'Adresa contact'}, inplace=True)
    df_cfi['Status_comanda']= "IN TERMEN"

    conditions = [
        pd.to_datetime(df_cfi['Zi referinta']) > pd.to_datetime(df_cfi['Data livrare']),
        pd.to_datetime(df_cfi['An livrare']) > pd.to_datetime(df_cfi['An referinta']),
        pd.to_datetime(df_cfi['KW data livrare']) == pd.to_datetime(df_cfi['KW data referinta']),
        pd.to_datetime(df_cfi['KW data livrare']) == pd.to_datetime(df_cfi['KW data referinta']+1)
    ]

    #define results
    results = ['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']

    #create new column based on conditions in column1 and column2
    df_cfi['Status_comanda'] = np.select(conditions, results)
    df_cfi['Status_comanda'] = df_cfi['Status_comanda'].apply(lambda x: 'IN TERMEN' if x == '0' else x)
    #df_cfi['Stoc minim'] = df_cfi['Stoc minim'].apply(lambda x: 'FARA STOC MINIM' if math.isnan(x) else x)
    df_cfi=df_cfi[['Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status_comanda', 'Furnizor', 'Nr comanda', 'Pozitie', 
    'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta',  'Data comenzii', 'Data livrare', 
    'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit']]
    df_cfi.drop_duplicates(subset=['Nr comanda', 'Pozitie'], inplace=True, ignore_index=True)
    df_cfi = df_cfi.sort_values('Zile intarziere',ascending=False)
    #data frame formated for display - create a copy because it may also change the column types and mess up further calculations
    df_formatted = df_cfi.copy(deep=True)
    df_formatted.drop(['Zi referinta'], axis=1, inplace=True)
    df_formatted = df_formatted.sort_values('Zile intarziere',ascending=False)
    #df_formatted.drop(['Zi referinta'])
    df_formatted['Stoc minim'] = df_formatted['Stoc minim'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Stoc minim'] = df_formatted['Stoc minim'].apply(lambda x: 'FARA STOC MINIM' if x=='nan' else x)
    df_formatted['Cantitate comanda'] = df_formatted['Cantitate comanda'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Cantitate restanta'] = df_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    #df_formatted['Zi referinta'] = df_formatted['Zi referinta'].dt.strftime('%d/%m/%Y')
    df_formatted['Data comenzii'] = df_formatted['Data comenzii'].dt.strftime('%d/%m/%Y')
    df_formatted['Data livrare'] = df_formatted['Data livrare'].dt.strftime('%d/%m/%Y')
    df_formatted['Cel mai vechi termen de livrare catre client'] = df_formatted['Cel mai vechi termen de livrare catre client'].dt.strftime('%d/%m/%Y')
    df_formatted.fillna(value={'Cel mai vechi termen de livrare catre client': "FARA COMANDA CLIENT", 'Client': " ", 'Stoc minim': "FARA STOC MINIM"}, inplace=True)
    
    df_cfi.fillna(value={'Cel mai vechi termen de livrare catre client': "FARA COMANDA CLIENT", 'Client': " ", 'Stoc minim': "FARA STOC MINIM"}, inplace=True)

    df_cfi_display=df_cfi.sort_values('Zile intarziere',ascending=False).head(10)
    
    if role=="admin":
        #[07]
        st.header("Status Comenzi Furnizori Intarziate")
        col5, col6 = st.columns((4,1))
        with col5:
            niceGrid(df_formatted)
        with col6:
            fig = px.pie(df_cfi_display, values='Zile intarziere', names='Nr comanda', title='Top 10 comenzi zile intarziere')
            st.plotly_chart(fig, use_container_width=True)


    #%%#########################################################

    ############## [08] Pt. CC O2N si situatie CF ordonat dupa data comenzii ###############
    #%%=======================================================
    #
    df_cfcc = df_cfi.copy(deep=True)
    df_cfcc['Pozitie'] = df_cfcc['Pozitie'].astype(float).astype(int).astype(str)
    df_cfcc['Cod PIO'] = df_cfcc['Cod Lingemann']



    df_ccf['Legatura_CF']=df_ccf['Numar intern comanda furnizor'].str.strip() + df_ccf['Numar pozitie'].astype(float).astype(int).astype(str).str.strip()
    df_cfcc['Legatura_CF']=df_cfcc['Nr comanda'].str.strip() + df_cfcc['Pozitie'].str.strip()
    #defineste key pentru join
    
    #df_cfcc1 = df_cfcc.join(df_ccf.set_index('Legatura CF'), on=['Legatura CF'], how='left', rsuffix='_df_ccf')
    df_cfcc = df_cfcc.join(df_ccf.set_index('Legatura_CF'), on='Legatura_CF',rsuffix='_df_ccf')
    df_cfcc.rename(columns={'Data iesire 1':'DC1', 'Data livrare 1':'TL1', 'Data iesire 2':'DC2', 'Data livrare 2':'TL2','Data iesire 3':'DC3', 'Data livrare 3':'TL3'}, inplace=True)
    df_cfcc.fillna(value={'DC1': pd.to_datetime("1990-01-01"), 'TL1': pd.to_datetime("1990-01-01"), 'DC2': pd.to_datetime("1990-01-01"), 'TL2': pd.to_datetime("1990-01-01"), 'DC3': pd.to_datetime("1990-01-01"), 'TL3': pd.to_datetime("1990-01-01")}, inplace=True)

    df_cfcc.drop(['Numar pozitie', 'Label', 'Nr. confirmare 1', 'Nr. confirmare 2','Nr. confirmare 3', 'Nr. poz. cod compus', 'Numar intern comanda furnizor', 'Legatura_CF'], axis=1, inplace=True)
    # pentru coloana Status
    df_cfcc['Status'] = 'FARA CONFIRMARE'
    for i, row in df_cfcc.iterrows():
        if pd.to_datetime(df_cfcc.at[i,'DC3'])>pd.to_datetime("1990-01-01"):
            df_cfcc.at[i,'Status']=df_cfcc.at[i,'DC3']
        else:
            if pd.to_datetime(df_cfcc.at[i,'DC2'])>pd.to_datetime("1990-01-01"):
                df_cfcc.at[i,'Status']=df_cfcc.at[i,'DC2']
            else:
                if pd.to_datetime(df_cfcc.at[i,'DC1'])>pd.to_datetime("1990-01-01"):
                    df_cfcc.at[i,'Status']=df_cfcc.at[i,'DC1']
                else:
                    df_cfcc.at[i,'Status'] = "FARA CONFIRMARE"

    #df_cfcc1.fillna(value={'Status': "FARA CONFIRMARE"}, inplace=True)
    #df_cfcc1['Status'] = np.where(df_cfcc1['Status']>pd.to_datetime("1900-01-01"), pd.to_datetime(df_cfcc1['Status']), 'FARA CONFIRMARE')
    
    df_cfcc['Data Confirmare CF'] = df_cfcc['Status']
    #df_cfcc1['Data Comenzii'] = df_cfcc['Data comenzii']
    #print(df_cfcc1.columns.to_list())
    df_cfcc = df_cfcc[['Cod PIO', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status_comanda', 'Furnizor','Nr comanda','Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta', 'Data comenzii',  'Data Confirmare CF', 'Data livrare', 'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit', 'Zi referinta']]
    
    df_cfcc.to_excel("output/Situatie Comenzi Furnizori Completa - neformatat.xlsx")
    df_cfcc.sort_values('Data comenzii', ascending = True, inplace=True)
    #st.write(df_cfcc)

    #daca e KA, am filtru suplimentar pe status
    
    
    #%%#########################################################

    ############## [09] RAPORT Stocuri minime - Comenzi Furnizori - cantitati restante ###############
    #%%=======================================================

    
    df_cfcc['Legatura Depozit'] = df_cfcc['Depozit'].str.strip() + df_cfcc['Cod PIO'].str.strip()
    rcf= pd.pivot_table(df_cfcc, values=['Nr comanda','Cantitate restanta'], index=['Legatura Depozit'], aggfunc={'Nr comanda' : 'count', 'Cantitate restanta' : 'sum'},
                                    fill_value='').reset_index(level=-1)
    #rcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
    rcf.loc['total']= rcf.sum(numeric_only=True)
    rcf = rcf.sort_values('Legatura Depozit')
    rcf_formatted = rcf.copy(deep=True)
    rcf_formatted['Cantitate restanta'] = rcf_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    #
    rcf.to_excel("output/Raport Comenzi Furnizori - Cantitati Restante.xlsx")
    #st.dataframe(rcf)

    pcf=pd.read_excel('output/Raport Comenzi Furnizori - Cantitati Restante.xlsx')
    pcf = pcf.dropna(subset=['Legatura Depozit'])
    rcf_todisplay=pcf.sort_values('Cantitate restanta',ascending=False).head(10)
    
    if role=="admin":
        #[09]
        st.header("Stocuri Minime - Comenzi Furnizori - cantitati restante")
        col5, col6 = st.columns((2,1))
        with col5:
            niceGrid(rcf_formatted)
        with col6:
            fig = px.pie(rcf_todisplay, values='Cantitate restanta', names='Legatura Depozit', title='Top 10 produse cu cantitati restante')
            st.plotly_chart(fig, use_container_width=True)


    #%%#############################################################

    ############## [10] Lucru CC - Comenzi clienti in raport cu ce am dp la furnizori ###############
    #%%=======================================================
    #
    df_ccd['Zi referinta'] =pd.to_datetime(data_referinta)
    df_ccd['KW data referinta'] = data_referinta.isocalendar().week
    df_ccd['An referinta'] = datetime.now().year
    df_ccd['KW data livrare'] = pd.to_datetime(df_ccd['Data livrare']).apply(lambda x: x.isocalendar().week if not pd.isnull(x) else 0)
    df_ccd['An livrare'] = pd.to_datetime(df_ccd['Data livrare']).apply(lambda x: x.year if not pd.isnull(x) else 0)
    df_ccd['Zile intarziere'] = (pd.to_datetime(df_ccd['Zi referinta'])-pd.to_datetime(df_ccd['Data livrare'])).apply(lambda x: x.days if not pd.isnull(x) else -1)
    df_ccd['Currency'] = df_ccd['Cod curs valutar']
    df_ccd['TIP TL'] = np.where(df_ccd['Cod termen livrare']=="B", "APROXIMATIV","FIX")

    df_ccd['Legatura']=df_ccd['Depozit'].str.strip() + df_ccd['Lieferartikel'].str.strip()
    df_cfcc['Legatura']=df_cfcc['Depozit'].str.strip() + df_cfcc['Cod PIO'].str.strip()
    #defineste key pentru join
    df_ccd = df_ccd.join(df_cfcc.set_index('Legatura'), on='Legatura', rsuffix='_df_cfcc1')
    df_ccd.sort_values(['Lieferartikel', 'Numar intern comanda client', 'Numar pozitie', 'Cod client'])
    df_ccd.drop_duplicates(subset=['Lieferartikel','Numar intern comanda client', 'Numar pozitie', 'Cod client'], inplace=True, ignore_index=True)
    #create index for join
    
    #replace Currency RON for empty values
    df_ccd.fillna(value={'Currency': "RON"}, inplace=True)
    df_ccd.fillna(value={'Furnizor': ""}, inplace=True)
    # fill new column "RESTRICTII"
    conditionsl = [
        df_ccd['Validare comanda client'] == "N",
        df_ccd['Validare generare dispozitie livrare'] == "N",
        np.isclose(df_ccd['Livrare partiala permisa 1=DA'].round(1), 0.0)
    ]
    #define results
    resultsl = ['ORDER RELEASE: NO', 'KOMMFREIGABE: NEIN', 'COMANDA SE LIVREAZA INTEGRAL']

    #create new column based on conditions in column1 and column2
    df_ccd['RESTRICTII'] = np.select(conditionsl, resultsl)
    df_ccd.fillna(value={'RESTRICTII': "FARA RESTRICTII"}, inplace=True)
    df_ccd['RESTRICTII'] = df_ccd['RESTRICTII'].apply(lambda x: x if x!='0' else 'FARA RESTRICTII')
    df_ccd.fillna(value={'Status_comanda': "INTARZIATE"}, inplace=True)

    df_ccd['Cea mai veche CF'] = df_ccd['Data comenzii']
    df_ccd.fillna(value={'Cea mai veche CF': "FARA CF"}, inplace=True)
    #df_lcc1['Data confirmare CF'] = df_lcc1['Status']
    df_ccd.fillna(value={'Data Confirmare CF': ""}, inplace=True)
    df_ccd['Data livrare CF'] = df_ccd['Data livrare_df_cfcc1']
    df_ccd.fillna(value={'Data livrare': ""}, inplace=True)

    #Calculate Status Comanda
    #=IF(YEAR(TODAY())>[@[Year livrare]],"INTARZIATE",IF(YEAR(TODAY())<[@[Year livrare]],"IN TERMEN",IF(ISOWEEKNUM(TODAY())>[@[KW livrare]],"INTARZIATE",IF(ISOWEEKNUM(TODAY())=[@[KW livrare]],"SAPTAMANA ASTA",IF(ISOWEEKNUM(TODAY())+1=[@[KW livrare]],"SAPTAMANA VIITOARE","IN TERMEN")))))
    df_ccd['Status_comanda']= "IN TERMEN"

    conditions = [
        pd.to_datetime(df_ccd['Zi referinta']) > pd.to_datetime(df_ccd['Data livrare']),
        pd.to_datetime(df_ccd['An livrare']) > pd.to_datetime(df_ccd['An referinta']),
        pd.to_datetime(df_ccd['KW data livrare']) == pd.to_datetime(df_ccd['KW data referinta']),
        pd.to_datetime(df_ccd['KW data livrare']) == pd.to_datetime(df_ccd['KW data referinta']+1)
    ]

    #define results
    results = ['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']

    #create new column based on conditions in column1 and column2
    df_ccd['Status_comanda'] = np.select(conditions, results)
    df_ccd['Status_comanda'] = df_ccd['Status_comanda'].apply(lambda x: 'IN TERMEN' if x == '0' else x)

    #rename columns
    df_ccd.drop(['Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'Cantitate comanda', 'Cantitate restanta_df_cfcc1', 'Depozit_df_cfcc1', 
    'Data livrare_df_cfcc1', 'Adresa contact', 'Zi referinta_df_cfcc1', 'KW data referinta', 'An referinta', 
    'Zile intarziere_df_cfcc1', 'Cel mai vechi termen de livrare catre client', 'Data comenzii', 'Client', 'Stoc minim', 'Cod PIO', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status'], axis=1, inplace=True)
    #'KW data livrare', 'An livrare', 
    df_ccd.rename(columns={'Grupa client':'Grup', 'NumeF':'Nume_client', 'Numar intern comanda client':'Nr. intern CC', 'Lieferartikel':'Cod produs', 
    'Text produs':'Denumire', 'Validare generare dispozitie livrare':'Se pot emite DL', 'Validare comanda client':'Order Release', 'Cod termen livrare':'Termen de livrare', 
    'Cantitate pozitie':'Cantitate comanda', 'Reprezentant principal':'Key Account', 'Data inregistrare':'Data creere', 'Cod curs valutar':'Moneda', 
    'Nr. comanda client':'NR. extern CC', '':'', 'Livrare partiala permisa 1=DA': 'Livrare integrala'}, inplace=True)
    #drop columns
    
    df_ccd = df_ccd.join(df_ka.set_index('Client'), on=['Nume_client'], how='left', rsuffix='_df_cfcc1')
    df_ccd.drop(['Grup_df_cfcc1', 'Nr comanda'], axis=1, inplace=True)
    df_ccd = df_ccd[['KW data livrare', 'An livrare', 'Zile intarziere', 'Furnizor', 'Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'KA', 
    'Currency', 'TIP TL', 'RESTRICTII','Status_comanda', 'Grup', 'Cod client', 'Nume_client', 'Nr. intern CC', 'Numar pozitie', 'Cod produs', 'Denumire', 'Tip comanda client',
    'Depozit', 'Se pot emite DL', 'Order Release', 'Termen de livrare', 'Data livrare', 'Cantitate comanda', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB in percents', 
    'Key Account', 'Data creere', 'Moneda', 'Livrare integrala', 'Unitate masura', 'Cod produs client', 'NR. extern CC', 'Data comanda client', 'Nr. comanda furnizor atribuit', 
    'Confirmare comanda furnizor', 'Persoana de contact', 'Zi referinta']]

    df_ccd.sort_values(by=['Zile intarziere'], ascending=False, inplace=True)
    #

    df_ccd_formatted = df_ccd.copy(deep=True)
    df_ccd_formatted['Cea mai veche CF'] = df_ccd_formatted['Cea mai veche CF'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CF') else x)
    df_ccd_formatted['Data Confirmare CF'] = df_ccd_formatted['Data Confirmare CF'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    df_ccd_formatted['Data livrare CF'] = df_ccd_formatted['Data livrare CF'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    df_ccd_formatted['Data livrare'] = df_ccd_formatted['Data livrare'].dt.strftime('%d/%m/%Y')
    df_ccd_formatted['Cantitate comanda'] = df_ccd_formatted['Cantitate comanda'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Cantitate livrata'] = df_ccd_formatted['Cantitate livrata'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Cantitate restanta'] = df_ccd_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Valoare restanta'] = df_ccd_formatted['Valoare restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['DB'] = df_ccd_formatted['DB'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['DB in percents'] = df_ccd_formatted['DB in percents'].apply(lambda x: "{:,.2f}".format(float(x)) if x!='undefiniert' else x).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_ccd_formatted['Data creere'] = df_ccd_formatted['Data creere'].dt.strftime('%d/%m/%Y')
    df_ccd_formatted['Data comanda client'] = df_ccd_formatted['Data comanda client'].dt.strftime('%d/%m/%Y')
    df_ccd_formatted['Zi referinta'] = df_ccd_formatted['Zi referinta'].dt.strftime('%d/%m/%Y')

    df_ccd.to_excel("output/de control/Lucru CC.xlsx")
    if role=="admin":
        #[10]
        st.header("Lucru CC - Comenzi clienti in raport cu ce am dp la furnizori")
        niceGrid(df_ccd_formatted)



    #%%#######################################################


    ############## [11] Status CC de copiat - Comenzile per key accounts si status ###############
    #%%=======================================================
    df_ccd.drop(['Zi referinta'], axis=1, inplace=True)
    df_ccd.fillna(value={'Furnizor': "None"}, inplace=True)
    df_ccd.fillna(value={'KA': "None Assigned"}, inplace=True)
    df_ccd.fillna(value={'Data livrare CF': " "}, inplace=True)
    df_ccd.fillna(value={'Data Confirmare CF': " "}, inplace=True)
       
    pivot_ccd = df_ccd.pivot_table(df_ccd[['Cantitate restanta', 'Valoare restanta']], index=['KA','Cod client', 'Nume_client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status_comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'Unitate masura', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor'], aggfunc=np.sum)
    
    pivot_ccd.reset_index(inplace=True)
    pivot_ccd.to_excel("output/de control/Status CC de copiat - pivot.xlsx", index=False)
    #st.write(groupedcc)
    #groupedccP.to_excel("output/Status CC de copiat var2.xlsx", index=False)

    pivot_statccF = pd.read_excel('output/de control/Status CC de copiat - pivot.xlsx')

    #daca e KA, am filtru suplimentar pe status
    # st.write(pivot_statccF)
    if (role=="admin") or (role=="ka") or (role=="achizitii") or (role=="full_access"):
        #[11]
        list_status=['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']
        list_whsUser = list(df_access.query('User==@username').groupby('Depozit').groups.keys())
        list_clientiUser = list(pivot_statccF.query('Depozit in @list_whsUser').groupby('Nume_client').groups.keys())
        list_furnizoriUser = list(pivot_statccF.query('Depozit in @list_whsUser').groupby('Furnizor').groups.keys())
        if role == "achizitii":
            # v01, v02= st.columns(2)
            # with v01:
            #     selectDepozit = st.multiselect("Depozite: ", options=list_whsUser, default=list_whsUser, label_visibility="collapsed", disabled=True)
            # with v02:
            #     selectStatus  = st.multiselect("Status: ", options=list_status, default=list_status, label_visibility="collapsed", disabled=True)
            # selectFurnizori = st.multiselect("Furnizori: ", options=list_furnizoriUser, default=list_furnizoriUser, label_visibility="collapsed", disabled=True)
            #pivot_statccF=pivot_statccF.query("Status_comanda == @selectStatus & Depozit == @selectDepozit & Furnizor == @selectFurnizori", disabled=True)
            pivot_statccF=pivot_statccF.query("Depozit in @list_whsUser & Furnizor in @list_furnizoriUser")
        else:
            if role == "ka":
                list_clientiUser = list(pivot_statccF.query('Depozit in @list_whsUser & KA == @username').groupby('Nume_client').groups.keys())
                list_furnizoriUser = list(pivot_statccF.query('Depozit in @list_whsUser & KA == @username').groupby('Furnizor').groups.keys())
                # ka01, ka02, ka03 = st.columns(3)
                # with ka01:
                #     selectDepozit = st.multiselect("Depozite: ", options=list_whsUser, default=list_whsUser, label_visibility="collapsed", disabled=True)
                # with ka02:
                #     selectClienti = st.multiselect("Clienti: ", options=list_clientiUser, default=list_clientiUser, label_visibility="collapsed", disabled=True)
                # with ka03:
                #     selectStatus  = st.multiselect("Status: ", options=list_status, default=list_status, label_visibility="collapsed", disabled=True)
                # selectFurnizori = st.multiselect("Furnizori: ", options=list_furnizoriUser, default=list_furnizoriUser, label_visibility="collapsed", disabled=True)
                #pivot_statccF=pivot_statccF.query("KA == @username & Status_comanda == @selectStatus & Depozit == @selectDepozit & Nume_client == @selectClienti & Furnizor == @selectFurnizori")
                pivot_statccF=pivot_statccF.query("KA == @username & Depozit in @list_whsUser & Nume_client in @list_clientiUser & Furnizor in @list_furnizoriUser")


    
        #########!!! Output Comenzi Furnizori Completa !!! add formatting #########
        pivot_statccF_formatted = pivot_statccF.copy(deep=True)
        pivot_statccF_formatted['Cea mai veche CF'] = pivot_statccF_formatted['Cea mai veche CF'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x)  and x!=' 'and x!='' and x!='FARA CF') else x)
        pivot_statccF_formatted['Data Confirmare CF'] = pivot_statccF_formatted['Data Confirmare CF'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!=''  and x!=' 'and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
        pivot_statccF_formatted['Data livrare CF'] = pivot_statccF_formatted['Data livrare CF'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!=' ' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
        pivot_statccF_formatted['Data livrare'] = pivot_statccF_formatted['Data livrare'].dt.strftime('%d/%m/%Y')
        pivot_statccF_formatted['Cantitate restanta'] = pivot_statccF_formatted['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
        pivot_statccF_formatted['Valoare restanta'] = pivot_statccF_formatted['Valoare restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
        pivot_statccF_formatted['Data creere'] = pivot_statccF_formatted['Data creere'].dt.strftime('%d/%m/%Y')

        if (role=="admin") or (role=="ka") or (role=="full_access"):
            st.header("Status Comenzi Clienti Completa")
            niceGrid(pivot_statccF_formatted)

    #########!!! Output Comenzi Furnizori Completa !!!#########
    if (role=="achizitii"):
        #[08] inlocuit KA cu achizitii on May 8th 
        #list_furnizoriUser = list(df_cfcc.groupby('Furnizor').groups.keys())
        #selectFurnizori = st.multiselect("Furmizori: ", options=list_furnizoriUser, default=list_furnizoriUser)
        df_cfcc=df_cfcc.query("Depozit in @list_whsUser")
        

    df_out_CF = df_cfcc.copy(deep=True)
    df_out_CF = df_out_CF[['Cod PIO', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status_comanda', 'Furnizor','Nr comanda','Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta', 'Data comenzii',  'Data Confirmare CF', 'Data livrare', 'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit']]

    #data frame formated for display - create a copy because it may also change the column types and mess up further calculations
    #.apply(lambda x: "{:,.2f}".format(float(x)) if x!='undefiniert' else x)
    df_out_CF['Stoc minim'] = df_out_CF['Stoc minim'].apply(lambda x: '{:,.2f}'.format(x).replace(",", "~").replace(".", ",").replace("~", ".") if x!='FARA STOC MINIM' else x)
    df_out_CF['Cantitate comanda'] = df_out_CF['Cantitate comanda'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_out_CF['Cantitate restanta'] = df_out_CF['Cantitate restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_out_CF['Status'] = df_out_CF['Status'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    #df_out_CF['Zi referinta'] = df_out_CF['Zi referinta'].dt.strftime('%d/%m/%Y')
    df_out_CF['DC1'] = pd.to_datetime(df_out_CF['DC1']).dt.strftime('%d/%m/%Y')
    df_out_CF['DC2'] = pd.to_datetime(df_out_CF['DC2']).dt.strftime('%d/%m/%Y')
    df_out_CF['DC3'] = pd.to_datetime(df_out_CF['DC3']).dt.strftime('%d/%m/%Y')
    df_out_CF['TL1'] = pd.to_datetime(df_out_CF['TL1']).dt.strftime('%d/%m/%Y')
    df_out_CF['TL2'] = pd.to_datetime(df_out_CF['TL2']).dt.strftime('%d/%m/%Y')
    df_out_CF['TL3'] = pd.to_datetime(df_out_CF['TL3']).dt.strftime('%d/%m/%Y')
    df_out_CF['Data comenzii'] = pd.to_datetime(df_out_CF['Data comenzii']).dt.strftime('%d/%m/%Y')
    df_out_CF['Data Confirmare CF'] = df_out_CF['Data Confirmare CF'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    df_out_CF['Data livrare'] = pd.to_datetime(df_out_CF['Data livrare']).dt.strftime('%d/%m/%Y')
    df_out_CF['Cel mai vechi termen de livrare catre client'] = df_out_CF['Cel mai vechi termen de livrare catre client'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    #df_out_CF = df_out_CF.sort_values(by=['Data comenzii'], inplace=True)
    df_out_CF.to_excel("output/Situatie Comenzi Furnizori Completa.xlsx")

    if (role=="admin") or (role=="achizitii") or (role=="full_access"):
        #[08] inlocuit KA cu achizitii on May 8th
        st.header("Situatie Comenzi Furnizori Completa")
        if (role=="admin"):
            niceGrid(df_out_CF)
        else: 
            df_out_CF=df_out_CF[['Status_comanda', 'Furnizor','Nr comanda','Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta', 'Data comenzii',  'Data Confirmare CF', 'Data livrare', 'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit']]
            niceGrid(df_out_CF)

    #%%#######################################################

    ############## [12] Verificare SM de copiat ###############
    #%%=======================================================

    df_stocmin.drop(['Label', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal'], axis=1, inplace=True)
    df_stocmin.rename(columns={'Cod produs':'Cod PIO', 'Stoc minim':'Stoc minim / depozit'}, inplace=True)
    
    # create index pentu join
    #df_stocmin.set_index('Depozit' ,'Cod produs')
    #df_cfcc.set_index('Depozit', 'Cod PIO')
    df_stocmin=df_stocmin.join(df_cfcc.set_index('Legatura'), on='Legatura',rsuffix='_df_cfcc1')
    
    df_stocmin.drop(['Nr comanda', 'Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM_df_cfcc1', 'Cantitate comanda', 'Cantitate restanta', 
    'Depozit_df_cfcc1', 'Adresa contact', 'Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Zile intarziere', 'Cel mai vechi termen de livrare catre client', 
    'Client', 'Stoc minim', 'Status_comanda', 'Cod PIO_df_cfcc1', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Data Confirmare CF'], axis=1, inplace=True)
    df_stocmin.fillna(value={'Data comenzii': ""}, inplace=True)
    df_stocmin.fillna(value={'Status': ""}, inplace=True)
    df_stocmin.fillna(value={'Data livrare': ""}, inplace=True)
    df_stocmin.fillna(value={'Furnizor': ""}, inplace=True)
    df_stocmin.sort_values(by=['Legatura', 'Cod PIO', 'Furnizor', 'Data comenzii'], inplace=True)
    df_stocmin.drop_duplicates(['Legatura', 'Cod PIO', 'Furnizor'], keep='first', inplace=True)
    df_stocmin.rename(columns={'Data comenzii':'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC', 'Status':'Data confirmare cea mai veche CF - din lucru supplier - status pt. CC', 'Data livrare':'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC', 'Furnizor':'Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'}, inplace=True)
    
    df_stocmin.to_excel("output/Stocmin.xlsx", index=False)
    
    # create index pentu join

    pcc['Legatura']=pcc['Depozit'].str.strip() + pcc['Lieferartikel'].str.strip()
    pcc.to_excel("output/pcc cu legatura.xlsx", index=False)
    df_stocmin=df_stocmin.join(pcc.set_index('Legatura'), on='Legatura', rsuffix='_pcc')
    df_stocmin.fillna(value={'Cantitate restanta': 0}, inplace=True)
    df_stocmin.rename(columns={'Cantitate restanta':'Cant deschisa in CC - din CC deschise'}, inplace=True)
    df_stocmin.to_excel("output/Stocmin - join pcc.xlsx", index=False)
   
    inner_join = pd.merge(df_stocmin, 
                      pcc, 
                      on ='Legatura', 
                      how ='left')
    inner_join.to_excel("output/Stocmin_pcc inner.xlsx", index=False)
    df_stocmin=df_stocmin.join(pcf.set_index('Legatura Depozit'), on='Legatura', rsuffix='_pcf')
    df_stocmin.fillna(value={'Cantitate restanta': 0}, inplace=True)
    df_stocmin.rename(columns={'Cantitate restanta':'Cantitate in CF - din CF deschise'}, inplace=True)
    df_stocmin.fillna(value={'Nr comanda': ""}, inplace=True)
    df_stocmin.rename(columns={'Nr comanda':'Numar CF deschise - din CF deschise'}, inplace=True)
    
    df_stock.set_index('Depozit' ,'Cod produs')
    df_stock['Legatura']=df_stock['Depozit'].str.strip() + df_stock['Cod produs'].str.strip()
    df_stocmin=df_stocmin.join(df_stock.set_index('Legatura'), on='Legatura', rsuffix='_pcf')
    
    df_stocmin.drop(['Depozit_pcf', 'Cod produs', 'Descriere', 'UM_pcf', 'Cant. Rezervata', 'Cantitate in Comenzi clienti','Cantitate in Comenzi furnizori', 'Categ. Pret vanzare',
    'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica',  'Categorie pret / descriere', 'Pret lista', 
    'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse'], axis=1, inplace=True)
    df_stocmin.fillna(value={'Stoc disponibil': 0}, inplace=True)
    df_stocmin.rename(columns={'Stoc disponibil':'Stoc disponibil / depozit'}, inplace=True)
    convert_dict ={'Medie zilnica an curent':np.float32, 'Stoc minim / depozit': np.float32, 'Medie lunara an curent':np.float32, 'Medie lunara an precedent':np.float32, 
    'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC':np.datetime64, 'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC':np.datetime64,
    'Cant deschisa in CC - din CC deschise': np.float32, 'Cantitate in CF - din CF deschise': np.float64,'Stoc disponibil / depozit': np.float32}
    df_stocmin = df_stocmin.astype(convert_dict)

    df_stocmin['Zile acoperite de stoc'] = np.where(df_stocmin['Medie zilnica an curent']!=0, 
    np.round((df_stocmin['Stoc disponibil / depozit']-df_stocmin['Cant deschisa in CC - din CC deschise'])/df_stocmin['Medie zilnica an curent']),"FARA RULAJ AN CURENT")

    df_stocmin['Zile pana la livrare CF'] = np.where(df_stocmin['Cantitate in CF - din CF deschise']!=0, 
    (pd.to_datetime(df_stocmin['data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC'])-pd.to_datetime(data_referinta)).apply(lambda x: x.days),-1000)

    df_stocmin['Status']=''
    for index in range(len(df_stocmin)): 
        if (df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index] > 0):
            if (df_stocmin['Stoc disponibil / depozit'].iloc[index] == 0):
                df_stocmin['Status'].iloc[index] = "00 - Produs cu CC si fara stoc"
            else: 
                if (df_stocmin['Stoc disponibil / depozit'].iloc[index] >= df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index]+df_stocmin['Stoc minim / depozit'].iloc[index]):
                    df_stocmin['Status'].iloc[index] = "10-SA acopera CC si SM"
                else: 
                    if (df_stocmin['Stoc disponibil / depozit'].iloc[index] >= df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index]):
                        df_stocmin['Status'].iloc[index] = "02-SA acopera CC dar nu acopera SM"
                    else:
                        df_stocmin['Status'].iloc[index] = "01-SA nu acopera CC"
        else:
            if (df_stocmin['Stoc disponibil / depozit'].iloc[index] >= df_stocmin['Stoc minim / depozit'].iloc[index]):
                df_stocmin['Status'].iloc[index] = "09-SA acopera SM"
            else: 
                if (df_stocmin['Stoc disponibil / depozit'].iloc[index] == 0):
                    if (df_stocmin['Zile pana la livrare CF'].iloc[index] < 0):
                        df_stocmin['Status'].iloc[index] = "03-Fara SA si CF intarziate sau fara CF"
                    else: 
                        df_stocmin['Status'].iloc[index] = "04-Fara SA si CF in termen"
                else:
                    df_stocmin['Status'].iloc[index] = "05- SA nu acopera SM - Verificare zile acoperite de stoc"


    df_stocmin = df_stocmin[['Depozit', 'Cod PIO', 'Descriere produs', 'UM', 'Stoc minim / depozit', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent', 'Cant deschisa in CC - din CC deschise', 'Stoc disponibil / depozit', 'Cantitate in CF - din CF deschise', 'Zile acoperite de stoc', 'Zile pana la livrare CF', 'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC', 'Numar CF deschise - din CF deschise', 'Data confirmare cea mai veche CF - din lucru supplier - status pt. CC', 'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC', 'Status', 'Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC']]
    
    #remove duplicates based on 'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC' - imi trebuie cea mai veche
    df_stocmin.sort_values(['Depozit', 'Cod PIO', 'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC'], inplace=True)
    df_stocmin.drop_duplicates(subset=['Depozit', 'Cod PIO'], keep="first", inplace=True)
    
    if (role=="achizitii") or (role=="ka"):
        #df_stocmin=df_stocmin.query("Depozit == @selectDepozit")
        df_stocmin=df_stocmin.query("Depozit in @list_whsUser")

    df_stocmin = df_stocmin.sort_values(['Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'])
    df_stocmin.to_excel("output/de control/Situatie SM final.xlsx")


    #########!!! Output Comenzi Furnizori Completa !!!#########
    
    df_out_SM = df_stocmin.copy(deep=True)
    df_out_SM = df_out_SM.sort_values(['Depozit','Cod PIO'])
    df_out_SM.to_excel("output/Situatie SM Completa.xlsx")

    df_formatted = df_out_SM.copy(deep=True)
    
    df_formatted['Stoc minim / depozit'] = df_formatted['Stoc minim / depozit'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Medie zilnica an curent'] = df_formatted['Medie zilnica an curent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Medie lunara an curent'] = df_formatted['Medie lunara an curent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Medie lunara an precedent'] = df_formatted['Medie lunara an precedent'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Cant deschisa in CC - din CC deschise'] = df_formatted['Cant deschisa in CC - din CC deschise'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Stoc disponibil / depozit'] = df_formatted['Stoc disponibil / depozit'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Cantitate in CF - din CF deschise'] = df_formatted['Cantitate in CF - din CF deschise'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    df_formatted['Data emitere cea mai veche CF  - din lucru supplier - status pt. CC'] = df_formatted['Data emitere cea mai veche CF  - din lucru supplier - status pt. CC'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CF') else x)
    df_formatted['Data confirmare cea mai veche CF - din lucru supplier - status pt. CC'] = df_formatted['Data confirmare cea mai veche CF - din lucru supplier - status pt. CC'].apply(lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)
    df_formatted['data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC'] = df_formatted['data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC'].apply(lambda x: x.strftime('%d/%m/%Y') if (not pd.isnull(x) and x!='' and x!='FARA CONFIRMARE' and x!='FARA COMANDA CLIENT') else x)

    if (role=="admin") or (role=="achizitii") or (role=="ka") or (role=="full_access"):
        #[12]
        st.header("Situatie Stocuri Minime Completa")
        niceGrid(df_formatted)
    ###########################################################
    #%%#######################################################

    ############## [13] Centralizator ###############
    #%%=======================================================
    pivot_centralizator = df_ccd.groupby(['Cod client', 'Nume_client', 'Status_comanda']).aggregate({'Valoare restanta':'sum'})
    pivot_centralizator.reset_index(inplace=True)
    pivot_centralizator.to_excel("output/Status comenzi clienti Centralizator.xlsx", index=False)
    #citeste-l inapoi ca sa-l poti afisa OK
    pivot_centralizator=pd.read_excel("output/Status comenzi clienti Centralizator.xlsx")
    pivot_centralizator['Valoare restanta'] = pivot_centralizator['Valoare restanta'].map('{:,.2f}'.format).str.replace(",", "~").str.replace(".", ",").str.replace("~", ".")
    
    # if (role=="admin") or (role=="full_access"):
    #     #[13]
    #     st.header("Centralizator comenzi clienti")
    #     niceGrid(pivot_centralizator)


    #%%##############################################################



#################### Sidebar for authentication ##########
st.sidebar.title('Authentication')
selectedOption = st.sidebar.selectbox('Main', ['', 'Login', 'Register User', 'Forgot password', 'Reset password', 'Update user information'])
if selectedOption == 'Login':
    current_user = check_user()
    st.session_state.sidebar_state = 'collapsed'
elif selectedOption == 'Register User':
    register_user()
    st.session_state.sidebar_state = 'collapsed'
elif selectedOption == 'Forgot password':
    forgot_password()
    st.session_state.sidebar_state = 'collapsed'
elif selectedOption == 'Reset password':
    reset_password()
    st.session_state.sidebar_state = 'collapsed'
elif selectedOption == 'Update user information':
    update_user_info()
    st.session_state.sidebar_state = 'collapsed'




