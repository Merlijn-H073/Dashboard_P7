# -*- coding: utf-8 -*-
"""
Beginner versie van het hartgezondheid dashboard.
Toont vereenvoudigde visualisaties en analyses.

@author: merli and sven
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

#%% Functies
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

def bereken_rmssd(df):
    """
    Berekent de RMSSD (Root Mean Square of Successive Differences).
    Dit is een maat voor hartslagvariabiliteit.
    """
    rmssd = np.sqrt(np.mean(np.square(np.diff(df['rr'])))) * 100
    return rmssd

def visualize_rmssd_per_block(df):
    """
    Visualiseert de RMSSD per minuut in een lijngrafiek.
    """
    df['time_block'] = (df['timestamp'] // 60) * 60  # Groepeer per minuut
    rmssd_per_block = df.groupby('time_block').apply(bereken_rmssd).reset_index(name='rmssd')
    rmssd_per_block['time_block_min'] = rmssd_per_block['time_block'] / 60
    fig = px.line(rmssd_per_block, x='time_block_min', y='rmssd', markers=True)
    fig.update_layout(xaxis_title='Tijd (minuten)', yaxis_title='RMSSD (ms)')
    return fig

def visualize_stressscore(df):
    """
    Berekent en visualiseert een stressscore op basis van RMSSD.
    Lage RMSSD = hoge stress, hoge RMSSD = lage stress.
    """
    min_rmssd = df['rmssd'].min()
    max_rmssd = df['rmssd'].max()
    stressscore = 100 * (1 - (df['rmssd'] - min_rmssd) / (max_rmssd - min_rmssd))
    fig = go.Figure(go.Bar(x=['Stressscore'], y=[stressscore.mean()], marker_color='red'))
    fig.update_layout(yaxis=dict(range=[0, 100], title='Stressscore (0-100)'), xaxis=dict(title=''))
    return fig

def visualize_gauge(rmssd):
    fig = go.Figure(go.Indicator(mode="gauge+number+delta", value=rmssd, delta={'reference': rmssd, 'increasing': {'color': "red"}}, gauge={'axis': {'range': [0, 100], 'tickvals': [0, 25, 50, 75], 'ticktext': ["0", "25", "50", "75"]}, 'steps': [{'range': [0, 25], 'color': "red"}, {'range': [25, 50], 'color': "orange"}, {'range': [50, 75], 'color': "lightgreen"}, {'range': [75, 100], 'color': "yellow"}], 'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': rmssd}}))
    return fig

def bereken_sdnn(df):
    """
    Berekent SDNN (standaarddeviatie van RR-intervallen in ms).
    Input: DataFrame met kolom 'rr' in seconden.
    Output: SDNN in milliseconden.
    """
    sdnn = np.std(df['rr'], ddof=1) * 1000  # Seconden naar ms
    return sdnn

def visualize_sdnn_per_block(df):
    """
    Visualiseert de SDNN per minuut in een lijngrafiek.
    """
    df['time_block'] = (df['timestamp'] // 60) * 60  # Groepeer per minuut
    sdnn_per_block = df.groupby('time_block').apply(bereken_sdnn).reset_index(name='sdnn')
    sdnn_per_block['time_block_min'] = sdnn_per_block['time_block'] / 60
    fig = px.line(sdnn_per_block, x='time_block_min', y='sdnn', markers=True)
    fig.update_layout(xaxis_title='Tijd (minuten)', yaxis_title='SDNN (ms)')
    return fig

def bereken_stappenteller(df, intervallen, activiteiten, drempel=0.5):
    """
    Detecteert stappen op basis van versnellingsdata.
    
    Parameters:
    - df: DataFrame met versnellingsdata
    - intervallen: Tijdsintervallen voor verschillende activiteiten
    - activiteiten: Labels voor de activiteiten
    - drempel: Gevoeligheid voor stapdetectie (0-1)
    
    Returns:
    - df: DataFrame met stappenteller
    - stappen_index: Indices waar stappen gedetecteerd zijn
    """
    df = df.copy()
    # Label de activiteiten
    df['activiteit'] = pd.cut(df['timestamp'], bins=intervallen, labels=activiteiten, ordered=False)
    
    # Bereken totale versnelling
    df['samengesteld_signaal'] = np.sqrt(df['accX']**2 + df['accY']**2 + df['accZ']**2)
    df['genormaliseerd'] = df['samengesteld_signaal'] - df['samengesteld_signaal'].mean()

    # Detecteer stappen per activiteit
    stappen_dfs = []
    for activiteit in activiteiten:
        df_filt = df[df['activiteit'] == activiteit]
        if df_filt.empty:
            continue
        pieken = find_peaks(df_filt['genormaliseerd'],
                            height=df_filt['genormaliseerd'].max() * drempel,
                            distance=10)[0]
        stappen_dfs.append(df_filt.iloc[pieken])

    # Combineer alle gedetecteerde stappen
    df_stappen = pd.concat(stappen_dfs)
    stappen_index = df_stappen.index

    # Maak stappenteller
    df['is_een_stap'] = df.index.isin(stappen_index)
    df['stappenteller'] = df['is_een_stap'].cumsum()

    return df, stappen_index

def berekenen_intensiteit(df_acc, df_bpm, resolutie=60):
    # Verdeel data in tijdsblokken van 1 minuut
    df_acc['blok'] = (df_acc['timestamp'] // resolutie).astype(int)
    df_bpm['blok'] = (df_bpm['timestamp'] // resolutie).astype(int)
    
    # Bereken gemiddelde versnelling en hartslag per blok
    acc_blok = df_acc.groupby('blok')['samengesteld'].mean().reset_index(name='gem_acc')
    bpm_blok = df_bpm.groupby('blok')['bpm'].mean().reset_index(name='gem_bpm')
    
    # Combineer versnellings- en hartslagdata
    df_blok = pd.merge(acc_blok, bpm_blok, on='blok', how='inner')
    
    # Bepaal rusthartslag (5e percentiel van alle hartslagwaarden)
    resting_hr = df_bpm['bpm'].quantile(0.05)
    
    # Bereken hartslagzones met Karvonen formule
    max_hr = 220 - st.session_state.user_age  # Maximale hartslag op basis van leeftijd
    hrr = max_hr - resting_hr  # Heart Rate Reserve
    moderate_hr = resting_hr + (hrr * 0.45)  # 45% van HRR voor matige intensiteit
    vigorous_hr = resting_hr + (hrr * 0.70)  # 70% van HRR voor hoge intensiteit
    
    # Bepaal versnellingsdrempels op basis van percentielwaarden
    acc_moderate = np.percentile(df_acc['samengesteld'], 60)  # 60e percentiel voor matig
    acc_vigorous = np.percentile(df_acc['samengesteld'], 80)  # 80e percentiel voor intensief
    
    # Begin met alle minuten als rust
    df_blok['intensiteit'] = 0
    
    # Classificeer eerst op basis van hartslag
    df_blok['hr_intensity'] = np.where(
        df_blok['gem_bpm'] > vigorous_hr, 2,  # Boven vigorous_hr = intensief
        np.where(df_blok['gem_bpm'] > moderate_hr, 1, 0)  # Boven moderate_hr = matig
    )
    
    # Classificeer daarna op basis van versnelling
    df_blok['acc_intensity'] = np.where(
        df_blok['gem_acc'] > acc_vigorous, 2,  # Boven acc_vigorous = intensief
        np.where(df_blok['gem_acc'] > acc_moderate, 1, 0)  # Boven acc_moderate = matig
    )
    
    # Combineer hartslag en versnelling voor eindclassificatie:
    # Intensief: Beide metingen hoog
    # Matig: Of één hoog, of beide matig
    df_blok['intensiteit'] = np.where(
        ((df_blok['hr_intensity'] == 2) & (df_blok['acc_intensity'] == 2)),  # Beide hoog
        2,  # Intensief
        np.where(
            ((df_blok['hr_intensity'] == 2) & (df_blok['acc_intensity'] >= 1)) |  # Hoge hartslag met matige beweging
            ((df_blok['hr_intensity'] >= 1) & (df_blok['acc_intensity'] == 2)) |  # Hoge beweging met matige hartslag
            ((df_blok['hr_intensity'] == 1) & (df_blok['acc_intensity'] == 1)),   # Beide matig
            1,  # Matig
            0   # Rust
        )
    )
    
    # Zoek aaneengesloten blokken activiteit
    df_blok['consecutive_group'] = (df_blok['intensiteit'] != df_blok['intensiteit'].shift()).cumsum()
    df_blok['group_size'] = df_blok.groupby('consecutive_group')['intensiteit'].transform('size')
    
    # Tel alleen blokken van 10+ minuten mee (WHO richtlijn)
    min_consecutive_blocks = 10
    df_blok.loc[df_blok['group_size'] < min_consecutive_blocks, 'intensiteit'] = 0
    
    # Bereken totaal aantal intensiteitsminuten
    moderate_minutes = (df_blok['intensiteit'] == 1).sum()
    vigorous_minutes = (df_blok['intensiteit'] == 2).sum() * 2  # Intensief telt dubbel
    total_intensity_minutes = moderate_minutes + vigorous_minutes
    
    # Verwijder hulpkolommen
    df_blok = df_blok.drop(['hr_intensity', 'acc_intensity'], axis=1)
    
    return df_blok, total_intensity_minutes

#%% Streamlit opmaak
st.set_page_config(page_title="Dashboard hart gezondheid", layout="wide", initial_sidebar_state="collapsed")
st.title('Dashboard hart gezondheid')

# Check of data er is
if 'data_initialized' not in st.session_state:
    st.error("Begin alstublieft op de homepagina om de data te initialiseren.")
    st.stop()
    
# haal de data uit de session state
df_ecg = st.session_state.df_ecg
df_ecg_pieken = st.session_state.df_ecg_pieken
intervallen = st.session_state.intervallen
activiteiten = st.session_state.activiteiten
activiteiten_kleuren = st.session_state.activiteiten_kleuren

# Sidebar
st.sidebar.header("Navigatie: selectie van grafieken")
with st.sidebar:
    st.sidebar.subheader("Beginner")
    show_hrv = st.checkbox("HRV", value=True)
    show_sdnn = st.checkbox("SDNN", value=True)
    show_stappenteller = st.checkbox("Stappenteller", value=True)
    show_bewegingsminuten = st.checkbox("Bewegings minuten", value=True)
    
# plots
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if show_hrv:
        st.subheader("HRV (RMSSD) per minuten")
        fig2 = visualize_rmssd_per_block(df_ecg_pieken.copy())
        intervallen_minuten = [i / 60 for i in intervallen]
        for i in range(len(intervallen_minuten) - 1):
            kleur = activiteiten_kleuren[activiteiten[i]]
            fig2.add_vrect(x0=intervallen_minuten[i], x1=intervallen_minuten[i+1], fillcolor=kleur, opacity=0.25, annotation_text=activiteiten[i])
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("ℹ️ Uitleg over de grafiek"):
            st.subheader("HRV-analyse: RMSSD per 60 seconden")
            st.write("""             
