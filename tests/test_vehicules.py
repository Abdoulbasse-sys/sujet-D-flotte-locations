"""Tests unitaires de base. Lancer avec : pytest"""

import pytest

from src.enums import CategorieClient
from src.exceptions import DonneesInvalidesError, VehiculeIndisponibleError
from src.flotte import Flotte
from src.location import GestionLocations
from src.vehicules import Voiture
from datetime import date, timedelta


def test_creation_voiture_invalide():
    with pytest.raises(DonneesInvalidesError):
        Voiture("", "Toyota", "Yaris", 5, 20000)


def test_calcul_tarif_entreprise_moins_cher_que_particulier():
    v = Voiture("DK-0001-XX", "Toyota", "Yaris", 5, 20000)
    tarif_particulier = v.calculer_tarif_jour(CategorieClient.PARTICULIER)
    tarif_entreprise = v.calculer_tarif_jour(CategorieClient.ENTREPRISE)
    assert tarif_entreprise < tarif_particulier


def test_location_vehicule_deja_loue_leve_exception():
    flotte = Flotte("Test")
    v = Voiture("DK-0002-XX", "Toyota", "Yaris", 5, 20000)
    flotte.ajouter_vehicule(v)
    gestion = GestionLocations()

    gestion.demarrer_location(v, "Client A", CategorieClient.PARTICULIER,
                               date.today(), date.today() + timedelta(days=2))

    with pytest.raises(VehiculeIndisponibleError):
        gestion.demarrer_location(v, "Client B", CategorieClient.PARTICULIER,
                                   date.today(), date.today() + timedelta(days=1))
