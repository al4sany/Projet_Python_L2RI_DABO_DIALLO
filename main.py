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

    return bu


# ============================================================
#                       MENU INTERACTIF
# ============================================================

TYPES_DOCUMENT = {
    "1": ("Livre", Livre),
    "2": ("Revue", Revue),
    "3": ("DVD", DVD),
    "4": ("Memoire", Memoire),
}

CATEGORIES_ADHERENT = {
    "1": CategorieAdherent.ETUDIANT,
    "2": CategorieAdherent.ENSEIGNANT,
    "3": CategorieAdherent.EXTERNE,
}


def demander_date(message: str) -> datetime:
    """Demande une date à l'utilisateur (ou renvoie maintenant si vide)."""
    saisie = input(f"{message} (format AAAA-MM-JJ, laisser vide pour aujourd'hui) : ").strip()
    if not saisie:
        return datetime.now()
    try:
        return datetime.strptime(saisie, "%Y-%m-%d")
    except ValueError:
        print("Date invalide, valeur par défaut (aujourd'hui) utilisée.")
        return datetime.now()


def menu_ajouter_document(bu: Bibliotheque) -> None:
    print("\n--- Ajouter un document ---")
    print("1. Livre  2. Revue  3. DVD  4. Mémoire")
    choix = input("Type de document : ").strip()
    if choix not in TYPES_DOCUMENT:
        print("Choix invalide.")
        return

    nom_type, classe = TYPES_DOCUMENT[choix]
    titre = input("Titre : ").strip()
    reference = input("Référence (unique, ex: LIV004) : ").strip()

    try:
        if classe is Livre:
            auteur = input("Auteur : ").strip()
            doc = Livre(titre, reference, auteur)
        elif classe is Revue:
            numero = int(input("Numéro : ").strip())
            doc = Revue(titre, reference, numero)
        elif classe is DVD:
            realisateur = input("Réalisateur : ").strip()
            doc = DVD(titre, reference, realisateur)
        else:
            etudiant = input("Étudiant auteur du mémoire : ").strip()
            doc = Memoire(titre, reference, etudiant)

        bu.ajouter_document(doc)
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        print(f"Document '{titre}' ({nom_type}) ajouté avec succès.")
    except ValueError:
        print("Erreur : le numéro saisi n'est pas un entier valide.")
    except DocumentException as e:
        print(f"Erreur métier : {e}")


def menu_emprunter_document(bu: Bibliotheque, adherents: dict) -> None:
    print("\n--- Emprunter un document ---")
    ref = input("Référence du document à emprunter : ").strip()
    adh_id = input("Identifiant de l'adhérent (ex: ADH001) : ").strip()

    if adh_id not in adherents:
        creer = input("Adhérent inconnu. Le créer maintenant ? (o/n) : ").strip().lower()
        if creer != "o":
            return
        nom = input("Nom de l'adhérent : ").strip()
        print("1. Étudiant  2. Enseignant  3. Externe")
        cat_choix = input("Catégorie : ").strip()
        categorie = CATEGORIES_ADHERENT.get(cat_choix, CategorieAdherent.ETUDIANT)
        adherents[adh_id] = Adherent(nom, adh_id, categorie)

    adherent = adherents[adh_id]

    try:
        doc = bu.chercher_document(ref)
        doc.emprunter()
        date_debut = demander_date("Date d'emprunt")
        emprunt = adherent.ajouter_emprunt(doc, date_debut)

        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_emprunt_sql(
            doc.reference, adherent.identifiant, adherent.nom, adherent.categorie.value,
            emprunt.date_emprunt.strftime("%Y-%m-%d %H:%M:%S"),
            emprunt.date_retour_prevue.strftime("%Y-%m-%d %H:%M:%S")
        )
        print(f"Emprunt enregistré : {adherent.nom} <- '{doc.titre}' (retour prévu le {emprunt.date_retour_prevue.strftime('%Y-%m-%d')}).")
    except DocumentException as e:
        print(f"Erreur métier : {e}")


def menu_retourner_document(adherents: dict, bu: Bibliotheque) -> None:
    print("\n--- Retourner un document ---")
    adh_id = input("Identifiant de l'adhérent : ").strip()
    if adh_id not in adherents:
        print("Adhérent introuvable.")
        return
    adherent = adherents[adh_id]
    ref = input("Référence du document rendu : ").strip()

    try:
        date_retour = demander_date("Date de retour")
        amende = adherent.retourner_document(ref, date_retour)

        doc = bu.chercher_document(ref)
        synchroniser_document_sql(doc.reference, doc.titre, doc.__class__.__name__, doc.statut.value)
        enregistrer_retour_sql(ref, adherent.identifiant, date_retour.strftime("%Y-%m-%d %H:%M:%S"), amende)

        print(f"Retour enregistré. Amende à payer : {amende:.2f} €")
    except EmpruntException as e:
        print(f"Erreur métier : {e}")
    except DocumentException as e:
        print(f"Erreur métier : {e}")


