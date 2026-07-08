import json
import logging
from documents import DocumentBase, Livre, Revue, DVD, Memoire
from exceptions_enums import StatutDocument, DocumentException

class Bibliotheque:
    """Agrégation : contient des documents."""
    def __init__(self, nom: str):
        self.nom: str = nom
        self.catalogue: list[DocumentBase] = []

    def ajouter_document(self, doc: DocumentBase) -> None:
        if any(d.reference == doc.reference for d in self.catalogue):
            raise DocumentException(f"Un document avec la référence '{doc.reference}' existe déjà.")
        self.catalogue.append(doc)
        logging.info(f"Document ajouté au catalogue : {doc.titre} ({doc.reference})")

    def chercher_document(self, reference: str) -> DocumentBase:
        for doc in self.catalogue:
            if doc.reference == reference:
                return doc
        raise DocumentException(f"Le document '{reference}' est introuvable.")

    def exporter_catalogue_json(self, chemin_fichier: str) -> None:
        data = []
        for doc in self.catalogue:
            type_doc = doc.__class__.__name__
            info = {
                "type": type_doc,
                "titre": doc.titre,
                "reference": doc.reference,
                "statut": doc.statut.value
            }
            if isinstance(doc, Livre):
                info["auteur"] = doc.auteur
            elif isinstance(doc, Revue):
                info["numero"] = doc.numero
            elif isinstance(doc, DVD):
                info["realisateur"] = doc.realisateur
            elif isinstance(doc, Memoire):
                info["etudiant"] = doc.etudiant
            
            data.append(info)

        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Catalogue exporté dans {chemin_fichier}")

    def charger_catalogue_json(self, chemin_fichier: str) -> None:
        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.catalogue.clear()
            for info in data:
                type_doc = info.get("type")
                titre = info.get("titre")
                ref = info.get("reference")
                statut = StatutDocument[info.get("statut", "DISPONIBLE")]

                if type_doc == "Livre":
                    doc = Livre(titre, ref, info.get("auteur", "Inconnu"), statut)
                elif type_doc == "Revue":
                    doc = Revue(titre, ref, int(info.get("numero", 0)), statut)
                elif type_doc == "DVD":
                    doc = DVD(titre, ref, info.get("realisateur", "Inconnu"), statut)
                elif type_doc == "Memoire":
                    doc = Memoire(titre, ref, info.get("etudiant", "Inconnu"), statut)
                else:
                    continue
                self.catalogue.append(doc)
            logging.info(f"Catalogue chargé depuis {chemin_fichier}.")
        except Exception as e:
            logging.error(f"Erreur chargement JSON : {e}")
