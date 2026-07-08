# Contributions au projet - Sujet B (Bibliothèque Universitaire)

## Membres du groupe
- Alassane Dabo — @alassane_dabo
- Abdoul Aziz Diallo — @abdoul_aziz_diallo

## Répartition du travail

| Membre | Modules / classes développés |
|--------|-------------------------------|----------------------|
| Alassane Dabo | Conception SQL, `database/connection.py`, `database/queries.py` et gestion des logs.
| Abdoul Aziz Diallo | Conception POO (`DocumentBase`, `Livre`, `Revue`, `DVD`, `Memoire`), Composition, exports JSON/CSV.

## Répartition par phase

| Phase                            | Responsable principal |
|-----------------------------------|------------------------|
| Conception (diagramme de classes) | Alassane Dabo & Abdoul Aziz Diallo |
| Implémentation POO                | Abdoul Aziz Diallo |
| Persistance fichiers (JSON/CSV)   | Abdoul Aziz Diallo |
| Persistance SQL                   | Alassane Dabo |
| Tests / gestion des exceptions     | Alassane Dabo & Abdoul Aziz Diallo |
| README / documentation            | Abdoul Aziz Diallo |

## Difficultés rencontrées et résolution
1. **Gestion des dates et des calculs de retards** : Les calculs de retards dynamiques ont été optimisés en utilisant le type `datetime` natif de Python et des validations strictes.
2. **Context Manager SQLite** : Nous avons implémenté un Context Manager personnalisé pour sécuriser les verrous de table SQLite lors des transactions d'emprunt et de retour.