def menu_voir_catalogue(bu: Bibliotheque) -> None:
    print("\n--- Catalogue actuel ---")
    if not bu.catalogue:
        print("Le catalogue est vide.")
        return
    for doc in bu.catalogue:
        print(f" - [{doc.reference}] {doc.titre} ({doc.__class__.__name__}) - Statut : {doc.statut.value}")


def menu_retards() -> None:
    date_ref = input("Date de référence (AAAA-MM-JJ, vide = aujourd'hui) : ").strip()
    date_ref_str = date_ref + " 23:59:59" if date_ref else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    retards = obtenir_emprunts_en_retard(date_ref_str)
    print("\n--- Emprunts en retard ---")
    if not retards:
        print("Aucun retard trouvé.")
    for r in retards:
        print(f" - {r['adherent_nom']} ({r['adherent_categorie']}) : '{r['titre']}' - prévu le {r['date_retour_prevue']}")


def menu_top_documents() -> None:
    top = obtenir_top_documents_empruntes()
    print("\n--- Top des documents les plus empruntés ---")
    if not top:
        print("Aucun emprunt enregistré.")
    for t in top:
        print(f" - {t['titre']} ({t['type']}) : {t['total_emprunts']} emprunt(s)")


def menu_historique_adherent() -> None:
    adh_id = input("Identifiant de l'adhérent : ").strip()
    historique = obtenir_historique_adherent(adh_id)
    print(f"\n--- Historique de l'adhérent {adh_id} ---")
    if not historique:
        print("Aucun historique trouvé.")
    for h in historique:
        print(f" - '{h['titre']}' | Emprunté le {h['date_emprunt']} | Retour : {h['date_retour_effective']} | Amende : {h['amende_payee']} €")


def menu_statistiques() -> None:
    stats = obtenir_statistiques_globales()
    print("\n--- Statistiques globales ---")
    print(f" - Total des amendes perçues : {stats['total_amendes']} €")
    print(f" - Nombre de retours traités : {stats['total_retours']}")
    print(f" - Emprunts actuellement en cours : {stats['emprunts_actifs']}")


def menu_export_json(bu: Bibliotheque) -> None:
    bu.exporter_catalogue_json("data/catalogue.json")
    print("Catalogue exporté dans data/catalogue.json")


def menu_export_csv() -> None:
    date_ref_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    exporter_retards_csv("data/emprunts_en_retard.csv", date_ref_str)
    print("Retards exportés dans data/emprunts_en_retard.csv")


def afficher_menu() -> None:
    print("\n" + "=" * 55)
    print(" BIBLIOTHÈQUE UNIVERSITAIRE ISI - MENU PRINCIPAL")
    print("=" * 55)
    print(" 1. Lancer la démonstration automatique (données de test)")
    print(" 2. Ajouter un document")
    print(" 3. Emprunter un document")
    print(" 4. Retourner un document")
    print(" 5. Voir le catalogue")
    print(" 6. Voir les emprunts en retard (SQL)")
    print(" 7. Voir le top des documents empruntés (SQL)")
    print(" 8. Voir l'historique d'un adhérent (SQL)")
    print(" 9. Voir les statistiques globales (SQL)")
    print("10. Exporter le catalogue en JSON")
    print("11. Exporter les retards en CSV")
    print(" 0. Quitter")
    print("=" * 55)


def lancer_menu_interactif() -> None:
    """Point d'entrée principal : menu interactif en ligne de commande."""
    initialiser_bdd()
    bu = Bibliotheque("Bibliothèque Interuniversitaire ISI-Dakar")
    adherents: dict[str, Adherent] = {}

    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        if choix == "1":
            bu = executer_demonstration()
            print("\n(Démonstration terminée. Le catalogue et les emprunts de test sont chargés.)")
        elif choix == "2":
            menu_ajouter_document(bu)
        elif choix == "3":
            menu_emprunter_document(bu, adherents)
        elif choix == "4":
            menu_retourner_document(adherents, bu)
        elif choix == "5":
            menu_voir_catalogue(bu)
        elif choix == "6":
            menu_retards()
        elif choix == "7":
            menu_top_documents()
        elif choix == "8":
            menu_historique_adherent()
        elif choix == "9":
            menu_statistiques()
        elif choix == "10":
            menu_export_json(bu)
        elif choix == "11":
            menu_export_csv()
        elif choix == "0":
            print("Fermeture de l'application. À bientôt !")
            logging.info("=== FERMETURE DE L'APPLICATION PAR L'UTILISATEUR ===")
            break
        else:
            print("Choix invalide, veuillez réessayer.")


if __name__ == "__main__":
    lancer_menu_interactif()
