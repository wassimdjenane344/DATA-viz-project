# app.py
import streamlit as st
import pandas as pd
from utils.io import load_data
from utils.prep import clean_data, make_geodataframe
from utils.viz import bar_chart_dispo_commune, scatter_plot_capacite_vs_dispo, map_chart_dispo


st.set_page_config(
    page_title="Dispo Vélib' - L'Histoire d'un Trajet", 
    layout="wide",
    initial_sidebar_state="expanded" 
)


df_raw = load_data()
if df_raw is None or df_raw.empty:
    st.error("Échec du chargement des données initiales. Vérifiez le fichier 'data/velib_data.json'.")
    st.stop() 

df_clean, data_quality_report = clean_data(df_raw)
if df_clean.empty:
    st.error("Aucune donnée valide n'a pu être traitée après le nettoyage. Vérifiez la structure du fichier JSON et le script de préparation.")
    st.info(data_quality_report) 
    st.stop() 


st.title("🚲 L'Odyssée Vélib' : Trouver un vélo quand on en a besoin")
st.markdown("""
**Le Problème : La station vide.** Qui n'a jamais vécu ça ? Fin de journée, sortie de concert à l'Accor Arena (Bercy), ou simple envie de rentrer... et là, la station Vélib' la plus proche est désespérément vide. 😩 Ou pire, pleine à craquer quand on veut *déposer* son vélo ! 

Cette application explore la disponibilité actuelle des Vélib' pour comprendre où et quand les vélos manquent ou abondent. L'objectif : transformer la frustration en anticipation et mieux planifier nos trajets.
""")
st.caption("Source: Données temps réel Vélib' Métropole (via le fichier JSON fourni).") 


with st.sidebar:
    st.header("Filtres") 
    
   
    if not df_clean.empty:
        
        commune_list = ['Toutes']
        if 'Commune' in df_clean.columns:
            try:
               
                unique_communes = sorted(df_clean['Commune'].unique())
                commune_list.extend(unique_communes)
            except Exception as e:
                st.warning(f"Impossible de trier les communes: {e}")
                commune_list.extend(df_clean['Commune'].unique())
        
        commune_select = st.selectbox(
            "📍 Où cherchez-vous ?",
            commune_list,
            index=0 
        ) 
        
        
        min_velos_dispo = 0
        max_val_velos = 10 
        if 'VelosDispoTotal' in df_clean.columns:
            try:
               max_val_velos = int(df_clean['VelosDispoTotal'].max())
               
               if max_val_velos < 0: max_val_velos = 0
            except ValueError:
                st.warning("Impossible de déterminer le max de vélos disponibles, utilisation d'une valeur par défaut.")
                max_val_velos = 50 

            min_velos_dispo = st.slider(
                "Combien de vélos au minimum ?",
                min_value=0,
                max_value=max_val_velos, 
                value=1 if max_val_velos >= 1 else 0, 
                step=1,
                help="Filtre les stations ayant AU MOINS ce nombre de vélos disponibles."
            )
        else:
             st.warning("Colonne 'VelosDispoTotal' manquante, filtre désactivé.")
             min_velos_dispo = 0 

        
        type_velo_options = ['Tous']
        if 'VelosMecaniques' in df_clean.columns: type_velo_options.append('Mécanique')
        if 'VelosElectriques' in df_clean.columns: type_velo_options.append('Électrique')

        
        type_velo_select = 'Tous'
        if len(type_velo_options) > 1:
            type_velo_select = st.radio(
                " Quel type de vélo ?",
                type_velo_options,
                index=0, 
                help="Certaines stations n'ont peut-être que des vélos mécaniques ou électriques."
            )
        else:
             st.info("Information sur le type de vélo non disponible.")
             type_velo_select = 'Tous' 
        
    else:
        st.warning("Impossible de charger les filtres, données manquantes ou invalides.")




df_filtered = df_clean.copy()
if 'Commune' in df_filtered.columns and commune_select != 'Toutes':
    df_filtered = df_filtered[df_filtered['Commune'] == commune_select]
