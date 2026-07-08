"""
Module persistence.py
Auteur assigné : Omar Ngalla Diagne

Persistance JSON (export/import de l'état complet de la flotte) et
CSV (export des contrats de location).
"""

from __future__ import annotations

import csv
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .enums import CategorieClient, StatutVehicule
from .exceptions import DonneesInvalidesError
from .flotte import Flotte
from .location import Location
from .vehicules import Moto, Utilitaire, VehiculeBase, Voiture

logger = logging.getLogger(__name__)

_CLASSES_VEHICULE = {"Voiture": Voiture, "Utilitaire": Utilitaire, "Moto": Moto}


def _vehicule_vers_dict(v: VehiculeBase) -> Dict[str, Any]:
    base = {
        "type": v.__class__.__name__,
        "immatriculation": v.immatriculation,
        "marque": v.marque,
        "modele": v.modele,
        "kilometrage": v.kilometrage,
        "statut": v.statut.value,
    }
    if isinstance(v, Voiture):
        base.update({"nb_places": v.nb_places, "tarif_base": v.tarif_base})
    elif isinstance(v, Utilitaire):
        base.update({"capacite_charge_kg": v.capacite_charge_kg, "tarif_base": v.tarif_base})
    elif isinstance(v, Moto):
        base.update({"cylindree_cc": v.cylindree_cc, "tarif_base": v.tarif_base})
    return base


def _dict_vers_vehicule(d: Dict[str, Any]) -> VehiculeBase:
    type_v = d.get("type")
    if type_v not in _CLASSES_VEHICULE:
        raise DonneesInvalidesError(f"Type de véhicule inconnu dans le JSON : {type_v}")

    if type_v == "Voiture":
        v = Voiture(d["immatriculation"], d["marque"], d["modele"],
                    d["nb_places"], d["tarif_base"], d.get("kilometrage", 0))
    elif type_v == "Utilitaire":
        v = Utilitaire(d["immatriculation"], d["marque"], d["modele"],
                       d["capacite_charge_kg"], d["tarif_base"], d.get("kilometrage", 0))
    else:  # Moto
        v = Moto(d["immatriculation"], d["marque"], d["modele"],
                 d["cylindree_cc"], d["tarif_base"], d.get("kilometrage", 0))

    v.statut = StatutVehicule(d.get("statut", StatutVehicule.DISPONIBLE.value))
    return v


def sauvegarder_flotte_json(flotte: Flotte, chemin: str) -> None:
    """Exporte l'état complet de la flotte (tous les véhicules) en JSON."""
    donnees = {"nom_flotte": flotte.nom, "vehicules": [_vehicule_vers_dict(v) for v in flotte.vehicules]}
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
    logger.info("Flotte '%s' sauvegardée dans %s (%d véhicules).", flotte.nom, chemin, len(flotte))


def charger_flotte_json(chemin: str) -> Flotte:
    """Recharge une flotte complète depuis un fichier JSON."""
    path = Path(chemin)
    if not path.exists():
        raise DonneesInvalidesError(f"Fichier JSON introuvable : {chemin}")

    with open(chemin, "r", encoding="utf-8") as f:
        donnees = json.load(f)

    flotte = Flotte(donnees.get("nom_flotte", "Flotte importée"))
    for d in donnees.get("vehicules", []):
        flotte.ajouter_vehicule(_dict_vers_vehicule(d))
    logger.info("Flotte rechargée depuis %s (%d véhicules).", chemin, len(flotte))
    return flotte


def exporter_locations_csv(locations: List[Location], chemin: str,
                            debut: Optional[date] = None, fin: Optional[date] = None) -> int:
    """Exporte les contrats de location (actifs ou clôturés) sur une période donnée.
    Retourne le nombre de lignes exportées."""
    lignes_filtrees = [
        loc for loc in locations
        if (debut is None or loc.date_debut >= debut) and (fin is None or loc.date_debut <= fin)
    ]

    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_location", "immatriculation", "client", "categorie_client",
            "date_debut", "date_fin_prevue", "date_retour_reel",
            "montant_total", "penalite", "statut",
        ])
        for loc in lignes_filtrees:
            writer.writerow([
                loc.id_location,
                loc.vehicule.immatriculation,
                loc.client_nom,
                loc.categorie_client.value,
                loc.date_debut.isoformat(),
                loc.date_fin_prevue.isoformat(),
                loc.date_retour_reel.isoformat() if loc.date_retour_reel else "",
                loc.montant_total,
                loc.penalite,
                "cloturee" if loc.cloturee else "active",
            ])

    logger.info("Export CSV de %d locations vers %s.", len(lignes_filtrees), chemin)
    return len(lignes_filtrees)
