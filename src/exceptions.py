"""
Module exceptions.py
Auteur assigné : Abdoul Basse

Exceptions métier personnalisées. On évite volontairement tout "except:" nu
dans le reste du projet : chaque cas d'erreur métier a sa propre classe.
"""


class ErreurMetierBase(Exception):
    """Classe de base pour toutes les exceptions métier du projet."""


class VehiculeIndisponibleError(ErreurMetierBase):
    """Levée quand on tente de louer un véhicule qui n'est pas DISPONIBLE."""


class EntretienRequisError(ErreurMetierBase):
    """Levée quand une opération est refusée car le véhicule nécessite un entretien."""


class DonneesInvalidesError(ErreurMetierBase):
    """Levée quand une donnée fournie par l'utilisateur est invalide
    (immatriculation vide, kilométrage négatif, dates incohérentes, etc.)."""


class LocationInexistanteError(ErreurMetierBase):
    """Levée quand on cherche une location qui n'existe pas dans le système."""
