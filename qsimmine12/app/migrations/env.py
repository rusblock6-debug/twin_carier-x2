import logging
from logging.config import fileConfig

from sqlalchemy import pool
from alembic import context

from app import engine

target_metadata = None

# Alembic Config object
config = context.config

# Логирование (из alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def run_migrations_offline():
    """Запуск миграций в оффлайн-режиме."""
    url = str(engine.url).replace("%", "%%")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций в онлайн-режиме."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