Wat laat het zien:
De RMSSD (Root Mean Square of Successive Differences) is een maat voor de variatie in tijd tussen opeenvolgende hartslagen. Hier wordt het per minuut gevisualiseerd.

Wat betekend dit:
RMSSD is een indicator voor parasympathische activiteit (ontspanningszenuwstelsel). 
Omdat dit een indicator is voor het parasympathische zenuwstelsel geeft deze alleen acurate resultaten als er in rust gemeten is.

**Hoge RMSSD** = betere stressregulatie, rustiger autonoom zenuwstelsel.

**Lage RMSSD** = verhoogde stress, vermoeidheid of verminderde cardiovasculaire flexibiliteit.

Belangrijk bij het beoordelen van stressniveau, herstel na inspanning, of algemene hartgezondheid.

*bron: Caring Medical Florida. (2024, 12 juli). Heart rate variability. https://caringmedical.com/hauser-neck-center/heart-rate-variability/*
                     """)

with col2:
    if show_sdnn:
        st.subheader("HRV (SDNN) per minuten")
        fig3 = visualize_sdnn_per_block(df_ecg_pieken.copy())
        intervallen_minuten = [i / 60 for i in intervallen]
        for i in range(len(intervallen_minuten) - 1):
            kleur = activiteiten_kleuren[activiteiten[i]]
            fig3.add_vrect(x0=intervallen_minuten[i], x1=intervallen_minuten[i+1], fillcolor=kleur, opacity=0.25, annotation_text=activiteiten[i])
        st.plotly_chart(fig3, use_container_width=True)
        with st.expander("ℹ️ Uitleg over de grafiek"):
            st.subheader("HRV-analyse: SDNN per 60 seconden")
            st.write("""                 
