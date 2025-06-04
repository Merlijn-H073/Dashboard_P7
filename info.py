# -*- coding: utf-8 -*-
"""
Informatiepagina voor het hartgezondheid dashboard.
Biedt gedetailleerde uitleg over alle functionaliteiten en berekeningen.

@author: merli and sven
"""
import streamlit as st
import plotly.graph_objects as go

def info_page():
    st.set_page_config(page_title="Dashboard Informatie", layout="wide")
    st.title("Informatie over het Dashboard")

    # Inhoudsopgave
    st.sidebar.header("Inhoudsopgave")
    page = st.sidebar.radio("Ga naar:", [
        "Algemene Informatie",
        "Data & Metingen",
        "Hartslagvariabiliteit (HRV)",
        "Bewegingsintensiteit",
        "Stappenteller",
        "Technische Details"
    ])

    if page == "Algemene Informatie":
        st.header("Algemene Informatie")
        
        st.subheader("Over het Dashboard")
        st.write("""
        Dit dashboard is ontwikkeld om inzicht te geven in uw hartgezondheid en bewegingspatronen. 
        Het verwerkt gegevens van een draagbare sensor die verschillende fysiologische signalen meet:
        - ECG (elektrocardiogram)
        - Beweging (accelerometer)
        - Temperatuur
        
        Het dashboard biedt twee weergaven:
        1. **Beginner**: Eenvoudige visualisaties van de belangrijkste gezondheidsmetrieken
        2. **Geavanceerd**: Uitgebreidere analyses en meer gedetailleerde grafieken
        """)

        st.subheader("Hoe te Gebruiken")
        st.write("""
        1. **Voorbereiding**:
           - Doe een meting met de hartslagsensor
           - Exporteer de data naar een .csv of .txt bestand
           - Upload het bestand via het menu in de zijbalk
        
        2. **Persoonlijke Instellingen**:
           - Vul uw leeftijd in voor nauwkeurige hartslagzoneberekeningen
           - De leeftijd wordt gebruikt in de Karvonen-formule voor het bepalen van trainingsintensiteit
        
        3. **Navigatie**:
           - Gebruik de knoppen voor Beginner of Geavanceerd
           - Bekijk verschillende grafieken en analyses
           - Gebruik de uitleg bij elke grafiek voor interpretatie
        """)

    elif page == "Data & Metingen":
        st.header("Data & Metingen")
        
        st.subheader("Sensorgegevens")
        st.write("""
        De sensor verzamelt verschillende soorten data:
        
        **ECG-signaal**:
        - Elektrische activiteit van het hart
        - Sampling rate: 1024 Hz
        - Gebruikt voor het detecteren van hartslagen en HRV-analyse
        
        **Bewegingsdata (Accelerometer)**:
        - Driedimensionale bewegingsdetectie (X, Y, Z-as)
        - Gebruikt voor activiteitsherkenning en stappentelling
        - Helpt bij het bepalen van bewegingsintensiteit
        """)

        st.subheader("Dataverwerking")
        st.write("""
        Het dashboard voert verschillende verwerkingsstappen uit:
        
        1. **Voorbewerking**:
           - Tijdsynchronisatie
           - Ruisfiltering
           - Normalisatie van signalen
        
        2. **Feature Extractie**:
           - R-piek detectie in ECG
           - Berekening van RR-intervallen
           - Bewegingspatroonherkenning
        
        3. **Analyse**:
           - HRV-berekeningen (RMSSD, SDNN)
           - Activiteitsclassificatie
           - Stressniveaubepaling
        """)

    elif page == "Hartslagvariabiliteit (HRV)":
        st.header("Hartslagvariabiliteit (HRV)")
        
        st.subheader("Wat is HRV?")
        st.write("""
        Hartslagvariabiliteit (HRV) is de variatie in tijd tussen opeenvolgende hartslagen. 
        Het is een belangrijke indicator voor:
        - Autonome zenuwstelsel functie
        - Stressniveau
        - Herstel en adaptatie
        - Algemene gezondheid
        """)

        st.subheader("HRV Metrieken")
        st.write("""
        Het dashboard gebruikt twee belangrijke HRV-metrieken:
        
        **1. RMSSD (Root Mean Square of Successive Differences)**
        - Maat voor korte-termijn HRV
        - Indicator voor parasympathische activiteit
        - Interpretatie:
          * Hoge waarden: Goed herstel, lage stress
          * Lage waarden: Verhoogde stress, verminderd herstel
        
        **2. SDNN (Standard Deviation of NN intervals)**
        - Maat voor totale HRV
        - Weerspiegelt alle cyclische componenten
        - Interpretatie:
          * Hoge waarden: Goede aanpassingscapaciteit
          * Lage waarden: Verminderde hartflexibiliteit
        """)

        st.subheader("Stressscore Berekening")
        st.write("""
        De stressscore wordt berekend op basis van HRV-waarden:
        1. Normalisatie van RMSSD-waarden
        2. Omzetting naar 0-100 schaal
        3. Inverse relatie met stress:
           - Lage HRV = Hoge stressscore
           - Hoge HRV = Lage stressscore
        """)

    elif page == "Bewegingsintensiteit":
        st.header("Bewegingsintensiteit")
        
        st.subheader("Intensiteitsberekening")
        st.write("""
        De bewegingsintensiteit wordt bepaald door een combinatie van:
        
        **1. Hartslag Zones (Karvonen formule)**
        - Berekend met de Karvonen formule:
            - Doelhartslag = Rusthartslag + (HRR × percentage)
            - HRR = max_HR - rust_HR
            - met:
                - HRR = Heart Rate Reserve (het verschil tussen de maximale hartslag en de rusthartslag)
                - max_HR = de maximale hartslag (220 - leeftijd)
                - rust_HR = de hartslag in rust (5e percentiel van alle hartslagwaarden)
        - Gebruikt persoonlijke leeftijd uit het profiel
        - Zones:
          * Rust: < 45% van HRR
          * Matig: 45-70% van HRR
          * Intensief: > 70% van HRR
        
        **2. Bewegingsdata**
        - Gebaseerd op versnellingsmetingen
        - Drempelwaarden:
          * Matig: > 60e percentiel van alle bewegingsdata
          * Intensief: > 80e percentiel van alle bewegingsdata
        
        **Eindclassificatie**
        De uiteindelijke intensiteit wordt bepaald door de combinatie van hartslag en beweging:
        - Intensief (telt 2x): Beide metingen intensief
        - Matig (telt 1x): 
          * Één meting intensief en andere matig/rust, OF
          * Beide metingen matig
        - Rust: Alle andere combinaties
        """)

        st.subheader("WHO Richtlijnen")
        st.write("""
        Het dashboard volgt de WHO-richtlijnen voor beweging:
        
        **Dagelijks doel: 30 intensiteitsminuten**
        - 30 minuten matige intensiteit OF
        - 15 minuten hoge intensiteit
        - Hoge intensiteit telt dubbel
        
        **Voorwaarden**:
        - Minimaal 10 minuten aaneengesloten activiteit
        - Combinatie van hartslag en beweging
        """)

    elif page == "Stappenteller":
        st.header("Stappenteller")
        
        st.subheader("Stapdetectie")
        st.write("""
        De stappenteller werkt via een geavanceerd algoritme:
        
        **1. Signaalverwerking**
        - Combinatie van X, Y, Z versnellingsdata
        - Berekening van totale versnellingsmagnitude
        - Ruisfiltering en normalisatie
        
        **2. Stapdetectie**
        - Piekdetectie in versnellingssignaal
        - Adaptieve drempelwaarde
        - Minimale tijd tussen stappen
        
        **3. Validatie**
        - Activiteitscontext
        - Bewegingspatroonherkenning
        - Filtering van valse detecties
        """)

        st.subheader("Activiteitsniveaus")
        st.write("""
        **Dagelijks stappendoel: 10.000 stappen**
        
        Classificatie van activiteitsniveaus:
        - Nauwelijks actief: < 5.000 stappen
        - Licht actief: 5.000-7.499 stappen
        - Redelijk actief: 7.500-9.999 stappen
        - Actief: 10.000-12.499 stappen
        - Zeer actief: ≥ 12.500 stappen
        """)

    elif page == "Technische Details":
        st.header("Technische Details")
        
        st.subheader("Belangrijke Functies")
        st.write("Het dashboard gebruikt verschillende functies voor de analyse van hartslag- en bewegingsdata:")

        st.subheader("1. R-piek Detectie")
        st.write("**Functie: `detecteer_Rpieken(df, pct_drempel)`**")
        st.code('''def detecteer_Rpieken(df, pct_drempel):
    max_ecg = max(df['ECG'])
    drempelwaarde = pct_drempel * max_ecg
    pieken = find_peaks(df['ECG'], height=drempelwaarde)[0]
    return df.iloc[pieken]''', language='python')
        
        st.write("""
        **Doel**: Detecteert de R-pieken in het ECG-signaal, wat essentieel is voor hartslaganalyse.
        
        **Parameters**:
        - `df`: DataFrame met ECG-data
        - `pct_drempel`: Percentage van maximale ECG-waarde als drempel (meestal 0.6 of 60%)
        
        **Werking**:
        1. Bepaalt maximale ECG-waarde in het signaal
        2. Berekent drempelwaarde als percentage van maximum
        3. Gebruikt scipy's `find_peaks` voor piekdetectie
        4. Retourneert alleen de datapunten met R-pieken
        """)

        st.subheader("2. HRV Berekeningen")
        st.write("**Functie: `bereken_rmssd(df)`**")
        st.code('''def bereken_rmssd(df):
    rmssd = np.sqrt(np.mean(np.square(np.diff(df['rr'])))) * 100
    return rmssd''', language='python')
        
        st.write("""
        **Doel**: Berekent de Root Mean Square of Successive Differences (RMSSD) van RR-intervallen.
        
        **Parameters**:
        - `df`: DataFrame met RR-intervallen
        
        **Werking**:
        1. Berekent verschillen tussen opeenvolgende RR-intervallen (`np.diff`)
        2. Kwadreert deze verschillen (`np.square`)
        3. Neemt het gemiddelde (`np.mean`)
        4. Berekent de wortel (`np.sqrt`)
        5. Vermenigvuldigt met 100 voor betere leesbaarheid
        """)

        st.subheader("3. SDNN Berekening")
        st.write("**Functie: `bereken_sdnn(df)`**")
        st.code('''def bereken_sdnn(df):
    sdnn = np.std(df['rr'], ddof=1) * 1000
    return sdnn''', language='python')
        
        st.write("""
        **Doel**: Berekent de Standard Deviation of NN (Normal-to-Normal) intervals.
        
        **Parameters**:
        - `df`: DataFrame met RR-intervallen
        
        **Werking**:
        1. Berekent standaarddeviatie van RR-intervallen
        2. Gebruikt ddof=1 voor sample standard deviation
        3. Converteert naar milliseconden (×1000)
        """)

        st.subheader("4. Stappenteller Algoritme")
        st.write("**Functie: `bereken_stappenteller(df, intervallen, activiteiten, drempel)`**")
        st.code('''def bereken_stappenteller(df, intervallen, activiteiten, drempel=0.5):
    df = df.copy()
    df['samengesteld_signaal'] = np.sqrt(df['accX']**2 + df['accY']**2 + df['accZ']**2)
    df['genormaliseerd'] = df['samengesteld_signaal'] - df['samengesteld_signaal'].mean()
    
    # Stap detectie per activiteit
    stappen_dfs = []
    for activiteit in activiteiten:
        df_filt = df[df['activiteit'] == activiteit]
        if df_filt.empty:
            continue
        pieken = find_peaks(df_filt['genormaliseerd'],
                          height=df_filt['genormaliseerd'].max() * drempel,
                          distance=10)[0]
        stappen_dfs.append(df_filt.iloc[pieken])
    
    return df, stappen_index''', language='python')
        
        st.write("""
        **Doel**: Detecteert stappen op basis van versnellingsdata.
        
        **Parameters**:
        - `df`: DataFrame met versnellingsdata
        - `intervallen`: Tijdsintervallen voor activiteiten
        - `activiteiten`: Labels voor verschillende activiteiten
        - `drempel`: Gevoeligheid voor stapdetectie (default: 0.5)
        
        **Werking**:
        1. Berekent totale versnellingsmagnitude uit X, Y, Z componenten
        2. Normaliseert het signaal
        3. Detecteert pieken per activiteit
        4. Past minimale afstand tussen stappen toe
        5. Combineert resultaten tot stappentelling
        """)

        st.subheader("5. Intensiteitsberekening")
        st.write("**Functie: `berekenen_intensiteit(df_acc, df_bpm, resolutie=60)`**")
        st.code('''def berekenen_intensiteit(df_acc, df_bpm, resolutie=60):
    # Bereken hartslagzones
    max_hr = 220 - st.session_state.user_age
    hrr = max_hr - resting_hr
    moderate_hr = resting_hr + (hrr * 0.45)
    vigorous_hr = resting_hr + (hrr * 0.70)
    
    # Classificatie logica
    df_blok['intensiteit'] = np.where(
        ((df_blok['hr_intensity'] == 2) & (df_blok['acc_intensity'] == 2)),
        2,  # Intensief
        np.where(
            ((df_blok['hr_intensity'] == 2) & (df_blok['acc_intensity'] >= 1)) |
            ((df_blok['hr_intensity'] >= 1) & (df_blok['acc_intensity'] == 2)) |
            ((df_blok['hr_intensity'] == 1) & (df_blok['acc_intensity'] == 1)),
            1,  # Matig
            0   # Rust
        )
    )
    return df_blok, total_intensity_minutes''', language='python')
        
        st.write("""
        **Doel**: Bepaalt bewegingsintensiteit op basis van hartslag en versnelling.
        
        **Parameters**:
        - `df_acc`: DataFrame met versnellingsdata
        - `df_bpm`: DataFrame met hartslagdata
        - `resolutie`: Tijdsblok in seconden (default: 60)
        
        **Werking**:
        1. Berekent hartslagzones met Karvonen-formule
        2. Bepaalt intensiteitsniveaus voor hartslag en beweging
        3. Combineert beide metingen voor eindclassificatie
        4. Past WHO-richtlijnen toe (10+ min aaneengesloten)
        5. Berekent totale intensiteitsminuten
        """)

        st.subheader("6. HRV Gauge Visualisatie")
        st.write("**Functie: `visualize_gauge(rmssd, gemiddelde_rmssd)`**")
        st.code('''def visualize_gauge(rmssd, gemiddelde_rmssd):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rmssd,
        delta={'reference': gemiddelde_rmssd, 
               'increasing': {'color': "red"}, 
               'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [0, 100], 
                    'tickvals': [0, 25, 50, 75], 
                    'ticktext': ["0", "25", "50", "75"]},
            'steps': [
                {'range': [0, 25], 'color': "red"},
                {'range': [25, 50], 'color': "orange"},
                {'range': [50, 75], 'color': "lightgreen"},
                {'range': [75, 100], 'color': "yellow"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': gemiddelde_rmssd
            }
        }
    ))
    return fig''', language='python')
        
        st.write("""
        **Doel**: Creëert een interactieve gauge (meter) visualisatie voor HRV-waarden.
        
        **Parameters**:
        - `rmssd`: Huidige RMSSD waarde om te tonen
        - `gemiddelde_rmssd`: Gemiddelde RMSSD waarde als referentie
        
        **Werking**:
        1. Maakt een Plotly gauge visualisatie
        2. Toont huidige RMSSD waarde met een wijzer
        3. Vergelijkt met gemiddelde (delta)
        4. Gebruikt kleurcodering voor verschillende zones:
           - Rood (0-25): Zeer lage HRV
           - Oranje (25-50): Lage HRV
           - Lichtgroen (50-75): Optimale HRV
           - Geel (75-100): Hoge HRV
        5. Toont zwarte referentielijn voor gemiddelde
        
        **Visuele Elementen**:
        - Wijzer: Toont huidige waarde
        - Delta: Verschil met gemiddelde
        - Kleurzones: Indicatie van HRV-status
        - Referentielijn: Gemiddelde waarde
        """)

        st.subheader("7. Stressscore Visualisatie")
        st.write("**Functie: `visualize_stressscore(df)`**")
        st.code('''def visualize_stressscore(df):
    min_rmssd = df['rmssd'].min()
    max_rmssd = df['rmssd'].max()
    stressscore = 100 * (1 - (df['rmssd'] - min_rmssd) / (max_rmssd - min_rmssd))
    fig = go.Figure(go.Bar(
        x=['Stressscore'], 
        y=[stressscore.mean()], 
        marker_color='red'
    ))
    fig.update_layout(
        yaxis=dict(
            range=[0, 100], 
            title='Stressscore (0-100)'
        ), 
        xaxis=dict(title='')
    )
    return fig''', language='python')
        
        st.write("""
        **Doel**: Berekent en visualiseert een stressscore op basis van HRV-waarden.
        
        **Parameters**:
        - `df`: DataFrame met RMSSD waarden
        
        **Werking**:
        1. Berekent minimum en maximum RMSSD waarden
        2. Normaliseert RMSSD naar stressscore (0-100):
           - Lage RMSSD → Hoge stressscore
           - Hoge RMSSD → Lage stressscore
        3. Creëert een staafdiagram met de gemiddelde stressscore
        
        **Interpretatie**:
        - 0-30: Laag stressniveau
        - 31-60: Gemiddeld stressniveau
        - 61-100: Hoog stressniveau
        
        **Visualisatie**:
        - Rode staaf voor duidelijke stress-indicatie
        - Y-as van 0-100 voor intuïtieve schaal
        - Gemiddelde score over de meetperiode
        """)

        st.subheader("Dataformaat")
        st.write("**Vereist bestandsformaat:**")
        st.write("""
        - CSV of TXT bestand
        - Kolommen:
          * `time`: tijdstempel (ms)
          * `ECG`: ECG-signaal (mV)
          * `accX`, `accY`, `accZ`: versnelling (g)
        - Sampling rate: 1024 Hz
        - Delimiter: komma (,)
        """)
        
        st.write("**Voorbeeld data format:**")
        st.code('''time,ECG,accX,accY,accZ
0,0.5,0.1,-0.2,1.0
1,0.6,0.2,-0.1,1.1
2,0.4,0.1,-0.3,0.9''', language='python')

    # Disclaimer onderaan elke pagina
    st.divider()
    st.caption("""
    **Disclaimer**: Dit dashboard is bedoeld als hulpmiddel ter ondersteuning van uw leefstijl.
    Raadpleeg altijd een arts bij gezondheidsklachten of medische vragen.
    """)

# Voeg de infopagina toe aan de navigatie
if __name__ == "__main__":
    info_page()

