# Gestion d'une flotte de véhicules en location — Sujet D

Projet de fin de semestre — L2 RI, ISI Dakar — Module POO & Persistance des données
Formateur : M. HAMANE — Année 2025-2026

## Description

Application Python de gestion d'une flotte de véhicules en location (voitures,
utilitaires, motos). Le système gère :

- Une hiérarchie de véhicules orientée objet (classe abstraite + 3 classes filles).
- Le cycle complet d'une location (réservation, retour, calcul du tarif, pénalité de retard).
- L'entretien des véhicules (composition).
- La persistance des données en JSON, CSV et SQLite.
- Des rapports de disponibilité et de chiffre d'affaires.

## Équipe

- Abdoul Basse
- Omar Ngalla Diagne
- Lamine Ekoye Diatta

Voir `CONTRIBUTIONS.md` pour la répartition détaillée du travail.

## Installation

```bash
git clone <url-du-depot>
cd flotte_locations
python3 -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Aucune dépendance externe n'est strictement nécessaire (le projet utilise
uniquement la bibliothèque standard Python : `sqlite3`, `json`, `csv`, `logging`,
`dataclasses`, `abc`, `enum`). `requirements.txt` liste les outils de dev (tests, lint).

## Utilisation

Lancer le scénario de démonstration complet :

```bash
python3 -m src.main
```

Cela va :
1. Créer une flotte de 8 véhicules (3 voitures, 3 utilitaires, 2 motos).
2. Effectuer plusieurs locations (dont une en retard, avec pénalité).
3. Enregistrer un entretien.
4. Exporter l'état de la flotte en JSON (`data/flotte.json`).
5. Exporter les locations en CSV (`exports/locations.csv`).
6. Créer/synchroniser la base SQLite (`data/flotte.db`).
7. Afficher les rapports et le résultat de 4 requêtes SQL métier.

## Structure du projet

```
flotte_locations/
├── README.md
├── CONTRIBUTIONS.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── enums.py           # StatutVehicule, CategorieClient, TypeEntretien
│   ├── exceptions.py       # Exceptions métier personnalisées
│   ├── vehicules.py        # VehiculeBase (ABC), Voiture, Utilitaire, Moto, Entretien
│   ├── flotte.py           # Flotte (agrégation de véhicules)
│   ├── location.py         # Location, GestionLocations
│   ├── persistence.py      # Export/import JSON, export CSV
│   ├── database.py         # Persistance SQLite + requêtes métier
│   ├── rapports.py         # Rapports texte (disponibilité, entretien)
│   └── main.py             # Scénario de démonstration
├── data/                   # fichiers JSON et SQLite générés (ignorés par git)
└── exports/                # fichiers CSV générés (ignorés par git)
```

## Architecture orientée objet

- **Classe abstraite** : `VehiculeBase` impose `calculer_tarif_jour()` et `necessite_entretien()`.
- **Héritage** : `Voiture`, `Utilitaire`, `Moto` héritent de `VehiculeBase` et surchargent les deux méthodes.
- **Enum** : `StatutVehicule`, `CategorieClient`, `TypeEntretien`.
- **Agrégation** : `Flotte` reçoit des `VehiculeBase` créés en dehors d'elle.
- **Composition** : chaque `VehiculeBase` crée et possède ses propres `Entretien` via `ajouter_entretien()`.

## Base de données

Deux tables liées par clé étrangère : `vehicules` et `locations`
(`locations.immatriculation` référence `vehicules.immatriculation`).

Requêtes métier implémentées (`src/database.py`) :
1. `vehicules_disponibles_a_date` — véhicules libres à une date donnée.
2. `chiffre_affaires_par_categorie_vehicule` — CA groupé par type de véhicule.
3. `historique_entretien_par_vehicule` — état courant d'un véhicule donné.
4. `locations_en_retard` — locations actives dont la date de fin est dépassée.
