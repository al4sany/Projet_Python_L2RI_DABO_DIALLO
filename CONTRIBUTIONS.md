# Contributions au projet

## Membres du groupe
- Nom Prénom 1 — alassane dabo
- Nom Prénom 2 — aziz diallo

## Répartition du travail

| Membre | Modules / classes développés | Contribution estimée |
|--------|-------------------------------|----------------------|
| dabo  | Conception de la Base SQL, `database/connection.py`, `database/queries.py` et gestion du logging. | 34% |
| aziz | Conception POO de la classe abstraite `DocumentBase` et des classes dérivées (`Livre`, `Revue`, `DVD`, `Memoire`). | 33% |
|        | Gestion des relations (Composition `Adherent`/`Emprunt` et Agrégation `Bibliotheque`), gestion des exports (JSON / CSV). | 33% |

## Répartition par phase

| Phase                            | Responsable principal |
|-----------------------------------|------------------------|
| Conception (diagramme de classes) | alassane et aziz   |
| Implémentation POO                | alassane                |
| Persistance fichiers (JSON/CSV)   | alassane                 |
| Persistance SQL                   | aziz                 |
| Tests / gestion des exceptions     | alassane et aziz          |
| README / documentation            | alassane aider de l'ia             |

## Difficultés rencontrées et résolution
1. **Gestion de la concurrence sur le double emprunt** : Nous avons résolu cela en implémentant des exceptions métier personnalisées (`DocumentException`) levées au moment de la vérification de l'état du document avant tout emprunt.
2. **Utilisation du Context Manager SQL avec SQLite** : Pour éviter les fuites de connexion, nous avons mis en place la classe `DBConnection` héritant du protocole `__enter__` et `__exit__` de Python, garantissant que la connexion est fermée automatiquement, même en cas d'erreur.
