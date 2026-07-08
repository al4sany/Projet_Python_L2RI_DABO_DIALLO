from abc import ABC, abstractmethod
from exceptions_enums import StatutDocument, DocumentException

class DocumentBase(ABC):
    """Classe abstraite pour tous les documents."""
    def __init__(self, titre: str, reference: str, statut: StatutDocument = StatutDocument.DISPONIBLE):
        self.titre: str = titre
        self.reference: str = reference
        self.statut: StatutDocument = statut

    @abstractmethod
    def emprunter(self) -> None:
        pass

    @abstractmethod
    def calculer_amende(self, jours_retard: int) -> float:
        pass

    def retourner(self) -> None:
        self.statut = StatutDocument.DISPONIBLE


class Livre(DocumentBase):
    def __init__(self, titre: str, reference: str, auteur: str, statut: StatutDocument = StatutDocument.DISPONIBLE):
        super().__init__(titre, reference, statut)
        self.auteur: str = auteur

    def emprunter(self) -> None:
        if self.statut != StatutDocument.DISPONIBLE:
            raise DocumentException(f"Le livre '{self.titre}' n'est pas disponible (Statut actuel : {self.statut.value}).")
        self.statut = StatutDocument.EMPRUNTE

    def calculer_amende(self, jours_retard: int) -> float:
        return max(0.0, jours_retard * 0.50)


class Revue(DocumentBase):
    def __init__(self, titre: str, reference: str, numero: int, statut: StatutDocument = StatutDocument.DISPONIBLE):
        super().__init__(titre, reference, statut)
        self.numero: int = numero

    def emprunter(self) -> None:
        if self.statut != StatutDocument.DISPONIBLE:
            raise DocumentException(f"La revue '{self.titre}' n'est pas disponible.")
        self.statut = StatutDocument.EMPRUNTE

    def calculer_amende(self, jours_retard: int) -> float:
        return max(0.0, jours_retard * 1.00)


class DVD(DocumentBase):
    def __init__(self, titre: str, reference: str, realisateur: str, statut: StatutDocument = StatutDocument.DISPONIBLE):
        super().__init__(titre, reference, statut)
        self.realisateur: str = realisateur

    def emprunter(self) -> None:
        if self.statut != StatutDocument.DISPONIBLE:
            raise DocumentException(f"Le DVD '{self.titre}' n'est pas disponible.")
        self.statut = StatutDocument.EMPRUNTE

    def calculer_amende(self, jours_retard: int) -> float:
        return max(0.0, jours_retard * 2.00)


class Memoire(DocumentBase):
    def __init__(self, titre: str, reference: str, etudiant: str, statut: StatutDocument = StatutDocument.DISPONIBLE):
        super().__init__(titre, reference, statut)
        self.etudiant: str = etudiant

    def emprunter(self) -> None:
        if self.statut != StatutDocument.DISPONIBLE:
            raise DocumentException(f"Le mémoire '{self.titre}' n'est pas disponible.")
        self.statut = StatutDocument.EMPRUNTE

    def calculer_amende(self, jours_retard: int) -> float:
        return max(0.0, jours_retard * 3.00)
