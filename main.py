import os
import logging
from datetime import datetime, timedelta

# Configurer le logger requis pour tracer les opérations critiques (exigence 3.3)
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
    logging.info("=== DEBUT DE LA SIMULATION / DEMONSTRATION ===")
    
    # 0. Initialiser la Base de données SQLite
    initialiser_bdd()

    # 1. Créer la bibliothèque et instancier des documents (Agrégation)
    bu = Bibliotheque("Bibliothèque Interuniversitaire ISI-Dakar")

    docs = [
        Livre("Introduction à l'Algorithmique", "LIV001", "Thomas Cormen"),
        Livre("Réseaux et Transmissions", "LIV002", "Andrew Tanenbaum"),
        Livre("Python pour les Data Scientists", "LIV003", "Wes McKinney"),
        Revue("Techno Réseau Mensuel", "REV001", 104),
        Revue("Science et Avenir Hors-série", "REV002", 42),
        DVD("Le Cœur du Réseau - Documentaire", "DVD001", "Jean-Luc Godard"),
        DVD("Algorithmes de demain", "DVD002", "Alan Turing"),
        Memoire("Mise en place d'un SDN sécurisé", "MEM001", "Amadou Diop")
    ]

    for doc in docs:
        bu.ajouter_document(doc)
        # Synchronisation immédiate avec la BDD SQL pour correspondre à notre catalogue
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)

    # 2. Sauvegarder le catalogue en JSON
    bu.exporter_catalogue_json("data/catalogue.json")

    # 3. Créer des Adhérents (Composition de leurs futurs emprunts)
    etudiant = Adherent("Fatou Diome", "ADH001", CategorieAdherent.ETUDIANT)
    enseignant = Adherent("Dr. Moustapha Ndiaye", "ADH002", CategorieAdherent.ENSEIGNANT)
    externe = Adherent("Mariama Ba", "ADH003", CategorieAdherent.EXTERNE)

    # Simulation de dates d'emprunt dans le passé pour créer des retards réalistes
    aujourdhui = datetime.now()
    il_y_a_15_jours = aujourdhui - timedelta(days=15)
    il_y_a_30_jours = aujourdhui - timedelta(days=30)

    # --- ENREGISTREMENT DES EMPRUNTS ---
    
    # Scénario A : Fatou (Étudiante) emprunte un Livre il y a 30 jours (Retard d'amende à prévoir)
    try:
        ref_doc = "LIV001"
        doc = bu.chercher_document(ref_doc)
        
        # Action POO
        doc.emprunter()  # Passe à EMPRUNTE
        emprunt = etudiant.ajouter_emprunt(doc, il_y_a_30_jours)
        
        # Synchronisation SQL
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, etudiant.identifiant, etudiant.nom, etudiant.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
        logging.info(f"Emprunt réussi : {etudiant.nom} a emprunté '{doc.titre}'")
    except Exception as e:
        logging.error(f"Échec de l'emprunt : {e}")

    # Scénario B : Dr. Ndiaye (Enseignant) emprunte une Revue il y a 15 jours (Retard d'amende à prévoir)
    try:
        ref_doc = "REV001"
        doc = bu.chercher_document(ref_doc)
        
        doc.emprunter()
        # Les enseignants ont droit à 7 jours de plus. Pour une Revue de 7 jours, ça fait 14 jours d'emprunt autorisé.
        # Emprunté il y a 15 jours, l'enseignant aura donc 1 jour de retard.
        emprunt = enseignant.ajouter_emprunt(doc, il_y_a_15_jours)
        
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, enseignant.identifiant, enseignant.nom, enseignant.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
        logging.info(f"Emprunt réussi : {enseignant.nom} a emprunté '{doc.titre}'")
    except Exception as e:
        logging.error(f"Échec de l'emprunt : {e}")

    # Scénario C : Mariama (Externe) emprunte un DVD aujourd'hui (Pas de retard)
    try:
        ref_doc = "DVD001"
        doc = bu.chercher_document(ref_doc)
        
        doc.emprunter()
        emprunt = externe.ajouter_emprunt(doc, aujourdhui)
        
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, externe.identifiant, externe.nom, externe.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
        logging.info(f"Emprunt réussi : {externe.nom} a emprunté '{doc.titre}'")
    except Exception as e:
        logging.error(f"Échec de l'emprunt : {e}")

    # Scénario D : Test de blocage (Emprunter un document déjà pris)
    try:
        logging.info("Tentative volontaire de ré-emprunter le document LIV001...")
        doc = bu.chercher_document("LIV001")
        doc.emprunter()  # Doit lever une exception car déjà EMPRUNTE
    except DocumentException as e:
        logging.info(f"SUCCÈS DU TEST : L'exception a bien empêché le double emprunt : {e}")
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")

    # --- RETOUR DE DOCUMENT ET CALCUL D'AMENDE ---
    
    # Fatou rend le livre 'LIV001' aujourd'hui
    # Livre emprunté il y a 30 jours, durée autorisée 21 jours pour étudiant -> 9 jours de retard.
    # Tarif retard Livre = 0.50 € par jour. Amende attendue : 9 * 0.50 = 4.50 €.
    try:
        logging.info(f"Traitement du retour pour {etudiant.nom} (LIV001)...")
        amende = etudiant.retourner_document("LIV001", aujourdhui)
        
        # Mettre à jour l'état dans la base de données SQL
        doc = bu.chercher_document("LIV001")
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_retour_sql("LIV001", etudiant.identifiant, aujourdhui.strftime("%Y-%m-%d %H:%M:%S"), amende)
        
        logging.info(f"Retour enregistré avec succès ! Amende calculée et payée : {amende} €")
    except Exception as e:
        logging.error(f"Erreur lors du retour : {e}")


    # --- REQUÊTES ET EXPORTS REQUIS ---

    # Export en CSV des emprunts en retard (Dr. Ndiaye a un retard actif sur sa revue REV001)
    date_ref_str = aujourdhui.strftime("%Y-%m-%d %H:%M:%S")
    exporter_retards_csv("data/emprunts_en_retard.csv", date_ref_str)

    # Récupérer et afficher les classements via les requêtes complexes SQL
    logging.info("--- EXÉCUTION DES REQUÊTES MÉTIERS SQL ---")
    
    retards_actifs = obtenir_emprunts_en_retard(date_ref_str)
    print("\n[SQL] Emprunts en retard actifs :")
    for r in retards_actifs:
        print(f" - {r['adherent_nom']} ({r['adherent_categorie']}) a dépassé la date ({r['date_retour_prevue']}) pour '{r['titre']}'")

    top_docs = obtenir_top_documents_empruntes()
    print("\n[SQL] Top des documents les plus empruntés :")
    for td in top_docs:
        print(f" - {td['titre']} ({td['type']}) : emprunté {td['total_emprunts']} fois")

    historique_fatou = obtenir_historique_adherent(etudiant.identifiant)
    print(f"\n[SQL] Historique des emprunts de {etudiant.nom} :")
    for h in historique_fatou:
        print(f" - '{h['titre']}' | Emprunté le : {h['date_emprunt']} | Statut : {h['date_retour_effective']} | Amende payée : {h['amende_payee']} €")

    stats = obtenir_statistiques_globales()
    print("\n[SQL] Statistiques globales de la Bibliothèque ISI :")
    print(f" - Total des amendes perçues : {stats['total_amendes']} €")
    print(f" - Nombre de retours traités : {stats['total_retours']}")
    print(f" - Nombre d'emprunts actuellement actifs (en cours) : {stats['emprunts_actifs']}\n")

    # Exporter le catalogue final mis à jour pour clore la démo
    bu.exporter_catalogue_json("data/catalogue.json")
    logging.info("=== FIN DE LA SIMULATION DU PROJET AVEC SUCCÈS ===")

if __name__ == "__main__":
    executer_demonstration()
