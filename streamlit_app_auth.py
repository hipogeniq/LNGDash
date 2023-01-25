# imports for needed packages
import streamlit as st  # 🎈 data web app development
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import streamlit_authenticator as stauth
import plotly as plotly 
import plotly.express as px # for simple plots like pie charts
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


#################### Update user info ########################
def update_user_info():
    try:
        if authenticator.update_user_details('Register user', preauthorization=False):
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)


#################### Register user ########################
def register_user():
    try:
        if authenticator.register_user('Register user', preauthorization=False):
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('User registered successfully')
    except Exception as e:
        st.error(e)

##################### Reset password #########################
def reset_password():
    try:
        username=""
        if authenticator.reset_password(username, 'Reset password'):
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('Password modified successfully')
    except Exception as e:
        st.error(e)

#################### Forgot password #########################
def forgot_password():
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
        if username_forgot_pw:
            with open('../config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('New password sent securely')
            # Random password to be transferred to user securely
        elif username_forgot_pw == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)
    

################### Check user autorization and role #######################
def check_user():
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
        mainpage(role)
    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] == None:
        st.warning('Please enter your username and password')
    
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
        columns_auto_size_mode=False,
        theme='alpine', #Add theme color to the table
        enable_enterprise_modules=True,
        height=400,
        width='50%',
        reload_data=False
    )

    data = grid_response['data']
    selected = grid_response['selected_rows'] 
    df = pd.DataFrame(selected)
    return df

