# backend/__init__.py
"""
Package principal de l'application Luxe Beauté
"""

__version__ = "2.0.0"
__author__ = "Équipe Luxe Beauté"


# backend/__init__.py
# Ce fichier permet d'importer facilement les modules
from .database import Base, engine, SessionLocal
from . import models, schemas, crud, routes