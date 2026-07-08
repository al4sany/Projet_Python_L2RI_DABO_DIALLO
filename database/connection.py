import sqlite3
import logging

class DBConnection:
    def __init__(self, db_path: str = "database/bibliotheque.db"):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
                logging.error(f"Transaction SQL annulée : {exc_val}")
            else:
                self.conn.commit()
            self.conn.close()

def initialiser_bdd(db_path: str = "database/bibliotheque.db") -> None:
    with DBConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            reference TEXT PRIMARY KEY,
            titre TEXT NOT NULL,
            type TEXT NOT NULL,
            statut TEXT NOT NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emprunts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_ref TEXT NOT NULL,
            adherent_id TEXT NOT NULL,
            adherent_nom TEXT NOT NULL,
            adherent_categorie TEXT NOT NULL,
            date_emprunt TEXT NOT NULL,
            date_retour_prevue TEXT NOT NULL,
            date_retour_effective TEXT,
            amende_payee REAL DEFAULT 0.0,
            FOREIGN KEY (document_ref) REFERENCES documents(reference)
        );
        """)
        logging.info("Base de données initialisée.")