if 'VelosDispoTotal' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['VelosDispoTotal'] >= min_velos_dispo]
if type_velo_select == 'Mécanique' and 'VelosMecaniques' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['VelosMecaniques'] > 0]
elif type_velo_select == 'Électrique' and 'VelosElectriques' in df_filtered.columns:
    df_filtered = df_filtered[df_filtered['VelosElectriques'] > 0]


st.header(" La Situation Actuelle (selon vos filtres)")

if df_filtered.empty:
    st.warning(f"Malheureusement, aucune station ne correspond à vos critères (Commune: {commune_select}, Min. Vélos: {min_velos_dispo}, Type: {type_velo_select}).")
    
else:
    total_stations_filtrees = len(df_filtered)
    total_velos_dispo = df_filtered['VelosDispoTotal'].sum() if 'VelosDispoTotal' in df_filtered.columns else 0
    avg_taux_dispo = df_filtered['TauxDispo'].mean() if 'TauxDispo' in df_filtered.columns else 0.0

    c1, c2, c3 = st.columns(3) 
    with c1:
        st.metric("Stations trouvées", f"{total_stations_filtrees}") 
        st.caption("Nombre de stations répondant à vos critères.")
    with c2:
        st.metric("Vélos disponibles (total)", f"{total_velos_dispo}") 
        st.caption(f"Total de vélos ({type_velo_select if type_velo_select != 'Tous' else 'tous types'}) sur ces stations.")
    with c3:
        st.metric("Disponibilité moyenne", f"{avg_taux_dispo:.1f}%" if pd.notna(avg_taux_dispo) else "N/A") 
        st.caption("Pourcentage moyen de vélos dispo par rapport à la capacité des stations filtrées.")

    st.divider()

 

    st.subheader("🗺️ Où sont les vélos ? La Carte !") 
    st.markdown("Visualisez la répartition géographique. Les **grosses bulles vertes** sont vos meilleures amies ! Les **petites bulles rouges** indiquent une pénurie.")
    gdf_filtered = make_geodataframe(df_filtered) 
    if gdf_filtered is not None and not gdf_filtered.empty:
        map_chart_dispo(gdf_filtered) 
    else:
        st.warning("Impossible d'afficher la carte (pas de données géographiques valides pour les filtres actuels).")

    st.divider()

    st.subheader("🧐 Analyse Détaillée")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Capacité vs. Disponibilité : Est-ce qu'une grande station a toujours des vélos ?**")
        if all(col in df_filtered.columns for col in ['CapaciteTotal', 'VelosDispoTotal', 'TauxDispo', 'NomStation', 'Commune']):
             scatter_chart = scatter_plot_capacite_vs_dispo(df_filtered)
             st.altair_chart(scatter_chart, use_container_width=True)
             st.info("""
             * **Points verts en haut à droite** : Grandes stations bien remplies 
             * **Points rouges en bas** : Stations (grandes ou petites) presque vides 
             * **Points loin de la diagonale** : Indiquent un déséquilibre (très pleine ou très vide par rapport à la capacité).
             """)
        else:
            st.warning("Données insuffisantes pour afficher ce graphique.")

    with col2:
        if commune_select == 'Toutes' and 'Commune' in df_filtered.columns:
            st.markdown("**Comparaison des Communes : Où est-ce le plus facile (en moyenne) ?**")
            bar_chart = bar_chart_dispo_commune(df_filtered)
            st.altair_chart(bar_chart, use_container_width=True)
            st.info("""
            Ce classement peut varier énormément ! Une commune avec beaucoup de gares ou de bureaux peut se vider le soir, tandis qu'une zone résidentielle peut se remplir. 
            Les zones très touristiques ou proches de grands lieux (comme Bercy/Accor Arena après un événement) peuvent aussi voir leur disponibilité chuter rapidement.
            """)
        elif commune_select != 'Toutes' and all(col in df_filtered.columns for col in ['NomStation', 'VelosDispoTotal', 'BornesLibres', 'TauxDispo']):
            st.markdown(f"**Zoom sur {commune_select} : Quelles stations choisir ?**")
            df_commune = df_filtered.sort_values(by='TauxDispo', ascending=False)
            display_cols_map = {
                'NomStation':'Station', 
                'VelosDispoTotal':'Vélos ', 
                'BornesLibres':'Places ', 
                'TauxDispo':'Dispo (%)'
            }
            display_cols = [display_cols_map[col] for col in display_cols_map if col in df_commune.columns]
            df_display = df_commune[[col for col in display_cols_map if col in df_commune.columns]].rename(columns=display_cols_map)
            
            if 'Station' in df_display.columns:
                df_display = df_display.set_index('Station')

            column_config = {}
            if 'Dispo (%)' in df_display.columns:
                column_config["Dispo (%)"] = st.column_config.ProgressColumn(
                        "Dispo (%)", format="%.1f%%", min_value=0, max_value=100,
                    )

            st.dataframe(df_display, column_config=column_config if column_config else None, height=300)
            st.info(" Triez par Vélos ou Places en cliquant sur l'en-tête. La barre 'Dispo (%)' donne une vue rapide.")
        else:
             st.info("Sélectionnez 'Toutes' les communes pour la comparaison ou vérifiez les données.")

    st.divider()


