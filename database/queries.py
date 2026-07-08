import sqlite3
from database.connection import DBConnection
import csv
import logging

def synchroniser_document_sql(doc_ref: str, titre: str, type_doc: str, statut: str, db_path: str = "database/bibliotheque.db") -> None:
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (reference, titre, type, statut)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(reference) DO UPDATE SET statut = excluded.statut;
        """, (doc_ref, titre, type_doc, statut))


def enregistrer_emprunt_sql(document_ref: str, adh_id: str, adh_nom: str, adh_cat: str, date_emp: str, date_prev: str, db_path: str = "database/bibliotheque.db") -> None:
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emprunts (document_ref, adherent_id, adherent_nom, adherent_categorie, date_emprunt, date_retour_prevue)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (document_ref, adh_id, adh_nom, adh_cat, date_emp, date_prev))


def enregistrer_retour_sql(document_ref: str, adh_id: str, date_eff: str, amende: float, db_path: str = "database/bibliotheque.db") -> None:
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emprunts
            SET date_retour_effective = ?, amende_payee = ?
            WHERE document_ref = ? AND adherent_id = ? AND date_retour_effective IS NULL;
        """, (date_eff, amende, document_ref, adh_id))


def obtenir_emprunts_en_retard(date_ref_str: str, db_path: str = "database/bibliotheque.db") -> list[dict]:
    requete = """
        SELECT e.id, e.document_ref, d.titre, e.adherent_nom, e.adherent_categorie, e.date_emprunt, e.date_retour_prevue
        FROM emprunts e
        JOIN documents d ON e.document_ref = d.reference
        WHERE e.date_retour_effective IS NULL AND e.date_retour_prevue < ?;
    """
    resultats = []
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(requete, (date_ref_str,))
        rows = cursor.fetchall()
        for r in rows:
            resultats.append({
                "id": r[0],
                "document_ref": r[1],
                "titre": r[2],
                "adherent_nom": r[3],
                "adherent_categorie": r[4],
                "date_emprunt": r[5],
                "date_retour_prevue": r[6]
            })
    return resultats


def obtenir_top_documents_empruntes(db_path: str = "database/bibliotheque.db") -> list[dict]:
    requete = """
        SELECT d.reference, d.titre, d.type, COUNT(e.id) as total_emprunts
        FROM emprunts e
        JOIN documents d ON e.document_ref = d.reference
        GROUP BY d.reference
        ORDER BY total_emprunts DESC;
    """
    resultats = []
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(requete)
        rows = cursor.fetchall()
        for r in rows:
            resultats.append({
                "reference": r[0],
                "titre": r[1],
                "type": r[2],
                "total_emprunts": r[3]
            })
    return resultats


def obtenir_historique_adherent(adherent_id: str, db_path: str = "database/bibliotheque.db") -> list[dict]:
    requete = """
        SELECT e.document_ref, d.titre, e.date_emprunt, e.date_retour_prevue, e.date_retour_effective, e.amende_payee
        FROM emprunts e
        JOIN documents d ON e.document_ref = d.reference
        WHERE e.adherent_id = ?
        ORDER BY e.date_emprunt DESC;
    """
    resultats = []
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(requete, (adherent_id,))
        rows = cursor.fetchall()
        for r in rows:
            resultats.append({
                "document_ref": r[0],
                "titre": r[1],
                "date_emprunt": r[2],
                "date_retour_prevue": r[3],
                "date_retour_effective": r[4] if r[4] else "Non rendu",
                "amende_payee": r[5]
            })
    return resultats


def obtenir_statistiques_globales(db_path: str = "database/bibliotheque.db") -> dict:
    requete = """
        SELECT 
            SUM(amende_payee) as total_amendes,
            COUNT(CASE WHEN date_retour_effective IS NOT NULL THEN 1 END) as total_retours,
            COUNT(CASE WHEN date_retour_effective IS NULL THEN 1 END) as emprunts_actifs
        FROM emprunts;
    """
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(requete)
        r = cursor.fetchone()
        return {
            "total_amendes": r[0] if r[0] else 0.0,
            "total_retours": r[1] if r[1] else 0,
            "emprunts_actifs": r[2] if r[2] else 0
        }


def exporter_retards_csv(chemin_csv: str, date_ref_str: str, db_path: str = "database/bibliotheque.db") -> None:
    retards = obtenir_emprunts_en_retard(date_ref_str, db_path)
    with open(chemin_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ID_Emprunt", "Référence", "Titre", "Adhérent", "Catégorie", "Date Emprunt", "Date Retour Prévue"])
        for r in retards:
            writer.writerow([r["id"], r["document_ref"], r["titre"], r["adherent_nom"], r["adherent_categorie"], r["date_emprunt"], r["date_retour_prevue"]])
    logging.info(f"Export CSV réussi : {chemin_csv}")
