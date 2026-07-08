"""
Module enums.py
Auteur assigné : Abdoul Basse

Définit les énumérations utilisées dans tout le projet :
- StatutVehicule : état courant d'un véhicule de la flotte
- CategorieClient : catégorie tarifaire du client qui loue
- TypeEntretien : nature d'une opération d'entretien
"""

from enum import Enum, auto


class StatutVehicule(Enum):
    """État courant d'un véhicule dans la flotte."""
    DISPONIBLE = "DISPONIBLE"
    LOUE = "LOUE"
    EN_MAINTENANCE = "EN_MAINTENANCE"
    HORS_SERVICE = "HORS_SERVICE"


class CategorieClient(Enum):
    """Catégorie de client, utilisée pour moduler le tarif de location."""
    PARTICULIER = "PARTICULIER"
    ENTREPRISE = "ENTREPRISE"
    EVENEMENTIEL = "EVENEMENTIEL"


class TypeEntretien(Enum):
    """Nature d'une opération d'entretien effectuée sur un véhicule."""
    VIDANGE = auto()
    REVISION = auto()
    REPARATION = auto()
    CONTROLE_TECHNIQUE = auto()
