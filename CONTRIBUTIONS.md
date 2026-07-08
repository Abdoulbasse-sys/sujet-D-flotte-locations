# Contributions au projet

## Membres du groupe
- Abdoul Basse — @A_COMPLETER_PSEUDO_GITHUB
- Omar Ngalla Diagne — @A_COMPLETER_PSEUDO_GITHUB
- Lamine Ekoye Diatta — @A_COMPLETER_PSEUDO_GITHUB

## Répartition du travail

| Membre | Modules / classes développés | Contribution estimée |
|--------|-------------------------------|----------------------|
| Abdoul Basse | `enums.py`, `exceptions.py`, `vehicules.py` (VehiculeBase, Voiture, Utilitaire, Moto, Entretien) | 33% |
| Omar Ngalla Diagne | `flotte.py` (Flotte), `location.py` (Location, GestionLocations), `persistence.py` (JSON/CSV) | 33% |
| Lamine Ekoye Diatta | `database.py` (SQLite, requêtes métier), `rapports.py`, `main.py` (intégration), README | 34% |

## Répartition par phase

| Phase | Responsable principal |
|-----------------------------------|------------------------|
| Conception (diagramme de classes) | Abdoul Basse |
| Implémentation POO | Abdoul Basse |
| Persistance fichiers (JSON/CSV) | Omar Ngalla Diagne |
| Persistance SQL | Lamine Ekoye Diatta |
| Tests / gestion des exceptions | Omar Ngalla Diagne + Abdoul Basse |
| README / documentation | Lamine Ekoye Diatta |

## Difficultés rencontrées et résolution

1. **Choix agrégation vs composition** : au départ hésitation sur la relation
   Flotte–Vehicule. Résolu en fixant la règle : la Flotte ne crée jamais les
   véhicules (agrégation), alors que le Vehicule crée lui-même ses Entretien
   (composition, cycle de vie lié).
2. **Calcul de la pénalité de retard** : décidé de comparer `date_retour_reel`
   à `date_fin_prevue` dans `GestionLocations.retourner_vehicule()`, avec un
   tarif fixe par jour de retard (`PENALITE_PAR_JOUR_RETARD`).

> ⚠️ À COMPLÉTER PAR L'ÉQUIPE avant l'envoi : pseudos GitHub réels, et adapter
> ce fichier si la répartition change pendant le développement. Chaque membre
> doit pouvoir défendre EXACTEMENT le code qui lui est attribué ici.
