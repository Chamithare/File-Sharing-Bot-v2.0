# This file makes the database directory a Python package
# It allows imports like: from database.database import db

from .database import db

__all__ = ['db']