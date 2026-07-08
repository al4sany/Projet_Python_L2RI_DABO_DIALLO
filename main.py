import os
import logging
from datetime import datetime, timedelta

# Configuration du logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/bibliotheque.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

from exceptions_enums import CategorieAdherent, StatutDocument, DocumentException, EmpruntException
from documents import Livre, Revue, DVD, Memoire
from emprunts import Adherent
from bibliotheque import Bibliotheque
from database.connection import initialiser_bdd
from database.queries import (
    synchroniser_document_sql,
    enregistrer_emprunt_sql,
    enregistrer_retour_sql,
    obtenir_emprunts_en_retard,
    obtenir_top_documents_empruntes,
    obtenir_historique_adherent,
    obtenir_statistiques_globales,
    exporter_retards_csv
)

def executer_demonstration():
    logging.info("=== DEBUT DE LA SIMULATION - GROUPE: ALASSANE DABO & ABDOUL AZIZ DIALLO ===")
    
    # 0. Base de données
    initialiser_bdd()

    # 1. Bibliothèque
    bu = Bibliotheque("Bibliothèque ISI Dakar")
    docs = [
        Livre("Introduction à l'Algorithmique", "LIV001", "Thomas Cormen"),
        Livre("Réseaux et Transmissions", "LIV002", "Andrew Tanenbaum"),
        Livre("Python pour les Data Scientists", "LIV003", "Wes McKinney"),
        Revue("Techno Réseau Mensuel", "REV001", 104),
        Revue("Science et Avenir Hors-série", "REV002", 42),
        DVD("Le Cœur du Réseau", "DVD001", "Jean-Luc Godard"),
        DVD("Algorithmes de demain", "DVD002", "Alan Turing"),
        Memoire("Mise en place d'un SDN sécurisé", "MEM001", "Amadou Diop")
    ]

    for doc in docs:
        bu.ajouter_document(doc)
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)

    bu.exporter_catalogue_json("data/catalogue.json")

    # 2. Adhérents
    etudiant = Adherent("Fatou Diome", "ADH001", CategorieAdherent.ETUDIANT)
    enseignant = Adherent("Dr. Moustapha Ndiaye", "ADH002", CategorieAdherent.ENSEIGNANT)
    externe = Adherent("Mariama Ba", "ADH003", CategorieAdherent.EXTERNE)

    aujourdhui = datetime.now()
    il_y_a_30_jours = aujourdhui - timedelta(days=30)
    il_y_a_15_jours = aujourdhui - timedelta(days=15)

    # Simulation d'emprunts
    try:
        doc = bu.chercher_document("LIV001")
        doc.emprunter()
        emprunt = etudiant.ajouter_emprunt(doc, il_y_a_30_jours)
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, etudiant.identifiant, etudiant.nom, etudiant.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        logging.error(f"Erreur : {e}")

    try:
        doc = bu.chercher_document("REV001")
        doc.emprunter()
        emprunt = enseignant.ajouter_emprunt(doc, il_y_a_15_jours)
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, enseignant.identifiant, enseignant.nom, enseignant.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        logging.error(f"Erreur : {e}")

    # Retour avec amende
    try:
        amende = etudiant.retourner_document("LIV001", aujourdhui)
        doc = bu.chercher_document("LIV001")
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_retour_sql("LIV001", etudiant.identifiant, aujourdhui.strftime("%Y-%m-%d %H:%M:%S"), amende)
        logging.info(f"Retour de LIV001 par {etudiant.nom}. Amende payée : {amende} €")
    except Exception as e:
        logging.error(f"Erreur : {e}")

    # Exports
    date_ref_str = aujourdhui.strftime("%Y-%m-%d %H:%M:%S")
    exporter_retards_csv("data/emprunts_en_retard.csv", date_ref_str)
    bu.exporter_catalogue_json("data/catalogue.json")

    # Rapports SQL
    print("\n--- STATISTIQUES GLOBALES (SQL) ---")
    stats = obtenir_statistiques_globales()
    print(f"Total des amendes perçues : {stats['total_amendes']} €")
    print(f"Nombre d'emprunts en cours : {stats['emprunts_actifs']}")

    logging.info("=== FIN DE LA SIMULATION ===")

if __name__ == "__main__":
    executer_demonstration()
