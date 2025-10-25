# Projet Data Storytelling: Disponibilité Vélib'

Application Streamlit réalisée pour le cours EFREI Data Stories 2025. Elle explore et montre la disponibilité des vélos Vélib' à Paris et sa proche banlieue, en utilisant les données pour raconter une histoire.

## L'Histoire : Pourquoi ce projet ?

**Le problème est simple** : trouver un Vélib' (ou une place libre) quand on en a besoin, surtout le soir ou après un événement, c'est parfois compliqué. On tombe sur des stations vides ou pleines, c'est frustrant.

Ce projet utilise les données de disponibilité pour :
1.  **Montrer** la situation actuelle : Où sont les vélos ? Où y a-t-il des places ?
2.  **Analyser** les différences : Certaines zones sont-elles mieux servies ? Une grande station a-t-elle toujours des vélos ?
3.  **Aider** l'utilisateur à voir rapidement les zones où c'est facile de trouver un vélo et celles où c'est plus tendu.

## Les Données

* **Source :** Données "temps réel" sur la disponibilité des stations Vélib' Métropole.
* **Fichier :** Pour ce projet, on utilise un *instantané* de ces données, stocké dans `data/velib_data.json`.
* **Licence :** Les données Vélib' sont généralement sous licence ouverte (à vérifier sur le portail officiel).
* **Préparation :** Les données JSON brutes ont été nettoyées : extraction des coordonnées, conversion des types, gestion des stations non opérationnelles, suppression des stations sans coordonnées, calcul du taux de disponibilité (`TauxDispo`).

## Fonctionnalités et Analyse

L'application permet d'explorer les données via :

* **Filtres** : Par commune, nombre minimum de vélos, type de vélo (mécanique/électrique).
* **Indicateurs Clés (KPIs)** : Résumé rapide de la situation selon les filtres (nb stations, nb vélos, dispo moyenne).
* **Carte Interactive** : Vue géographique des stations. La couleur indique la disponibilité (vert/orange/rouge), la taille le nombre de vélos.
* **Graphique Capacité vs. Disponibilité** : Nuage de points pour voir le lien (ou non) entre taille de station et disponibilité.
* **Comparaison des Communes** : Bar chart du taux de disponibilité moyen par commune (Top 20).
* **Tableau Détaillé par Commune** : Liste des stations d'une commune choisie avec vélos dispos, places libres, taux de dispo.

## Comment l'Application Raconte l'Histoire

1.  **Contexte** : L'intro pose le problème de la station vide/pleine.
2.  **Exploration** : Les filtres permettent de cibler la recherche.
3.  **Vue d'Ensemble** : KPIs et carte montrent la situation globale dans la zone.
4.  **Analyse** : Les graphiques aident à comprendre les tendances (une grande station n'est pas toujours pleine, certaines communes sont mieux loties en moyenne). Le tableau permet de choisir une station précise.
5.  **Conclusion** : Résumé des points clés et conseil pratique (regarder la carte, prévoir une station de secours).

## Limitations

* **Instantanéité** : Les données sont une photo à un instant T, la réalité change vite.
* **Pas de Prédiction** : L'outil ne devine pas la disponibilité future.
* **Fiabilité des Données** : Dépend de la qualité des données sources au moment de la capture.

