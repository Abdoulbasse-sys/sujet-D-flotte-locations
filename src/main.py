"""
Module main.py
Auteur assigné : Lamine Ekoye Diatta (intégration finale)

Scénario de démonstration : crée une flotte mixte, effectue des locations,
un entretien, exporte en JSON/CSV/SQLite et affiche les rapports.
C'est ce script que vous exécuterez en live le jour de la soutenance.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from pathlib import Path

from .database import (
    chiffre_affaires_par_categorie_vehicule,
    creer_tables,
    locations_en_retard,
    synchroniser_depuis_flotte,
    vehicules_disponibles_a_date,
)
from .enums import CategorieClient, TypeEntretien
from .exceptions import ErreurMetierBase
from .flotte import Flotte
from .location import GestionLocations
from .persistence import (
    charger_flotte_json,
    exporter_locations_csv,
    sauvegarder_flotte_json,
)
from .rapports import rapport_disponibilite_texte, rapport_entretien_requis
from .vehicules import Moto, Utilitaire, Voiture

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


def construire_flotte_demo() -> Flotte:
    """Crée une flotte mixte d'au moins 8 véhicules, 3 types différents."""
    flotte = Flotte("Flotte Sebas Location")

    voitures = [
        Voiture("DK-1234-AA", "Toyota", "Corolla", 5, 25000),
        Voiture("DK-5678-AB", "Hyundai", "i10", 4, 18000),
        Voiture("DK-9012-AC", "Kia", "Sportage", 5, 32000),
    ]
    utilitaires = [
        Utilitaire("DK-1111-BA", "Renault", "Kangoo", 800, 28000),
        Utilitaire("DK-2222-BB", "Ford", "Transit", 1500, 40000),
        Utilitaire("DK-3333-BC", "Peugeot", "Partner", 650, 24000),
    ]
    motos = [
        Moto("DK-4444-CA", "Yamaha", "XTZ125", 125, 8000),
        Moto("DK-5555-CB", "Honda", "CB500", 500, 12000),
    ]

    for v in voitures + utilitaires + motos:
        flotte.ajouter_vehicule(v)

    return flotte


def executer_demo() -> None:
    dossier_data = Path(__file__).resolve().parent.parent / "data"
    dossier_exports = Path(__file__).resolve().parent.parent / "exports"
    dossier_data.mkdir(exist_ok=True)
    dossier_exports.mkdir(exist_ok=True)

    chemin_json = dossier_data / "flotte.json"
    chemin_db = str(dossier_data / "flotte.db")
    chemin_csv = dossier_exports / "locations.csv"

    flotte = construire_flotte_demo()
    gestion = GestionLocations()

    aujourdhui = date.today()

    # Quelques locations
    v1 = flotte.obtenir_vehicule("DK-1234-AA")
    loc1 = gestion.demarrer_location(
        v1, "Aminata Diop", CategorieClient.PARTICULIER,
        aujourdhui - timedelta(days=5), aujourdhui - timedelta(days=1),
    )
    gestion.retourner_vehicule(loc1.id_location, aujourdhui - timedelta(days=1), km_parcourus=350)

    v2 = flotte.obtenir_vehicule("DK-2222-BB")
    loc2 = gestion.demarrer_location(
        v2, "Entreprise SENTRANS", CategorieClient.ENTREPRISE,
        aujourdhui - timedelta(days=2), aujourdhui + timedelta(days=3),
    )

    v3 = flotte.obtenir_vehicule("DK-4444-CA")
    loc3 = gestion.demarrer_location(
        v3, "Ibrahima Ndao", CategorieClient.EVENEMENTIEL,
        aujourdhui - timedelta(days=10), aujourdhui - timedelta(days=8),
    )
    # retour en retard de 3 jours -> pénalité
    gestion.retourner_vehicule(loc3.id_location, aujourdhui - timedelta(days=5), km_parcourus=120)

    # Un entretien
    v4 = flotte.obtenir_vehicule("DK-9012-AC")
    v4.rouler(11_000)  # dépasse le seuil -> passe EN_MAINTENANCE
    v4.ajouter_entretien(TypeEntretien.REVISION, cout=45000, description="Révision des 10000 km")

    # Gestion d'une erreur métier (véhicule déjà loué)
    try:
        gestion.demarrer_location(
            v2, "Un autre client", CategorieClient.PARTICULIER,
            aujourdhui, aujourdhui + timedelta(days=2),
        )
    except ErreurMetierBase as exc:
        logger.warning("Erreur métier attendue capturée : %s", exc)

    # Rapports
    print(rapport_disponibilite_texte(flotte, aujourdhui))
    print()
    print(rapport_entretien_requis(flotte))

    # Persistance
    sauvegarder_flotte_json(flotte, str(chemin_json))
    exporter_locations_csv(gestion.locations, str(chemin_csv))

    creer_tables(chemin_db)
    synchroniser_depuis_flotte(chemin_db, flotte, gestion)

    print("\n=== Véhicules disponibles aujourd'hui (requête SQL) ===")
    for row in vehicules_disponibles_a_date(chemin_db, aujourdhui):
        print(f"  {row}")

    print("\n=== Chiffre d'affaires par type de véhicule (requête SQL) ===")
    for row in chiffre_affaires_par_categorie_vehicule(chemin_db):
        print(f"  {row}")

    print("\n=== Locations en retard (requête SQL) ===")
    for row in locations_en_retard(chemin_db, aujourdhui):
        print(f"  {row}")

    # Rechargement JSON pour prouver la persistance
    flotte_rechargee = charger_flotte_json(str(chemin_json))
    print(f"\nFlotte rechargée depuis JSON : {len(flotte_rechargee)} véhicules.")


if __name__ == "__main__":
    executer_demo()
