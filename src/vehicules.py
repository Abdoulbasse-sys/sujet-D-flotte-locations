"""
Module vehicules.py
Auteur assigné : Abdoul Basse

Contient :
- Entretien : objet créé et possédé exclusivement par un véhicule (COMPOSITION).
- VehiculeBase (ABC) : classe abstraite mère de tous les véhicules.
- Voiture, Utilitaire, Moto : classes filles concrètes.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import List

from .enums import StatutVehicule, TypeEntretien
from .exceptions import DonneesInvalidesError

logger = logging.getLogger(__name__)


@dataclass
class Entretien:
    """Une opération d'entretien. Un Entretien n'existe jamais hors d'un véhicule :
    c'est le véhicule lui-même qui le crée -> relation de COMPOSITION."""

    type_entretien: TypeEntretien
    date_entretien: date
    kilometrage_au_moment: int
    cout: float
    description: str = ""

    def __post_init__(self) -> None:
        if self.kilometrage_au_moment < 0:
            raise DonneesInvalidesError("Le kilométrage d'entretien ne peut pas être négatif.")
        if self.cout < 0:
            raise DonneesInvalidesError("Le coût d'entretien ne peut pas être négatif.")


class VehiculeBase(ABC):
    """Classe abstraite mère de tous les véhicules de la flotte.

    Impose un contrat via deux méthodes abstraites :
    calculer_tarif_jour() et necessite_entretien().
    """

    SEUIL_KM_ENTRETIEN = 10_000  # km parcourus depuis le dernier entretien

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 kilometrage: int = 0) -> None:
        if not immatriculation or not immatriculation.strip():
            raise DonneesInvalidesError("L'immatriculation est obligatoire.")
        if kilometrage < 0:
            raise DonneesInvalidesError("Le kilométrage ne peut pas être négatif.")

        self.immatriculation: str = immatriculation.strip().upper()
        self.marque: str = marque
        self.modele: str = modele
        self.kilometrage: int = kilometrage
        self.statut: StatutVehicule = StatutVehicule.DISPONIBLE
        self._historique_entretiens: List[Entretien] = []  # composition
        self._km_au_dernier_entretien: int = kilometrage

    # --- méthodes abstraites : contrat imposé aux classes filles ---
    @abstractmethod
    def calculer_tarif_jour(self, categorie_client: "CategorieClient") -> float:  # noqa: F821
        """Retourne le tarif journalier de location, dépendant du type de véhicule
        et de la catégorie du client."""
        raise NotImplementedError

    @abstractmethod
    def necessite_entretien(self) -> bool:
        """Indique si le véhicule doit passer en entretien (règle propre au type)."""
        raise NotImplementedError

    # --- composition : le véhicule crée et possède ses Entretien ---
    def ajouter_entretien(self, type_entretien: TypeEntretien, cout: float,
                           description: str = "") -> Entretien:
        """Crée un nouvel Entretien pour CE véhicule (composition : le véhicule
        est responsable du cycle de vie de ses entretiens)."""
        entretien = Entretien(
            type_entretien=type_entretien,
            date_entretien=date.today(),
            kilometrage_au_moment=self.kilometrage,
            cout=cout,
            description=description,
        )
        self._historique_entretiens.append(entretien)
        self._km_au_dernier_entretien = self.kilometrage
        self.statut = StatutVehicule.DISPONIBLE
        logger.info(
            "Entretien %s enregistré pour %s (coût: %.2f FCFA)",
            type_entretien.name, self.immatriculation, cout,
        )
        return entretien

    @property
    def historique_entretiens(self) -> List[Entretien]:
        return list(self._historique_entretiens)

    def km_depuis_dernier_entretien(self) -> int:
        return self.kilometrage - self._km_au_dernier_entretien

    def jours_depuis_dernier_entretien(self) -> int | None:
        """Nombre de jours écoulés depuis le dernier entretien enregistré.
        Retourne None si le véhicule n'a encore jamais eu d'entretien."""
        if not self._historique_entretiens:
            return None
        derniere_date = self._historique_entretiens[-1].date_entretien
        return (date.today() - derniere_date).days

    def rouler(self, km: int) -> None:
        """Incrémente le kilométrage du véhicule (utilisé lors d'un retour de location)."""
        if km < 0:
            raise DonneesInvalidesError("Le kilométrage parcouru ne peut pas être négatif.")
        self.kilometrage += km
        if self.necessite_entretien():
            self.statut = StatutVehicule.EN_MAINTENANCE
            logger.warning("%s nécessite désormais un entretien.", self.immatriculation)

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}({self.immatriculation}, "
                f"{self.marque} {self.modele}, statut={self.statut.value})")


