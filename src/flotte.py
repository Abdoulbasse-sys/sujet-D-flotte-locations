"""
Module flotte.py
Auteur assigné : Omar Ngalla Diagne

Flotte : objet conteneur qui reçoit des véhicules créés en dehors de lui
-> relation d'AGRÉGATION (la Flotte ne crée pas les véhicules, elle les reçoit).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Dict, List, Optional

from .enums import StatutVehicule
from .exceptions import DonneesInvalidesError
from .vehicules import VehiculeBase

logger = logging.getLogger(__name__)


class Flotte:
    """Conteneur agrégeant des véhicules existants (agrégation, pas composition :
    les véhicules peuvent exister indépendamment de la Flotte)."""

    def __init__(self, nom: str) -> None:
        self.nom = nom
        self._vehicules: Dict[str, VehiculeBase] = {}

    def ajouter_vehicule(self, vehicule: VehiculeBase) -> None:
        """Ajoute un véhicule déjà créé à la flotte."""
        if vehicule.immatriculation in self._vehicules:
            raise DonneesInvalidesError(
                f"Un véhicule avec l'immatriculation {vehicule.immatriculation} existe déjà."
            )
        self._vehicules[vehicule.immatriculation] = vehicule
        logger.info("Véhicule %s ajouté à la flotte %s.", vehicule.immatriculation, self.nom)

    def retirer_vehicule(self, immatriculation: str) -> None:
        if immatriculation not in self._vehicules:
            raise DonneesInvalidesError(f"Véhicule {immatriculation} introuvable dans la flotte.")
        del self._vehicules[immatriculation]

    def obtenir_vehicule(self, immatriculation: str) -> VehiculeBase:
        try:
            return self._vehicules[immatriculation]
        except KeyError as exc:
            raise DonneesInvalidesError(f"Véhicule {immatriculation} introuvable.") from exc

    @property
    def vehicules(self) -> List[VehiculeBase]:
        return list(self._vehicules.values())

    def vehicules_disponibles(self, a_date: Optional[date] = None) -> List[VehiculeBase]:
        """Retourne les véhicules DISPONIBLES. Le paramètre a_date est conservé
        pour compatibilité avec la couche locations (statut recalculé en croisant
        avec les locations actives à cette date, voir rapports.py)."""
        return [v for v in self._vehicules.values() if v.statut == StatutVehicule.DISPONIBLE]

    def vehicules_necessitant_entretien(self) -> List[VehiculeBase]:
        return [v for v in self._vehicules.values() if v.necessite_entretien()]

    def rapport_disponibilite(self) -> Dict[str, int]:
        """Petit rapport texte : nombre de véhicules par statut."""
        rapport: Dict[str, int] = {statut.value: 0 for statut in StatutVehicule}
        for v in self._vehicules.values():
            rapport[v.statut.value] += 1
        return rapport

    def __len__(self) -> int:
        return len(self._vehicules)
