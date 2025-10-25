# utils/prep.py (Version Simplifiée)
import pandas as pd
import geopandas as gpd
import streamlit as st 

def clean_data(df_raw):
    """
    Nettoie les données brutes Vélib' de manière simplifiée: 
    extraction coordonnées, remplacements basiques, suppression si trop de manquants.
    """
    if df_raw.empty:
        return pd.DataFrame(), "Les données brutes sont vides."

    df = df_raw.copy()
    

    try:
        if 'coordonnees_geo' in df.columns and df['coordonnees_geo'].apply(lambda x: isinstance(x, dict)).any():
            coords = pd.json_normalize(df['coordonnees_geo'])
            df['lat'] = coords.get('lat', pd.NA)
            df['lon'] = coords.get('lon', pd.NA)
        else: 
            df['lat'] = pd.NA
            df['lon'] = pd.NA
            
    except Exception as e:
        st.warning(f"Impossible d'extraire les coordonnées géo : {e}")
        df['lat'] = pd.NA
        df['lon'] = pd.NA

    
    rename_map = {
        'name': 'NomStation',
        'nom_arrondissement_communes': 'Commune',
        'capacity': 'CapaciteTotal',
        'numdocksavailable': 'BornesLibres',
        'numbikesavailable': 'VelosDispoTotal',
        'mechanical': 'VelosMecaniques',
        'ebike': 'VelosElectriques',
        'is_renting': 'LocationPossible',
        'is_returning': 'RetourPossible'
    }
    df = df.rename(columns=rename_map)
    
    
    cols_to_keep = list(rename_map.values()) + ['lat', 'lon']
    
    
    for col in df.columns:
        if col not in cols_to_keep:
           
            if col in df.columns:
                 df = df.drop(columns=[col])


   

    
    for col in ['Commune', 'NomStation']:
        if col in df.columns:
            missing_pct = df[col].isnull().mean() * 100
            if missing_pct > 50: 
                df = df.drop(columns=[col])
                st.warning(f"Colonne '{col}' supprimée car >50% de valeurs manquantes.")
            else:
                 
                 df[col] = df[col].fillna('Inconnue').astype(str)

   
    numeric_cols = ['CapaciteTotal', 'BornesLibres', 'VelosDispoTotal', 'VelosMecaniques', 'VelosElectriques']
    for col in numeric_cols:
        if col in df.columns:
            
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df[col] = df[col].fillna(0).astype(int)

    
    if 'lat' in df.columns and 'lon' in df.columns:
         df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
         df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
         
         df.dropna(subset=['lat', 'lon'], inplace=True)
         
   
    bool_cols = ['LocationPossible', 'RetourPossible']
    for col in bool_cols:
        if col in df.columns:
           
            df[col] = df[col].astype(str).apply(lambda x: True if x == 'OUI' else False)

    if 'LocationPossible' in df.columns and 'RetourPossible' in df.columns:
        df = df[(df['LocationPossible'] == True) | (df['RetourPossible'] == True)]
    elif 'LocationPossible' in df.columns:
         df = df[df['LocationPossible'] == True]
    elif 'RetourPossible' in df.columns:
         df = df[df['RetourPossible'] == True]
         
    
    if 'CapaciteTotal' in df.columns and 'VelosDispoTotal' in df.columns:
       
        df['TauxDispo'] = df.apply(lambda row: (row['VelosDispoTotal'] / row['CapaciteTotal'] * 100) if row['CapaciteTotal'] > 0 else 0, axis=1)
    else:
        df['TauxDispo'] = 0 

    
    data_quality_report = f"""
    - **Stations initiales**: {len(df_raw)}.
    - **Stations après nettoyage/filtrage**: {len(df)}.
    - *Nettoyage simplifié appliqué (remplacement par 0 ou 'Inconnue', suppression lignes sans coordonnées valides).*
    """
    if df.empty:
        return pd.DataFrame(), "Aucune donnée valide restante après nettoyage."

    return df, data_quality_report


def make_geodataframe(df_clean):
    """Crée un GeoDataFrame pour la cartographie (inchangé)."""
    if df_clean.empty or 'lon' not in df_clean.columns or 'lat' not in df_clean.columns:
        st.warning("Données géographiques (lat/lon) manquantes ou invalides pour créer GeoDataFrame.")
        return None
        
   
    df_clean['lat'] = pd.to_numeric(df_clean['lat'], errors='coerce')
    df_clean['lon'] = pd.to_numeric(df_clean['lon'], errors='coerce')
    
    if df_clean[['lat', 'lon']].isnull().any().any():
        rows_to_drop = df_clean[['lat', 'lon']].isnull().any(axis=1).sum()
        if rows_to_drop > 0:
            st.warning(f"Suppression de {rows_to_drop} stations avec coordonnées invalides pour la carte.")
            df_geo = df_clean.dropna(subset=['lat', 'lon']).copy() 
        else:
             df_geo = df_clean.copy()
    else:
        df_geo = df_clean.copy()
        
    if df_geo.empty:
         st.warning("Aucune station avec coordonnées valides à afficher sur la carte.")
         return None

    try:
        gdf = gpd.GeoDataFrame(
            df_geo, 
            geometry=gpd.points_from_xy(df_geo.lon, df_geo.lat),
            crs="EPSG:4326" 
        )
        return gdf
    except Exception as e:
        st.error(f"Erreur lors de la création du GeoDataFrame : {e}")
        return None