Wat laat het zien:
De standaarddeviatie van alle RR-intervallen in een minuut. Dit is een globale maat voor hartslagvariatie.

Wat betekend dit:
SDNN is een algemene HRV-indicator.

Hoge SDNN = gezonde balans tussen stress en herstel, veerkrachtig autonoom zenuwstelsel.

Lage SDNN = vaak geassocieerd met chronische stress, burn-out, of hartproblemen.

*bron: Caring Medical Florida. (2024, 12 juli). Heart rate variability. https://caringmedical.com/hauser-neck-center/heart-rate-variability/*
                     """)
    
with col3:
    if show_stappenteller:
        st.subheader("Stappenteller")
        df_bewerkt, stappen_index = bereken_stappenteller(df_ecg_pieken, intervallen, activiteiten, drempel=0.1)
        totaal_stappen = df_bewerkt['stappenteller'].iloc[-1]
        
        # Calculate progress towards daily goal (typical goal is 10,000 steps)
        daily_goal = 10000
        progress = min(100, (totaal_stappen / daily_goal) * 100)
        
        # Display current steps with big number
        st.markdown(f"<h1 style='text-align: center; color: #0066cc;'>{int(totaal_stappen):,}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>stappen</p>", unsafe_allow_html=True)
        
        # Show progress bar
        st.progress(progress / 100)
        
        # Show goal information
        st.markdown(f"<p style='text-align: center;'>{int(totaal_stappen):,} / {daily_goal:,} stappen</p>", unsafe_allow_html=True)
        
        # Add context about step counts
        with st.expander("ℹ️ Over stappenteller"):
            st.write("""
            **Dagelijks stappendoel: 10.000 stappen**
            
            Verschillende activiteitsniveaus:
            - Sedentair: < 5.000 stappen
            - Licht actief: 5.000-7.499 stappen
            - Redelijk actief: 7.500-9.999 stappen
            - Actief: 10.000-12.499 stappen
            - Zeer actief: ≥ 12.500 stappen
            
            *Bron: Tudor-Locke et al. (2008) - International Journal of Behavioral Nutrition and Physical Activity*
            """)

if 'samengesteld' not in df_ecg.columns:
    df_ecg['samengesteld'] = np.sqrt(df_ecg['accX']**2 + df_ecg['accY']**2 + df_ecg['accZ']**2)
df_intensiteit, total_intensity_minutes = berekenen_intensiteit(df_ecg, df_ecg_pieken)
with col4:
    if show_bewegingsminuten:
        st.subheader("Bewegingsintensiteit")
    
        # Calculate moderate and vigorous minutes separately
        moderate_minutes = (df_intensiteit['intensiteit'] == 1).sum()
        vigorous_minutes = (df_intensiteit['intensiteit'] == 2).sum()
    
        # Create two columns for the metrics
        metric_col1, metric_col2 = st.columns(2)
    
        with metric_col1:
            st.metric(
                label="Matige intensiteit",
                value=f"{moderate_minutes} min",
                help="Minuten waarin je stevig doorstapt of licht actief bent"
                )
    
        with metric_col2:
            st.metric(
                label="Hoge intensiteit",
                value=f"{vigorous_minutes} min (telt 2x)",
                help="Minuten waarin je intensief beweegt (tellen dubbel voor je dagelijkse doel)"
                )
    
        # Show total with progress towards daily goal
        daily_goal = 30  # Standard daily goal is often 30 minutes
        progress = min(100, (total_intensity_minutes / daily_goal) * 100)
        
        st.progress(progress / 100)
        st.metric(
            label="Totaal intensiteitsminuten",
            value=f"{total_intensity_minutes} / {daily_goal} min",
            help="Dagelijks doel: 30 minuten matige OF 15 minuten intensieve beweging"
        )
        
        with st.expander("ℹ️ Over bewegingsminuten"):
            st.write("""
            **Bewegingsminuten Doel: 30 min per dag**
            
            De Wereldgezondheidsorganisatie (WHO) beveelt aan:
            - 30 min matige intensiteit OF
            - 15 min hoge intensiteit
            
            Hoge intensiteit telt dubbel, dus bijvoorbeeld:
            - 20 min matig + 5 min intensief = 30 min totaal
            - 15 min intensief = 30 min totaal
            
            *Bron: WHO Guidelines on Physical Activity and Sedentary Behaviour (2020)*
            """)