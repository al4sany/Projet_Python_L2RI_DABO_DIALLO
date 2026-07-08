import os
from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging

class StatutDocument(Enum):
    DISPONIBLE = "DISPONIBLE"
    EMPRUNTE = "EMPRUNTE"
    RESERVE = "RESERVE"
    PERDU = "PERDU"

class CategorieAdherent(Enum):
    ETUDIANT = "ETUDIANT"
    ENSEIGNANT = "ENSEIGNANT"
    EXTERNE = "EXTERNE"

class DocumentException(Exception):
    """Exception levée pour les erreurs liées aux documents."""
    pass

class EmpruntException(Exception):
    """Exception levée pour les erreurs liées aux emprunts."""
    pass
