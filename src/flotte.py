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
        if not nom or not nom.strip():
            raise DonneesInvalidesError("Le nom de la flotte est obligatoire.")
        self.nom = nom.strip()
        self._vehicules: Dict[str, VehiculeBase] = {}

    def ajouter_vehicule(self, vehicule: VehiculeBase) -> None:
        """Ajoute un véhicule déjà créé à la flotte."""
        if not isinstance(vehicule, VehiculeBase):
            raise DonneesInvalidesError(
                "L'objet ajouté à la flotte doit être un VehiculeBase."
            )
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
        """Retourne les véhicules DISPONIBLES selon leur statut courant.

        Le paramètre a_date n'est pas encore utilisé ici : croiser avec les
        locations actives à une date précise nécessiterait d'importer
        GestionLocations, ce qui créerait un cycle d'import avec location.py
        (qui importe déjà les types de vehicules.py). C'est
        database.vehicules_disponibles_a_date() qui fait ce calcul précis en
        croisant les deux tables SQL. Le paramètre est conservé ici pour que
        la signature reste stable si ce croisement est un jour rapatrié en
        mémoire.
        """
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

    def __contains__(self, immatriculation: str) -> bool:
        return immatriculation in self._vehicules

    def __iter__(self):
        return iter(self._vehicules.values())

    def __repr__(self) -> str:
        return f"Flotte(nom={self.nom!r}, {len(self._vehicules)} véhicule(s))"