#################### MAIN PAGE CONTENT ##########################################
def mainpage(role): 
 
    data_referinta = st.date_input("Data de referinta", value=pd.to_datetime("today"), max_value=pd.to_datetime("today"))
    # initializare datarames din fisiere
    df_ccd = pd.read_excel('input/002_Comenzi clienti deschise - lucru.xlsx', skipfooter=1)
    df_cfd = pd.read_excel('input/002_Comenzi furnizori deschise - lucru.xlsx',skiprows=1)
    df_ccf = pd.read_excel('input/002_Confirmari comenzi furnizori - incepand cu anul precedent.xlsx', skiprows=1)
    df_stock = pd.read_excel('input/002_Stock value_RO.xlsx', skiprows=1)
    df_stocmin = pd.read_excel('input/002_Stocuri minime dep. principale.xlsx', skiprows=1)
    df_ka = pd.read_excel('input/002_Clienti - KA.xlsx')

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


    if role=="admin": 
        st.header("Comenzi clienti deschise")
        niceGrid(df_ccd)
    #%%#############################################################

    ############## RAPORT SENIOR MANAGEMENT - Comenzi Clienti - cantitati restante  rcc ###############
    #%%=======================================================

    
    rcc= pd.pivot_table(df_ccd, values=['Cantitate restanta'], index=['Depozit','Lieferartikel'], 
                                    fill_value='').reset_index(level=-1)
    #rcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
    rcc.loc['total']= rcc.sum(numeric_only=True)
    #st.dataframe(rcc)
    #niceGrid(rcc)
    rcc.to_excel("output/Raport Comenzi Clienti - Cantitati Restante.xlsx")
    #niceGrid(pivot_cc.to_frame())
    pcc=pd.read_excel('output/Raport Comenzi Clienti - Cantitati Restante.xlsx')
    # adauga pie chart
    #pcc.sort_values('Cantitate restanta',ascending=False).head(10).plot(kind='pie', y='Cantitate restanta', autopct='%1.0f%%')
    pcc = pcc.dropna(subset=['Lieferartikel'])
    pcc=pcc.sort_values('Cantitate restanta',ascending=False).head(10)

    if (role=="admin") or (role=="manager"):
        st.header("RAPORT SENIOR MANAGEMENT - Comenzi Clienti - cantitati restante")
        col5, col6 = st.columns((1,1))
        with col5:
            niceGrid(rcc)
        with col6:
            fig = px.pie(pcc, values='Cantitate restanta', names='Lieferartikel', title='Top 10 produse cu cantitati restante')
            st.plotly_chart(fig, use_container_width=True)

    ##############################################################
    #
    #Ordoneaza comenzi clienti O2N
    df_ccd.columns = ['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Cod produs', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']
    df_ccd.sort_values(by='Data livrare', inplace=True)
    df_ccd = df_ccd[['Grupa client', 'Cod client', 'NumeF', 'Numar intern comanda client', 'Numar pozitie', 'Cod produs', 'Text produs', 'Tip comanda client', 'Depozit', 'Validare generare dispozitie livrare', 'Validare comanda client', 'Cod termen livrare', 'Data livrare', 'Cantitate pozitie', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 'Reprezentant principal', 'Data inregistrare', 'Cod curs valutar', 'Livrare partiala permisa 1=DA',	'Unitate masura', 'Cod produs client', 'Nr. comanda client', 'Data comanda client', 'Nr. comanda furnizor atribuit', 'Confirmare comanda furnizor', 'Persoana de contact']]
    
    if role=="admin":
        st.header("Comenzi clienti deschise - df_ccd")
        niceGrid(df_ccd)
    #%%#######################################################
    ############## Comenzi furnizori deschise  df_cfd ###############
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
    
    if role=="admin":
        st.header("Comenzi furnizori deschise - df_cfd")
        niceGrid(df_cfd)
    #%%#############################################################


    ############## Confirmari Comenzi Furnizori df_ccf ###############
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
    
    if role=="admin":
        st.header("Confirmari Comenzi Furnizori - df_ccf")
        niceGrid(df_ccf)

    #%%#############################################################


    ############## Valori stocuri df_stock ###############
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
    
    
    if role=="admin":
        st.header("Valori stocuri - df_stock")
        niceGrid(df_stock)
    #%%#############################################################


    ############## Stocuri Minime Depozite Principale df_stocmin ###############
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
    
    if role=="admin":
        st.header("Stocuri minime - df_stocmin")
        niceGrid(df_stocmin)
    #%%#############################################################


    ############## Status comenzi furnizori intarziat ###############
    #%%=======================================================
    
    df_cfi = df_cfd.copy(deep=True)
    df_cfi.drop(['Cod furnizor', 'Abgangs-Datum', 'Tip comanda furnizor', 'Pret manual', 'Cod curs valutar', 'Stoc disponibil', 'Confirmare rezervare', 
    'Confirmare comanda furnizor', 'Valoare comenda  furnizor', 'Data livrare dorita'], axis=1, inplace=True)
    df_cfi['Zi referinta'] = data_referinta
    df_cfi['KW data referinta'] = data_referinta.isocalendar().week
    df_cfi['An referinta'] = datetime.now().year
    df_cfi['KW data livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.isocalendar().week)
    df_cfi['An livrare'] = pd.to_datetime(df_cfi['Data livrare']).apply(lambda x: x.year)
    df_cfi['Zile intarziere'] = (pd.to_datetime(df_cfi['Zi referinta']) -pd.to_datetime(df_cfi['Data livrare'])).apply(lambda x: x.days)

    #define keys for join
    df_ccd.set_index('Depozit', 'Cod produs')
    df_cfi.set_index('Depozit', 'Cod produs')
    df_stocmin.set_index('Depozit', 'Cod produs')

    # join cu df_cco pt Data livrare('Cel mai vechi termen de livrare catre client') si NumeF('Client') dupa Legatura (CC) cu Legatura Depozit 
    df_cfi=df_cfi.join(df_ccd,rsuffix='_df_ccd')
    # join cu df_stocuriMinime pt Stoc minim('Stoc Minim') dupa Legatura (SM) cu Legatura Depozit  
    df_cfi = df_cfi.join(df_stocmin, rsuffix='_df_sm')


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
        pd.to_datetime(df_cfi['Zi referinta']) >= pd.to_datetime(df_cfi['Cel mai vechi termen de livrare catre client']),
        pd.to_datetime(df_cfi['An livrare']) > pd.to_datetime(df_cfi['An referinta']),
        pd.to_datetime(df_cfi['KW data livrare']) == pd.to_datetime(df_cfi['KW data referinta']),
        pd.to_datetime(df_cfi['KW data livrare']) == pd.to_datetime(df_cfi['KW data referinta']+1)
    ]

    #define results
    results = ['INTARZIATA', 'IN TERMEN', 'LIVRARE IN SAPTAMANA ACEASTA', 'LIVRARE SAPTAMANA URMATOARE']

    #create new column based on conditions in column1 and column2
    df_cfi['Status comanda'] = np.select(conditions, results)
    df_cfi.fillna(value={'Status comanda': "IN TERMEN"}, inplace=True)
    df_cfi=df_cfi[['Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status comanda', 'Furnizor', 'Nr comanda', 'Pozitie', 
    'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta',  'Data comenzii', 'Data livrare', 
    'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit']]
    #st.write(df_cfi)

    df_cfi_display=df_cfi.sort_values('Zile intarziere',ascending=False).head(10)
    
    if (role=="admin") or (role=="vanzari"):
        st.header("Status Comenzi Furnizori Intarziate")
        col5, col6 = st.columns((4,1))
        with col5:
            niceGrid(df_cfi)
        with col6:
            fig = px.pie(df_cfi_display, values='Zile intarziere', names='Nr comanda', title='Top 10 comenzi zile intarziere')
            st.plotly_chart(fig, use_container_width=True)


    #%%#########################################################

    ############## Pt. CC O2N si situatie CF ordonat dupa data comenzii ###############
    #%%=======================================================
    #
    df_cfcc = df_cfi.copy(deep=True)
    df_cfcc['Pozitie'] = df_cfcc['Pozitie'].astype(float).astype(int).astype(str)
    df_cfcc['Cod PIO'] = df_cfcc['Cod Lingemann']

    #defineste key pentru join
    df_ccf.set_index('Numar intern comanda furnizor', 'Numar pozitie')
    df_cfcc.set_index('Nr comanda', 'Pozitie')

    #df_cfcc1 = df_cfcc.join(df_ccf.set_index('Legatura CF'), on=['Legatura CF'], how='left', rsuffix='_df_ccf')
    df_cfcc = df_cfcc.join(df_ccf, rsuffix='_df_ccf')
    df_cfcc.rename(columns={'Data iesire 1':'DC1', 'Data livrare 1':'TL1', 'Data iesire 2':'DC2', 'Data livrare 2':'TL2','Data iesire 3':'DC3', 'Data livrare 3':'TL3'}, inplace=True)
    df_cfcc.fillna(value={'DC1': pd.to_datetime("1990-01-01"), 'TL1': pd.to_datetime("1990-01-01"), 'DC2': pd.to_datetime("1990-01-01"), 'TL2': pd.to_datetime("1990-01-01"), 'DC3': pd.to_datetime("1990-01-01"), 'TL3': pd.to_datetime("1990-01-01")}, inplace=True)

    df_cfcc.drop(['Numar pozitie', 'Label', 'Nr. confirmare 1', 'Nr. confirmare 2','Nr. confirmare 3', 'Nr. poz. cod compus', 'Numar intern comanda furnizor'], axis=1, inplace=True)
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
    df_cfcc = df_cfcc[['Cod PIO', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Status', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status comanda', 'Furnizor','Nr comanda','Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta', 'Data comenzii',  'Data Confirmare CF', 'Data livrare', 'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit', 'Zi referinta']]
    df_cfcc.sort_values(by=['Data comenzii'], inplace=True)
    #st.write(df_cfcc)

    #########!!! Output Comenzi Furnizori Completa !!!#########
    
    df_out_CF = df_cfcc.copy(deep=True)
    df_out_CF = df_out_CF[['Status comanda', 'Furnizor','Nr comanda','Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM', 'Cantitate comanda', 'Cantitate restanta', 'Data comenzii',  'Data Confirmare CF', 'Data livrare', 'Zile intarziere', 'Adresa contact', 'Cel mai vechi termen de livrare catre client', 'Client', 'Stoc minim', 'Depozit', 'Zi referinta']]
    df_out_CF.to_excel("output/Situatie Comenzi Furnizori Completa.xlsx")

    if (role=="admin") or (role=="vanzari"):
        st.header("Situatie Comenzi Furnizori Completa")
        niceGrid(df_out_CF)
    ###########################################################

    #%%#########################################################

    ############## RAPORT SENIOR MANAGEMENT - Comenzi Furnizori - cantitati restante ###############
    #%%=======================================================

    st.header("RAPORT SENIOR MANAGEMENT - Comenzi Furnizori - cantitati restante")

    #rcf=df_cfcc.groupby(['Depozit','Cod PIO'])
    #rcf=rcf.apply(lambda x: x) 
    #rcf=rcf.loc[:, ['Depozit','Cod PIO','Nr comanda','Cantitate restanta']]
    #rcf=rcf.groupby(['Depozit','Cod PIO']).agg({'Nr comanda': lambda x: len(x.unique()), 'Cantitate restanta':'sum'})
    #rcf.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
    rcf= pd.pivot_table(df_cfcc, values=['Nr comanda','Cantitate restanta'], index=['Depozit','Cod PIO'], aggfunc={'Nr comanda' : 'count', 'Cantitate restanta' : 'sum'},
                                    fill_value='').reset_index(level=-1)
    #rcc.sort_values(by='Cantitate restanta', ascending=False, inplace=True)
    rcf.loc['total']= rcf.sum(numeric_only=True)
    #
    rcf.to_excel("output/Raport Comenzi Furnizori - Cantitati Restante.xlsx")
    #st.dataframe(rcf)

    pcf=pd.read_excel('output/Raport Comenzi Furnizori - Cantitati Restante.xlsx')
    pcf = pcf.dropna(subset=['Cod PIO'])
    rcf_todisplay=pcf.sort_values('Cantitate restanta',ascending=False).head(10)
    
    if (role=="admin") or (role=="manager"):
        col5, col6 = st.columns((2,1))
        with col5:
            niceGrid(rcf)
        with col6:
            fig = px.pie(rcf_todisplay, values='Cantitate restanta', names='Cod PIO', title='Top 10 produse cu cantitati restante')
            st.plotly_chart(fig, use_container_width=True)


    #%%#############################################################

    ############## Lucru CC - Comenzi clienti in raport cu ce am dp la furnizori ###############
    #%%=======================================================
    #
    #df_lcc = df_ccd.copy(deep=True)
    df_ccd['Zi referinta'] =data_referinta
    df_ccd['KW livrare'] = pd.to_datetime(df_ccd['Data livrare']).apply(lambda x: x.isocalendar().week if not pd.isnull(x) else 0)
    df_ccd['Year livrare'] = pd.to_datetime(df_ccd['Data livrare']).apply(lambda x: x.year if not pd.isnull(x) else 0)
    df_ccd['Zile intarziere'] = (pd.to_datetime(df_ccd['Zi referinta'])-pd.to_datetime(df_ccd['Data livrare'])).apply(lambda x: x.days if not pd.isnull(x) else -1)
    df_ccd['Currency'] = df_ccd['Cod curs valutar']
    df_ccd['TIP TL'] = np.where(df_ccd['Cod termen livrare']=="B", "APROXIMATIV","FIX")

    #create index for join
    df_cfcc.set_index('Depozit', 'Cod PIO')
    df_ccd.set_index('Depozit', 'Cod produs')

    df_ccd = df_ccd.join(df_cfcc, rsuffix='_df_cfcc1')
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
    df_ccd.fillna(value={'Status Comanda': "INTARZIATE"}, inplace=True)

    df_ccd['Cea mai veche CF'] = df_ccd['Data comenzii']
    df_ccd.fillna(value={'Cea mai veche CF': "FARA CF"}, inplace=True)
    #df_lcc1['Data confirmare CF'] = df_lcc1['Status']
    df_ccd.fillna(value={'Data Confirmare CF': ""}, inplace=True)
    df_ccd['Data livrare CF'] = df_ccd['Data livrare']
    df_ccd.fillna(value={'Data livrare': ""}, inplace=True)
    #rename columns
    df_ccd.drop(['Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'Cantitate comanda', 'Cantitate restanta_df_cfcc1', 'Depozit_df_cfcc1', 
    'Data livrare_df_cfcc1', 'Adresa contact', 'Zi referinta_df_cfcc1', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 
    'Zile intarziere_df_cfcc1', 'Cel mai vechi termen de livrare catre client', 'Data comenzii', 'Client', 'Stoc minim', 'Cod PIO', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Status'], axis=1, inplace=True)
    df_ccd.rename(columns={'Grupa client':'Grup', 'NumeF':'Nume client', 'Numar intern comanda client':'Nr. intern CC', 'Lieferartikel':'Cod produs', 
    'Text produs':'Denumire', 'Validare generare dispozitie livrare':'Se pot emite DL', 'Validare comanda client':'Order Release', 'Cod termen livrare':'Termen de livrare', 
    'Cantitate pozitie':'Cantitate comanda', 'Reprezentant principal':'Key Account', 'Data inregistrare':'Data creere', 'Cod curs valutar':'Moneda', 
    'Nr. comanda client':'NR. extern CC', '':'', 'Livrare partiala permisa 1=DA': 'Livrare integrala'}, inplace=True)
    #drop columns
    df_ccd = df_ccd.join(df_ka.set_index('Client'), on=['Nume client'], how='left', rsuffix='_df_cfcc1')
    df_ccd.drop(['Grup_df_cfcc1', 'Nr comanda', 'Unitate masura'], axis=1, inplace=True)
    df_ccd = df_ccd[['KW livrare', 'Year livrare', 'Zile intarziere', 'Furnizor', 'Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'KA', 
    'Currency', 'TIP TL', 'RESTRICTII','Status comanda', 'Grup', 'Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'Cod produs', 'Denumire', 'Tip comanda client',
    'Depozit', 'Se pot emite DL', 'Order Release', 'Termen de livrare', 'Data livrare', 'Cantitate comanda', 'Cantitate livrata', 'Cantitate restanta', 'Valoare restanta', 'DB', 'DB%', 
    'Key Account', 'Data creere', 'Moneda', 'Livrare integrala', 'UM', 'Cod produs client', 'NR. extern CC', 'Data comanda client', 'Nr. comanda furnizor atribuit', 
    'Confirmare comanda furnizor', 'Persoana de contact', 'Zi referinta']]

    df_ccd.sort_values(by=['Zile intarziere'], ascending=False, inplace=True)
    #
    df_ccd.to_excel("output/de control/Lucru CC.xlsx")
    if role=="admin":
        st.header("Lucru CC - Comenzi clienti in raport cu ce am dp la furnizori")
        niceGrid(df_ccd)


    #%%#######################################################


    ############## Status CC de copiat - Comenzile per key accounts si status ###############
    #%%=======================================================

    #st.header("Comenzile per key accounts si status - se copiaza acum in excel in output folder")
    groupedcc = df_ccd.groupby(['KA','Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'UM', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor'], as_index=False).agg({'Cantitate restanta':'sum', 'Valoare restanta':'sum'})
    #groupedcc= pd.pivot_table(df_ccd, values=['Cantitate restanta', 'Valoare restanta'], index=['KA','Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'UM', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor'], aggfunc={'Cantitate restanta' : 'sum', 'Valoare restanta' : 'sum'}, fill_value='').reset_index(level=-1)
    # asta imi face transposed - intreresant... pot sa-i specific axis or something?
    #groupedccP = pd.pivot_table(df_ccd, columns=['KA','Cod client', 'Nume client', 'Nr. intern CC', 'Numar pozitie', 'NR. extern CC', 'Persoana de contact', 'Status comanda', 'RESTRICTII', 'Data creere', 'Data livrare', 'Depozit', 'Cod produs','Denumire', 'UM', 'Cod produs client', 'Zile intarziere','Cea mai veche CF', 'Data Confirmare CF', 'Data livrare CF', 'Furnizor'], aggfunc={'Cantitate restanta':'sum', 'Valoare restanta':'sum'}).transpose()
    groupedcc.loc['total']= groupedcc.sum(numeric_only=True)
    groupedcc.to_excel("output/de control/Status CC de copiat.xlsx", index=False)
    #st.write(groupedcc)
    #groupedccP.to_excel("output/Status CC de copiat var2.xlsx", index=False)

    pivot_statccF = pd.read_excel('output/de control/Status CC de copiat.xlsx')
    #########!!! Output Comenzi Furnizori Completa !!!#########
    
    df_out_SC = pivot_statccF.copy(deep=True)
    df_out_SC.to_excel("output/Status Comenzi Clienti Completa.xlsx")
    if (role=="admin") or (role=="vanzari"):
        st.header("Status Comenzi Clienti Completa")
        niceGrid(pivot_statccF)
    ###########################################################

    #%%#######################################################

    ############## Verificare SM de copiat ###############
    #%%=======================================================

    #st.header("Verificare SM de copiat")
    #df_smc = df_StocuriMinime.copy(deep=True)
    df_stocmin.drop(['Label', 'Unitate ambalare', 'Comanda minima', 'Cantitate luna precedenta', 'Cantitate an precedent', 'Cantitate an curent', 'Furnizor principal'], axis=1, inplace=True)
    df_stocmin.rename(columns={'Cod produs':'Cod PIO', 'Stoc minim':'Stoc minim / depozit'}, inplace=True)

    # create index pentu join
    df_stocmin.set_index('Depozit' ,'Cod produs')
    df_cfcc.set_index('Depozit', 'Cod PIO')
    df_stocmin=df_stocmin.join(df_cfcc, rsuffix='_df_cfcc1')

    #df_smc1=df_smc.join(df_cfcc1.set_index('Legatura depozit'), on=['Legatura'], how='left', rsuffix='_df_cfcc1')

    df_stocmin.drop(['Nr comanda', 'Pozitie', 'Cod Lingemann', 'Cod Furnizori / produs', 'Denumire produs', 'UM_df_cfcc1', 'Cantitate comanda', 'Cantitate restanta', 
    'Depozit_df_cfcc1', 'Adresa contact', 'Zi referinta', 'KW data referinta', 'An referinta', 'KW data livrare', 'An livrare', 'Zile intarziere', 'Cel mai vechi termen de livrare catre client', 
    'Client', 'Stoc minim', 'Status comanda', 'Cod PIO_df_cfcc1', 'DC1', 'TL1', 'DC2', 'TL2', 'DC3', 'TL3', 'Data Confirmare CF'], axis=1, inplace=True)
    df_stocmin.fillna(value={'Data comenzii': ""}, inplace=True)
    df_stocmin.fillna(value={'Status': ""}, inplace=True)
    df_stocmin.fillna(value={'Data livrare': ""}, inplace=True)
    df_stocmin.fillna(value={'Furnizor': ""}, inplace=True)
    df_stocmin.rename(columns={'Data comenzii':'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC', 'Status':'Data confirmare cea mai veche CF - din lucru supplier - status pt. CC', 'Data livrare':'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC', 'Furnizor':'Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'}, inplace=True)

    # create index pentu join
    df_stocmin.set_index('Depozit' ,'Cod produs')
    pcc.set_index('Depozit', 'Lieferartikel')

    df_stocmin=df_stocmin.join(pcc, rsuffix='_pcc')
    df_stocmin.fillna(value={'Cantitate restanta': 0}, inplace=True)
    df_stocmin.rename(columns={'Cantitate restanta':'Cant deschisa in CC - din CC deschise'}, inplace=True)

    df_stocmin.set_index('Depozit' ,'Cod produs')
    pcf.set_index('Depozit', 'Cod PIO')

    df_stocmin=df_stocmin.join(pcf, rsuffix='_pcf')
    df_stocmin.fillna(value={'Cantitate restanta': 0}, inplace=True)
    df_stocmin.rename(columns={'Cantitate restanta':'Cantitate in CF - din CF deschise'}, inplace=True)
    df_stocmin.fillna(value={'Nr comanda': ""}, inplace=True)
    df_stocmin.rename(columns={'Nr comanda':'Numar CF deschise - din CF deschise'}, inplace=True)

    df_stocmin.set_index('Depozit' ,'Cod produs')
    df_stock.set_index('Depozit' ,'Cod produs')
    df_stocmin=df_stocmin.join(df_stock, rsuffix='_pcf')
    df_stocmin.drop(['Depozit_pcf', 'Cod produs', 'Descriere', 'UM_pcf', 'Stoc disponibil', 'Cant. Rezervata', 'Cantitate in Comenzi clienti','Cantitate in Comenzi furnizori', 'Categ. Pret vanzare',
    'Pret mediu de achizitie', 'Valoare marfa disponibila', 'Valoare marfa fizica',  'Categorie pret / descriere', 'Pret lista', 
    'Data ultima iesire', 'Data ultima intrare', 'Furnizor principal', 'Grupa produse'], axis=1, inplace=True)
    df_stocmin.fillna(value={'Stoc fizic': 0}, inplace=True)
    df_stocmin.rename(columns={'Stoc fizic':'Stoc actual / depozit din stocuri'}, inplace=True)
    convert_dict ={'Medie zilnica an curent':np.float32, 'Stoc minim / depozit': np.float32, 'Medie lunara an curent':np.float32, 'Medie lunara an precedent':np.float32, 
    'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC':np.datetime64, 'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC':np.datetime64,
    'Cant deschisa in CC - din CC deschise': np.float32, 'Cantitate in CF - din CF deschise': np.float64,'Stoc actual / depozit din stocuri': np.float32}
    df_stocmin = df_stocmin.astype(convert_dict)

    df_stocmin['Zile acoperite de stoc'] = np.where(df_stocmin['Medie zilnica an curent']!=0, 
    np.round((df_stocmin['Stoc actual / depozit din stocuri']-df_stocmin['Cantitate in CF - din CF deschise'])/df_stocmin['Medie zilnica an curent']),"FARA RULAJ AN CURENT")

    df_stocmin['Zile pana la livrare CF'] = np.where(df_stocmin['Cantitate in CF - din CF deschise']!=0, 
    (pd.to_datetime(df_stocmin['data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC'])-pd.to_datetime(data_referinta)).apply(lambda x: x.days),-1000)

    df_stocmin['Status']=''
    for index in range(len(df_stocmin)): 
        if (df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index] > 0):
            if (df_stocmin['Stoc actual / depozit din stocuri'].iloc[index] == 0):
                df_stocmin['Status'].iloc[index] = "00 - Produs cu CC si fara stoc"
            else: 
                if (df_stocmin['Stoc actual / depozit din stocuri'].iloc[index] >= df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index]+df_stocmin['Stoc minim / depozit'].iloc[index]):
                    df_stocmin['Status'].iloc[index] = "10-SA acopera CC si SM"
                else: 
                    if (df_stocmin['Stoc actual / depozit din stocuri'].iloc[index] >= df_stocmin['Cant deschisa in CC - din CC deschise'].iloc[index]):
                        df_stocmin['Status'].iloc[index] = "02-SA acopera CC dar nu acopera SM"
                    else:
                        df_stocmin['Status'].iloc[index] = "01-SA nu acopera CC"
        else:
            if (df_stocmin['Stoc actual / depozit din stocuri'].iloc[index] >= df_stocmin['Stoc minim / depozit'].iloc[index]):
                df_stocmin['Status'].iloc[index] = "09-SA acopera SM"
            else: 
                if (df_stocmin['Stoc actual / depozit din stocuri'].iloc[index] == 0):
                    if (df_stocmin['Zile pana la livrare CF'].iloc[index] < 0):
                        df_stocmin['Status'].iloc[index] = "03-Fara SA si CF intarziate sau fara CF"
                    else: 
                        df_stocmin['Status'].iloc[index] = "04-Fara SA si CF in termen"
                else:
                    df_stocmin['Status'].iloc[index] = "05- SA nu acopera SM - Verificare zile acoperite de stoc"


    df_stocmin = df_stocmin[['Depozit', 'Cod PIO', 'Descriere produs', 'UM', 'Stoc minim / depozit', 'Medie zilnica an curent', 'Medie lunara an curent', 'Medie lunara an precedent', 'Cant deschisa in CC - din CC deschise', 'Stoc actual / depozit din stocuri', 'Cantitate in CF - din CF deschise', 'Zile acoperite de stoc', 'Zile pana la livrare CF', 'Data emitere cea mai veche CF  - din lucru supplier - status pt. CC', 'Numar CF deschise - din CF deschise', 'Data confirmare cea mai veche CF - din lucru supplier - status pt. CC', 'data livrare pt. cea mai veche CF - din lucru supplier - status pt. CC', 'Status', 'Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC']]
    #st.dataframe(df_smc4)
    #df_smc4_to_display=df_stocmin.copy(deep=True)
    #niceGrid(df_smc4_to_display)
    df_stocmin.sort_values(by=['Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'], ascending=False, inplace=True)
    df_stocmin.to_excel("output/de control/Situatie SM final.xlsx")


    #########!!! Output Comenzi Furnizori Completa !!!#########
    
    df_out_SM = df_stocmin.copy(deep=True)
    df_out_SM .sort_values(by=['Furnizor pt. cea mai veche CF- din lucru supplier - status pt. CC'], ascending=False, inplace=True)
    df_out_SM.to_excel("output/Situatie SM Completa.xlsx")
    
    if (role=="admin") or (role=="vanzari"):
        st.header("Situatie Stocuri Minime Completa")
        niceGrid(df_out_SM)
    ###########################################################


    
    pivot_centralizator = pivot_statccF.groupby(['Cod client', 'Nume client', 'Status comanda']).aggregate({'Valoare restanta':'sum'})
    pivot_centralizator.to_excel("output/Status comenzi clienti Centralizator.xlsx")
    #citeste-l inapoi ca sa-l poti afisa OK
    pivot_centralizator=pd.read_excel("output/Status comenzi clienti Centralizator.xlsx")
    
    
    if (role=="admin") or (role=="vanzari") or (role=="manager"):
        st.header("Centralizator comenzi clienti")
        niceGrid(pivot_centralizator)


 #%%##############################################################

#################### Sidebar for authentication ##########
st.sidebar.title('Authentication')
selectedOption = st.sidebar.selectbox('Main', ['', 'Login', 'Register User', 'Forgot password', 'Reset password', 'Update user information'])
if selectedOption == 'Login':
    check_user()
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
    #update_user_info()
    st.session_state.sidebar_state = 'collapsed'




