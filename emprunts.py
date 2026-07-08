from datetime import datetime, timedelta
from exceptions_enums import CategorieAdherent, EmpruntException
from documents import DocumentBase

class Emprunt:
    """Classe en relation de Composition avec Adherent (cycle de vie lié)."""
    def __init__(self, document: DocumentBase, date_emprunt: datetime, date_retour_prevue: datetime, date_retour_effective: datetime = None, amende_payee: float = 0.0):
        self.document: DocumentBase = document
        self.date_emprunt: datetime = date_emprunt
        self.date_retour_prevue: datetime = date_retour_prevue
        self.date_retour_effective: datetime = date_retour_effective
        self.amende_payee: float = amende_payee

    def est_en_retard(self, date_reference: datetime = None) -> bool:
        if self.date_retour_effective is not None:
            return False
        ref = date_reference if date_reference else datetime.now()
        return ref > self.date_retour_prevue

    def calculer_jours_retard(self, date_reference: datetime = None) -> int:
        if self.date_retour_effective:
            fin = self.date_retour_effective
        else:
            fin = date_reference if date_reference else datetime.now()
        
        if fin <= self.date_retour_prevue:
            return 0
        return (fin - self.date_retour_prevue).days

    def calculer_amende_actuelle(self, date_reference: datetime = None) -> float:
        jours = self.calculer_jours_retard(date_reference)
        return self.document.calculer_amende(jours)


class Adherent:
    """Représente un adhérent de la BU (Composition)."""
    def __init__(self, nom: str, identifiant: str, categorie: CategorieAdherent):
        self.nom: str = nom
        self.identifiant: str = identifiant
        self.categorie: CategorieAdherent = categorie
        self.emprunts: list[Emprunt] = []

    def ajouter_emprunt(self, document: DocumentBase, date_debut: datetime = None) -> Emprunt:
        if date_debut is None:
            date_debut = datetime.now()

        from documents import Livre, Revue, DVD, Memoire
        if isinstance(document, Livre):
            duree_autorisee = 21
        elif isinstance(document, Revue):
            duree_autorisee = 7
        elif isinstance(document, DVD):
            duree_autorisee = 5
        elif isinstance(document, Memoire):
            duree_autorisee = 14
        else:
            duree_autorisee = 14

        if self.categorie == CategorieAdherent.ENSEIGNANT:
            duree_autorisee += 7

        date_fin = date_debut + timedelta(days=duree_autorisee)
        
        nouvel_emprunt = Emprunt(document=document, date_emprunt=date_debut, date_retour_prevue=date_fin)
        self.emprunts.append(nouvel_emprunt)
        return nouvel_emprunt

    def retourner_document(self, document_ref: str, date_retour: datetime = None) -> float:
        if date_retour is None:
            date_retour = datetime.now()

        emprunt_cible = None
        for emp in self.emprunts:
            if emp.document.reference == document_ref and emp.date_retour_effective is None:
                emprunt_cible = emp
                break

        if not emprunt_cible:
            raise EmpruntException(f"Aucun emprunt actif trouvé pour '{document_ref}' chez {self.nom}.")

        emprunt_cible.date_retour_effective = date_retour
        emprunt_cible.document.retourner()

        amende = emprunt_cible.calculer_amende_actuelle(date_retour)
        emprunt_cible.amende_payee = amende
        return amende
