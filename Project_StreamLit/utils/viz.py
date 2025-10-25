# utils/viz.py
import altair as alt
import streamlit as st
import pandas as pd

def bar_chart_dispo_commune(df_filtered):
    """
    Crée un graphique en barres montrant la disponibilité moyenne par commune.
    """
    
    if 'Commune' not in df_filtered.columns:
        st.error("La colonne 'Commune' est manquante pour créer le graphique par commune.")
        return alt.Chart(pd.DataFrame({'x':[0], 'y':[0]})).mark_bar() # Return empty chart

    # Calculer la disponibilité moyenne par commune
    df_agg = df_filtered.groupby('Commune')['TauxDispo'].mean().reset_index().sort_values(by='TauxDispo', ascending=False)
    
    # Garder le Top 20 pour la lisibilité
    df_top = df_agg.head(20)

    chart = alt.Chart(df_top).mark_bar().encode(
        x=alt.X('TauxDispo', axis=alt.Axis(title='Taux de Disponibilité Moyen (%)')),
        y=alt.Y('Commune', sort='-x', axis=alt.Axis(title='Commune')), 
        tooltip=[
            alt.Tooltip('Commune'), 
            alt.Tooltip('TauxDispo', format=".1f", title="Dispo. Moyenne (%)")
        ] 
    ).properties(
        title="Top 20 des Communes par Disponibilité Moyenne de Vélos"
    ).interactive()

    return chart

def scatter_plot_capacite_vs_dispo(df_filtered):
    """
    Crée un nuage de points : Capacité vs Vélos Disponibles, couleur par TauxDispo.
    """
    
    required_cols = ['CapaciteTotal', 'VelosDispoTotal', 'TauxDispo', 'NomStation', 'Commune']
    if not all(col in df_filtered.columns for col in required_cols):
        st.error("Colonnes manquantes pour créer le nuage de points.")
        return alt.Chart(pd.DataFrame({'x':[0], 'y':[0]})).mark_point() # Return empty chart
        
    
    if len(df_filtered) > 1000:
        df_sample = df_filtered.sample(1000, random_state=42)
    else:
        df_sample = df_filtered

    chart = alt.Chart(df_sample).mark_circle(size=60).encode(
        x=alt.X('CapaciteTotal', axis=alt.Axis(title='Capacité Totale de la Station')),
        y=alt.Y('VelosDispoTotal', axis=alt.Axis(title='Nombre de Vélos Disponibles')),
        color=alt.Color('TauxDispo', scale=alt.Scale(scheme='redyellowgreen'), title="Taux Dispo (%)"),
        tooltip=[
            alt.Tooltip('NomStation', title="Station"),
            alt.Tooltip('Commune'),
            alt.Tooltip('CapaciteTotal', title="Capacité"),
            alt.Tooltip('VelosDispoTotal', title="Vélos Dispo"),
            alt.Tooltip('TauxDispo', format=".1f", title="Taux Dispo (%)")
        ]
    ).properties(
        title="Disponibilité vs Capacité des Stations"
    ).interactive() 

    return chart

def map_chart_dispo(gdf_filtered):
    """
    Crée une carte des stations, colorée par taux de disponibilité.
    """
    if gdf_filtered is None or gdf_filtered.empty:
        st.warning("Impossible d'afficher la carte : données géographiques invalides.")
        return
        
    
    if 'TauxDispo' not in gdf_filtered.columns or 'VelosDispoTotal' not in gdf_filtered.columns:
        st.error("Colonnes 'TauxDispo' ou 'VelosDispoTotal' manquantes pour la carte.")
       
        st.map(gdf_filtered, latitude='lat', longitude='lon', zoom=11)
        return

    
    def get_color(taux_dispo):
        
        try:
            taux = float(taux_dispo)
            if taux < 10:
                return "#FF0000"  
            elif taux < 30:
                return "#FFA500" 
            else:
                return "#008000"  
        except (ValueError, TypeError):
             return "#808080" 

    gdf_copy = gdf_filtered.copy()
    gdf_copy['color'] = gdf_copy['TauxDispo'].apply(get_color)


    st.map(
        gdf_copy,
        latitude='lat',
        longitude='lon',
        size='VelosDispoTotal', 
        color='color',          
        zoom=11                 
    )
    st.caption("🔴 Taux dispo < 10% | 🟠 < 30% | 🟢 >= 30%. La taille représente le nombre absolu de vélos disponibles.")