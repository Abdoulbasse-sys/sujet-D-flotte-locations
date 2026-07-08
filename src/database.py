"""
Module database.py
Auteur assigné : Lamine Ekoye Diatta

Persistance SQLite : deux tables liées par clé étrangère (vehicules, locations)
et au moins 4 requêtes métier (pas de simple SELECT *).
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import date
from typing import Iterator, List, Tuple

from .exceptions import DonneesInvalidesError
from .flotte import Flotte
from .location import GestionLocations

logger = logging.getLogger(__name__)


@contextmanager
def obtenir_connexion(chemin_db: str) -> Iterator[sqlite3.Connection]:
    """Fournit une connexion SQLite dans un contexte 'with' (aucune fuite de ressource)."""
    conn = sqlite3.connect(chemin_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def creer_tables(chemin_db: str) -> None:
    """Crée les deux tables liées si elles n'existent pas déjà."""
    with obtenir_connexion(chemin_db) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vehicules (
                immatriculation TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                marque TEXT NOT NULL,
                modele TEXT NOT NULL,
                kilometrage INTEGER NOT NULL,
                statut TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id_location TEXT PRIMARY KEY,
                immatriculation TEXT NOT NULL,
                client_nom TEXT NOT NULL,
                categorie_client TEXT NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin_prevue TEXT NOT NULL,
                date_retour_reel TEXT,
                montant_total REAL NOT NULL DEFAULT 0,
                penalite REAL NOT NULL DEFAULT 0,
                cloturee INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (immatriculation) REFERENCES vehicules (immatriculation)
            );
        """)
    logger.info("Tables SQLite créées/vérifiées dans %s.", chemin_db)


def synchroniser_depuis_flotte(chemin_db: str, flotte: Flotte,
                                gestion_locations: GestionLocations) -> None:
    """Écrit l'état courant de la flotte et des locations dans la base SQLite."""
    with obtenir_connexion(chemin_db) as conn:
        for v in flotte.vehicules:
            conn.execute(
                """INSERT INTO vehicules (immatriculation, type, marque, modele, kilometrage, statut)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(immatriculation) DO UPDATE SET
                     kilometrage=excluded.kilometrage, statut=excluded.statut;""",
                (v.immatriculation, v.__class__.__name__, v.marque, v.modele,
                 v.kilometrage, v.statut.value),
            )
        for loc in gestion_locations.locations:
            conn.execute(
                """INSERT INTO locations
                   (id_location, immatriculation, client_nom, categorie_client,
                    date_debut, date_fin_prevue, date_retour_reel, montant_total,
                    penalite, cloturee)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id_location) DO UPDATE SET
                     date_retour_reel=excluded.date_retour_reel,
                     montant_total=excluded.montant_total,
                     penalite=excluded.penalite,
                     cloturee=excluded.cloturee;""",
                (loc.id_location, loc.vehicule.immatriculation, loc.client_nom,
                 loc.categorie_client.value, loc.date_debut.isoformat(),
                 loc.date_fin_prevue.isoformat(),
                 loc.date_retour_reel.isoformat() if loc.date_retour_reel else None,
                 loc.montant_total, loc.penalite, int(loc.cloturee)),
            )
    logger.info("Synchronisation SQLite terminée.")


# ---------- Requêtes métier (4 requêtes différentes, pas de SELECT *) ----------

def vehicules_disponibles_a_date(chemin_db: str, a_date: date) -> List[Tuple[str, str, str]]:
    """Véhicules DISPONIBLES et non engagés dans une location active à la date donnée."""
    with obtenir_connexion(chemin_db) as conn:
        curseur = conn.execute(
            """SELECT v.immatriculation, v.type, v.marque
               FROM vehicules v
               WHERE v.statut = 'DISPONIBLE'
                 AND v.immatriculation NOT IN (
                     SELECT l.immatriculation FROM locations l
                     WHERE l.cloturee = 0
                       AND date(?) BETWEEN date(l.date_debut) AND date(l.date_fin_prevue)
                 );""",
            (a_date.isoformat(),),
        )
        return curseur.fetchall()


def chiffre_affaires_par_categorie_vehicule(chemin_db: str) -> List[Tuple[str, float]]:
    """Somme des montants encaissés (hors pénalités), groupée par type de véhicule."""
    with obtenir_connexion(chemin_db) as conn:
        curseur = conn.execute(
            """SELECT v.type, ROUND(SUM(l.montant_total), 2) AS chiffre_affaires
               FROM locations l
               JOIN vehicules v ON v.immatriculation = l.immatriculation
               WHERE l.cloturee = 1
               GROUP BY v.type
               ORDER BY chiffre_affaires DESC;""",
        )
        return curseur.fetchall()


def historique_entretien_par_vehicule(chemin_db: str, immatriculation: str) -> List[Tuple]:
    """Retourne le kilométrage courant et le statut d'un véhicule donné
    (l'historique détaillé des entretiens vit en mémoire/JSON, ceci relie
    l'identité SQL du véhicule à son état courant pour le rapport)."""
    with obtenir_connexion(chemin_db) as conn:
        curseur = conn.execute(
            """SELECT immatriculation, kilometrage, statut
               FROM vehicules WHERE immatriculation = ?;""",
            (immatriculation,),
        )
        resultat = curseur.fetchall()
        if not resultat:
            raise DonneesInvalidesError(f"Véhicule {immatriculation} absent de la base.")
        return resultat


def locations_en_retard(chemin_db: str, a_date: date) -> List[Tuple]:
    """Locations actives dont la date de fin prévue est dépassée (retard en cours)."""
    with obtenir_connexion(chemin_db) as conn:
        curseur = conn.execute(
            """SELECT id_location, immatriculation, client_nom, date_fin_prevue
               FROM locations
               WHERE cloturee = 0 AND date(date_fin_prevue) < date(?);""",
            (a_date.isoformat(),),
        )
        return curseur.fetchall()
