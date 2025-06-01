# -*- coding: utf-8 -*-
"""
Hoofdbestand voor het dashboard van hartgezondheid.
Initialiseert de data en zet de navigatiestructuur op.

@author: merli and sven
"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def detecteer_Rpieken(df, pct_drempel):
    """
    Detecteert R-pieken in het ECG signaal.
    
    Parameters:
    - df: DataFrame met ECG data
    - pct_drempel: Percentage van maximale ECG waarde als drempel
    
    Returns:
    - df_pieken: DataFrame met alleen de gedetecteerde R-pieken
    """
    max_ecg = max(df['ECG'])
    drempelwaarde = pct_drempel * max_ecg
    pieken = find_peaks(df['ECG'], height=drempelwaarde)[0]
    df_pieken = df.iloc[pieken]
    return df_pieken

def initialize_data(uploaded_file=None):
    """
    Initialiseert alle benodigde data voor het dashboard.
    Laadt de ruwe data en berekent afgeleide waarden.
    Slaat alles op in de Streamlit session state.
    """
    if 'data_initialized' not in st.session_state:
        # Definieer tijdstippen van verschillende activiteiten (in seconden)
        st.session_state.start_meting = 0
        st.session_state.start_lopen = 120
        st.session_state.schoenen_aandoen = 240
        st.session_state.lopen = 360
        st.session_state.hond_uitlaten = 420
        st.session_state.start_herstellen = 2160
        st.session_state.weer_lopen = 3360
        st.session_state.zitten = 4020
        st.session_state.alweer_lopen = 6000
        st.session_state.start_traplopen = 6480
        st.session_state.zittend_herstellen = 6780
        st.session_state.einde_meting = 7320

        # Drempelwaarde voor R-piek detectie
        st.session_state.rpieken_drempel = 0.6  # Aan te passen naar eigen inzicht
        
        # Maak lijst van tijdsintervallen voor activiteiten
        st.session_state.intervallen = [
            st.session_state.start_meting, st.session_state.start_lopen, 
            st.session_state.schoenen_aandoen, st.session_state.lopen,
            st.session_state.start_herstellen, st.session_state.weer_lopen, 
            st.session_state.zitten, st.session_state.alweer_lopen,
            st.session_state.start_traplopen, st.session_state.zittend_herstellen, 
            st.session_state.einde_meting
        ]

        # Labels voor de verschillende activiteiten
        st.session_state.activiteiten = [
            'zitten', 'lopen', 'schoenen aandoen', 'lopen',
            'zitten', 'lopen', 'zitten', 'lopen', 'traplopen', 'zitten'
        ]

        # Kleuren voor visualisatie van activiteiten
        st.session_state.activiteiten_kleuren = {
            'zitten': 'blue',
            'lopen': 'green',
            'schoenen aandoen': 'purple',
            'traplopen': 'red'
        }

        try:
            # Laad ruwe data en bereken tijdstempels
            if uploaded_file is not None:
                df_ecg = pd.read_csv(uploaded_file, delimiter=',', skipinitialspace=True)
            else:
                df_ecg = pd.read_csv("data Sanne.txt", delimiter=',', skipinitialspace=True)
                
            df_ecg['timestamp'] = (df_ecg['time'] - df_ecg['time'].iloc[0])/1024  # Converteer naar seconden
            df_ecg['activiteit'] = pd.cut(df_ecg['timestamp'], bins=st.session_state.intervallen, 
                                         labels=st.session_state.activiteiten, ordered=False)

            # Detecteer R-pieken en bereken hartslag-gerelateerde waarden
            df_ecg_pieken = detecteer_Rpieken(df_ecg, st.session_state.rpieken_drempel)
            df_ecg_pieken['rr'] = df_ecg_pieken['timestamp'].diff()  # RR-intervallen
            df_ecg_pieken['bpm'] = 60 / df_ecg_pieken['rr']  # Hartslag in slagen per minuut
            df_ecg_pieken['gemiddelde_tijd'] = df_ecg_pieken['timestamp'].rolling(window=2).mean()
            df_ecg_pieken = df_ecg_pieken[df_ecg_pieken['rr'].notna()]  # Verwijder NaN waarden

            # Sla bewerkte data op in session state
            st.session_state.df_ecg = df_ecg
            st.session_state.df_ecg_pieken = df_ecg_pieken
            st.session_state.data_initialized = True
            
            return True
        except Exception as e:
            st.error(f"Er is een fout opgetreden bij het laden van het bestand: {str(e)}")
            return False

def homepage():
    """
    Zet de hoofdpagina van het dashboard op.
    Initialiseert de data en toont basis informatie.
    """
    st.set_page_config(page_title="Dashboard hart gezondheid", layout="wide")
    st.title('Dashboard hart gezondheid')
    
    # Sidebar voor gebruikersinformatie en bestandsupload
    with st.sidebar:
        st.header("Dashboard Instellingen")
        
        # Leeftijd input
        if 'user_age' not in st.session_state:
            st.session_state.user_age = 25  # Default waarde
            
        st.session_state.user_age = st.number_input(
            "Wat is uw leeftijd?",
            min_value=1,
            max_value=120,
            value=st.session_state.user_age,
            help="Uw leeftijd wordt gebruikt voor het berekenen van hartslagzones"
        )
        
        st.divider()
        
        # Bestandsupload sectie
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload uw sensordata bestand",
            type=['csv', 'txt'],
            help="Upload een .csv of .txt bestand met uw sensorgegevens"
        )
        
        if uploaded_file is not None:
            if initialize_data(uploaded_file):
                st.success("✅ Data succesvol geladen!")
            else:
                st.error("❌ Er is iets misgegaan bij het laden van het bestand. Controleer of het bestand het juiste formaat heeft.")
        else:
            if initialize_data():
                st.info("ℹ️ Standaard voorbeelddata geladen. Upload uw eigen data voor persoonlijke analyse.")
    
    # Hoofdinhoud
    st.subheader("Welkom bij uw Hartgezondheid Dashboard")
    st.write("""Dit interactieve dashboard is ontwikkeld om inzicht te geven in uw hartgezondheid 
             op basis van gegevens die zijn verzameld met een draagbare sensor. 
             De sensor registreert onder andere ECG-signalen, beweging en temperatuur. 
             Door deze data te analyseren, worden parameters zoals hartslagvariabiliteit (HRV), 
             stressniveaus en fysieke activiteit in kaart gebracht.
             """)
    # Instructies en uitleg
    st.markdown("""
    ###  Hoe gebruikt u dit dashboard?
    
    1. **Start met uploaden:**
       - Upload uw sensordata via het menu aan de linkerkant
       - Ondersteunde formaten: .csv of .txt bestanden
       - Het bestand moet de volgende kolommen bevatten:
         * `time` - tijdstempel
         * `ECG` - ECG-signaal
         * `accX`, `accY`, `accZ` - versnellingsdata
    
    2. **Vul uw gegevens in:**
       - Geef uw leeftijd op voor nauwkeurige hartslagzoneberekeningen
    
    3. **Kies uw weergave:**
       - **Beginner**: Eenvoudige weergave met basis hartgezondheidsmetrieken
       - **Geavanceerd**: Gedetailleerde analyses en extra grafieken
    """)
             
    st.subheader("Wat kunt u hier doen?")   
    st.write("""
    - Bekijk uw hartactiviteit in real-time of per meetmoment.
    - Analyseer stressniveaus aan de hand van HRV-berekeningen zoals RMSSD en SDNN.
    - Volg uw bewegingen zoals stappen, traplopen en herstelmomenten.
    - Visualiseer trends in hartfunctie gekoppeld aan dagelijkse activiteiten.
    
    Het doel van dit dashboard is om u te ondersteunen bij het verkrijgen van meer grip
    op uw gezondheid. Door patronen in inspanning en herstel te herkennen, 
    kunt u beter begrijpen hoe uw lichaam reageert op stress en beweging.
    """)
    
    st.write("Kies of u de beginner versie of de geavanceerde versie wilt met de knoppen hieronder.")
    st.write("U kunt de keuze altijd nog veranderen in de sidebar")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Beginner"):
            st.switch_page("pages/beginner.py")
    with col2:
        if st.button("Geavanceerd"):
            st.switch_page("pages/Advanced.py")
    
    # Disclaimer onderaan de pagina
    st.divider()
    st.caption("""
    **Disclaimer**: Dit dashboard is bedoeld als hulpmiddel ter ondersteuning van uw leefstijl.
    Raadpleeg altijd een arts bij gezondheidsklachten of medische vragen.
    """)

pages = {
    "Home": [
        st.Page(homepage, title="Home pagina")],
    "subpaginas": [
        st.Page("pages/beginner.py", title="Beginner"),
        st.Page("pages/Advanced.py", title="Geavanceerd"),
        st.Page("pages/info.py", title="Informatie"),
    ],
}

# Start de navigatie
pg = st.navigation(pages)
pg.run()
    

