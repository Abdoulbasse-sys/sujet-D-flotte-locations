"""
Module location.py
Auteur assigné : Omar Ngalla Diagne

Gère le cycle complet d'une location : réservation, départ, retour,
calcul du tarif, et pénalité de retard (bonus).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

from .enums import CategorieClient, StatutVehicule
from .exceptions import (
    DonneesInvalidesError,
    LocationInexistanteError,
    VehiculeIndisponibleError,
)
from .vehicules import VehiculeBase

logger = logging.getLogger(__name__)

PENALITE_PAR_JOUR_RETARD = 5000.0  # FCFA / jour de retard


@dataclass
class Location:
    """Un contrat de location entre la flotte et un client."""

    vehicule: VehiculeBase
    client_nom: str
    categorie_client: CategorieClient
    date_debut: date
    date_fin_prevue: date
    id_location: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    date_retour_reel: Optional[date] = None
    cloturee: bool = False
    montant_total: float = 0.0
    penalite: float = 0.0

    def __post_init__(self) -> None:
        if self.date_fin_prevue < self.date_debut:
            raise DonneesInvalidesError("La date de fin prévue ne peut pas précéder la date de début.")

    @property
    def duree_prevue_jours(self) -> int:
        return max((self.date_fin_prevue - self.date_debut).days, 1)


class GestionLocations:
    """Gère l'ensemble des locations : démarrage, retour, calcul de tarifs et pénalités."""

    def __init__(self) -> None:
        self._locations: Dict[str, Location] = {}

    def demarrer_location(self, vehicule: VehiculeBase, client_nom: str,
                           categorie_client: CategorieClient,
                           date_debut: date, date_fin_prevue: date) -> Location:
        if vehicule.statut != StatutVehicule.DISPONIBLE:
            raise VehiculeIndisponibleError(
                f"Le véhicule {vehicule.immatriculation} n'est pas disponible "
                f"(statut actuel : {vehicule.statut.value})."
            )
        if not client_nom or not client_nom.strip():
            raise DonneesInvalidesError("Le nom du client est obligatoire.")

        location = Location(
            vehicule=vehicule,
            client_nom=client_nom.strip(),
            categorie_client=categorie_client,
            date_debut=date_debut,
            date_fin_prevue=date_fin_prevue,
        )
        vehicule.statut = StatutVehicule.LOUE
        self._locations[location.id_location] = location
        logger.info("Location %s démarrée pour %s (%s).",
                    location.id_location, client_nom, vehicule.immatriculation)
        return location

    def retourner_vehicule(self, id_location: str, date_retour: date,
                            km_parcourus: int) -> Location:
        location = self._obtenir(id_location)
        if location.cloturee:
            raise DonneesInvalidesError(f"La location {id_location} est déjà clôturée.")

        location.date_retour_reel = date_retour
        location.vehicule.rouler(km_parcourus)

        tarif_jour = location.vehicule.calculer_tarif_jour(location.categorie_client)
        location.montant_total = round(tarif_jour * location.duree_prevue_jours, 2)

        jours_retard = max((date_retour - location.date_fin_prevue).days, 0)
        location.penalite = round(jours_retard * PENALITE_PAR_JOUR_RETARD, 2)

        if location.vehicule.statut != StatutVehicule.EN_MAINTENANCE:
            location.vehicule.statut = StatutVehicule.DISPONIBLE
        location.cloturee = True

        logger.info(
            "Location %s clôturée : montant=%.2f, pénalité=%.2f (retard=%d j).",
            id_location, location.montant_total, location.penalite, jours_retard,
        )
        return location

    def _obtenir(self, id_location: str) -> Location:
        try:
            return self._locations[id_location]
        except KeyError as exc:
            raise LocationInexistanteError(f"Location {id_location} introuvable.") from exc

    @property
    def locations(self) -> List[Location]:
        return list(self._locations.values())

    def locations_actives(self) -> List[Location]:
        return [loc for loc in self._locations.values() if not loc.cloturee]

    def locations_periode(self, debut: date, fin: date) -> List[Location]:
        return [
            loc for loc in self._locations.values()
            if debut <= loc.date_debut <= fin
        ]
