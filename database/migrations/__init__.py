# database/migrations/__init__.py

from database.migrations.schema import setup_database, create_tables, seed_admin

__all__ = ['setup_database', 'create_tables', 'seed_admin']
