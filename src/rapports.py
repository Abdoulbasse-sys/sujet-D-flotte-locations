"""
Module rapports.py
Auteur assigné : Lamine Ekoye Diatta

Génère les rapports textuels demandés par le sujet :
- disponibilité de la flotte à une date donnée
- véhicules nécessitant un entretien
"""

from __future__ import annotations

from datetime import date
from typing import List

from .flotte import Flotte
from .vehicules import VehiculeBase


def rapport_disponibilite_texte(flotte: Flotte, a_date: date) -> str:
    lignes = [f"=== Rapport de disponibilité — {flotte.nom} — {a_date.isoformat()} ==="]
    compteur = flotte.rapport_disponibilite()
    for statut, nb in compteur.items():
        lignes.append(f"  {statut:<15} : {nb} véhicule(s)")
    lignes.append(f"  TOTAL           : {len(flotte)} véhicule(s)")
    return "\n".join(lignes)


def rapport_entretien_requis(flotte: Flotte) -> str:
    vehicules: List[VehiculeBase] = flotte.vehicules_necessitant_entretien()
    if not vehicules:
        return "Aucun véhicule ne nécessite d'entretien actuellement."
    lignes = ["=== Véhicules nécessitant un entretien ==="]
    for v in vehicules:
        lignes.append(
            f"  {v.immatriculation} ({v.marque} {v.modele}) — "
            f"{v.km_depuis_dernier_entretien()} km depuis dernier entretien"
        )
    return "\n".join(lignes)