class Voiture(VehiculeBase):
    """Véhicule de tourisme."""

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 nb_places: int, tarif_base: float, kilometrage: int = 0) -> None:
        super().__init__(immatriculation, marque, modele, kilometrage)
        if nb_places <= 0:
            raise DonneesInvalidesError("Le nombre de places doit être positif.")
        self.nb_places = nb_places
        self.tarif_base = tarif_base

    def calculer_tarif_jour(self, categorie_client) -> float:
        from .enums import CategorieClient
        multiplicateurs = {
            CategorieClient.PARTICULIER: 1.0,
            CategorieClient.ENTREPRISE: 0.85,   # tarif négocié
            CategorieClient.EVENEMENTIEL: 1.30,  # majoration événementielle
        }
        return round(self.tarif_base * multiplicateurs[categorie_client], 2)

    def necessite_entretien(self) -> bool:
        return self.km_depuis_dernier_entretien() >= self.SEUIL_KM_ENTRETIEN


class Utilitaire(VehiculeBase):
    """Camionnette / véhicule utilitaire de transport de marchandises."""

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 capacite_charge_kg: float, tarif_base: float,
                 kilometrage: int = 0) -> None:
        super().__init__(immatriculation, marque, modele, kilometrage)
        if capacite_charge_kg <= 0:
            raise DonneesInvalidesError("La capacité de charge doit être positive.")
        self.capacite_charge_kg = capacite_charge_kg
        self.tarif_base = tarif_base

    def calculer_tarif_jour(self, categorie_client) -> float:
        from .enums import CategorieClient
        multiplicateurs = {
            CategorieClient.PARTICULIER: 1.10,
            CategorieClient.ENTREPRISE: 0.90,
            CategorieClient.EVENEMENTIEL: 1.20,
        }
        return round(self.tarif_base * multiplicateurs[categorie_client], 2)

    def necessite_entretien(self) -> bool:
        # Les utilitaires sont plus sollicités : seuil plus bas
        return self.km_depuis_dernier_entretien() >= (self.SEUIL_KM_ENTRETIEN * 0.7)


class Moto(VehiculeBase):
    """Deux-roues motorisé."""

    def __init__(self, immatriculation: str, marque: str, modele: str,
                 cylindree_cc: int, tarif_base: float, kilometrage: int = 0) -> None:
        super().__init__(immatriculation, marque, modele, kilometrage)
        if cylindree_cc <= 0:
            raise DonneesInvalidesError("La cylindrée doit être positive.")
        self.cylindree_cc = cylindree_cc
        self.tarif_base = tarif_base

    def calculer_tarif_jour(self, categorie_client) -> float:
        from .enums import CategorieClient
        multiplicateurs = {
            CategorieClient.PARTICULIER: 1.0,
            CategorieClient.ENTREPRISE: 0.95,
            CategorieClient.EVENEMENTIEL: 1.40,
        }
        return round(self.tarif_base * multiplicateurs[categorie_client], 2)

    def necessite_entretien(self) -> bool:
        return self.km_depuis_dernier_entretien() >= (self.SEUIL_KM_ENTRETIEN * 0.5)