with st.expander(" Qualité des Données & Limites de l'Analyse"):
    st.markdown("### Qualité des Données") 
    st.info(data_quality_report) 
    
    st.markdown("### Limites")
    st.warning("""
    - **Instantanéité Volatile**: Les données Vélib' changent à chaque seconde ! Ce dashboard est une photo, pas un film. Rafraîchissez la page (F5) pour les données les plus récentes.
    - **Pas de Boule de Cristal**: On voit l'état actuel, mais on ne prédit pas si la station sera vide dans 10 minutes.
    - **Fiabilité des Capteurs**: L'analyse dépend de la précision des infos remontées par chaque station. Parfois, un vélo peut être marqué disponible alors qu'il est défectueux.
    """) 


st.header("🏁 Ce qu'il faut retenir & Prochaines Étapes")


if df_filtered.empty:
     conclusion_insight = "Vos filtres actuels ne retournent aucune station disponible."
     conclusion_recommendation = "Essayez de demander moins de vélos minimum, d'élargir la zone géographique ou d'accepter tous les types de vélos."
else:
     
     total_stations_filtrees = len(df_filtered) 
     type_texte = f"de type {type_velo_select.lower()}" if type_velo_select != 'Tous' else "tous types confondus"
     zone_texte = f"dans la commune de {commune_select}" if commune_select != 'Toutes' else "dans les zones sélectionnées"
     
     conclusion_insight = f"""
     **Votre recherche** ({pd.Timestamp.now(tz='Europe/Paris').strftime('%H:%M:%S')}) montre qu'il y a actuellement **{total_velos_dispo} vélo(s)** {type_texte} répartis sur **{total_stations_filtrees} station(s)** {zone_texte} répondant à vos critères (au moins {min_velos_dispo} vélo(s) par station). 
     La disponibilité varie fortement : certaines zones (ou stations) sont bien fournies (vertes 🟢), tandis que d'autres sont sous tension (rouges 🔴). Une grande capacité n'est pas toujours synonyme de disponibilité !
     """
     conclusion_recommendation = "Avant de partir, jetez un œil rapide à la **carte** pour visualiser les stations vertes 🟢 les plus proches de votre destination ou point de départ. Avoir une ou deux **stations de secours** en tête, surtout le soir ou près des zones d'événements (gares, salles de spectacle...), peut vous sauver la mise !"

st.success(
    f"""
    **Insight Clé**: {conclusion_insight}
    
    **Conseil Pratique**: {conclusion_recommendation}
    
    **Pour aller plus loin**: L'idéal serait d'analyser les données sur plusieurs jours/semaines pour voir s'il y a des **schémas récurrents** : quelles stations se vident systématiquement à 9h ? Lesquelles sont pleines le vendredi soir ? Cela permettrait d'anticiper encore mieux ! 🔮
    """
)