
import streamlit as st
import pandas as pd
import os


DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'velib_data.json')
def load_data():
    """
    Charge et met en cache les données brutes depuis le JSON local.
    """
    try:
        
        df_raw = pd.read_json(DATA_PATH)
        
        if df_raw.empty:
            st.error("Le jeu de données JSON est vide.")
            return pd.DataFrame()
            
        return df_raw
        
    except FileNotFoundError:
        st.error(f"Erreur : Le fichier {DATA_PATH} est introuvable. Assurez-vous qu'il est bien dans le dossier 'data'.")
        return pd.DataFrame()
    except ValueError as ve:
        st.error(f"Erreur lors de la lecture du JSON : {ve}. Assurez-vous que le fichier est correctement formaté.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur inattendue lors du chargement des données : {e}")
        return pd.DataFrame()