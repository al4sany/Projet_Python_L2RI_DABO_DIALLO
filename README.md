# Projet de Fin de Semestre L2 RI — Gestion de Bibliothèque Universitaire (BU)

Ce projet est réalisé dans le cadre du module **POO & Persistance des Données** (Licence 2 - Réseaux Informatiques) à l'**ISI Dakar** (Année universitaire 2025-2026).

##  Membres du Groupe
- **Alassane Dabo**
- **Abdoul Aziz Diallo**

---

## Fonctionnalités du Projet

Ce projet implémente le **Sujet B : Gestion de bibliothèque universitaire** :
1. **Catalogue mixte de documents** (Livre, Revue, DVD, Mémoire) héritant d'une classe abstraite.
2. **Cycle complet d'un emprunt** (emprunt par l'adhérent, retour avec gestion du statut, et blocage si indisponible).
3. **Calcul d'amende différencié** selon le type de document et la catégorie d'adhérent (les enseignants bénéficient d'une semaine supplémentaire sans pénalité).
4. **Persistance double** :
   - Fichiers **JSON** : Sauvegarde et rechargement dynamique du catalogue.
   - Fichiers **CSV** : Exportation de la liste des emprunts en retard.
   - Base de données **SQLite** : Tables `documents` et `emprunts` avec 4 requêtes métiers complexes.
5. **Gestion robuste des exceptions** et traçabilité complète via le module de **Logging** dans `logs/bibliotheque.log`.

---

##  Architecture du Projet

```text
projet_bu/
├── data/
│   ├── catalogue.json             # Sauvegarde JSON
│   └── emprunts_en_retard.csv     # Export CSV
├── database/
│   ├── __init__.py
│   ├── bibliotheque.db            # Base de données SQLite
│   ├── connection.py              # Context Manager SQLite
│   └── queries.py                 # Requêtes métiers SQL
├── logs/
│   └── bibliotheque.log           # Journal des opérations
├── CONTRIBUTIONS.md               # Répartition des tâches du groupe
├── README.md                      # Guide d'utilisation
├── exceptions_enums.py            # Enums & Exceptions
├── documents.py                   # Modélisation POO des Documents
├── emprunts.py                    # Classes Adherent et Emprunt
├── bibliotheque.py                # Classe Bibliotheque
├── requirements.txt               # Dépendances (standard Python uniquement)
└── main.py                        # Script de démonstration
```

---

## Installation et Exécution

1. **Se positionner dans le dossier** :
   ```bash
   cd projet_bu
   ```

2. **Lancer la démonstration** :
   ```bash
   python3 main.py
   ```
