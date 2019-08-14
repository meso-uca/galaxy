"""
This migration script eliminates all of the tables that were used for the 1st version of the
library templates where template fields and contents were each stored as a separate table row
in various library item tables.  All of these tables are dropped in this script, eliminating all
existing template data.  A total of 14 existing tables are dropped.

We're now basing library templates on forms, so field contents are
stored as a jsonified list in the form_values table.  This script introduces the following 3
new association tables:
1) library_info_association
2) library_folder_info_association
3) library_dataset_dataset_info_association

If using mysql, this script will throw an (OperationalError) exception due to a long index name on
the library_dataset_dataset_info_association table, which is OK because the script creates an index
with a shortened name.
"""
from __future__ import print_function

import logging

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Table
)

from galaxy.model.migrate.versions.util import (
    create_table,
    drop_table
)

log = logging.getLogger(__name__)
metadata = MetaData()

OLD_TABLE_NAMES = [
    'library_item_info_permissions',
    'library_item_info_template_permissions',
    'library_item_info_element',
    'library_item_info_template_element',
    'library_info_template_association',
    'library_folder_info_template_association',
    'library_dataset_info_template_association',
    'library_dataset_dataset_info_template_association',
    'library_info_association',
    'library_folder_info_association',
    'library_dataset_info_association',
    'library_dataset_dataset_info_association',
    'library_item_info',
    'library_item_info_template',
]

LibraryInfoAssociation_table = Table('library_info_association', metadata,
                                     Column("id", Integer, primary_key=True),
                                     Column("library_id", Integer, ForeignKey("library.id"), index=True),
                                     Column("form_definition_id", Integer, ForeignKey("form_definition.id"), index=True),
                                     Column("form_values_id", Integer, ForeignKey("form_values.id"), index=True))

LibraryFolderInfoAssociation_table = Table('library_folder_info_association', metadata,
                                           Column("id", Integer, primary_key=True),
                                           Column("library_folder_id", Integer, ForeignKey("library_folder.id"), nullable=True, index=True),
                                           Column("form_definition_id", Integer, ForeignKey("form_definition.id"), index=True),
                                           Column("form_values_id", Integer, ForeignKey("form_values.id"), index=True))

LibraryDatasetDatasetInfoAssociation_table = Table('library_dataset_dataset_info_association', metadata,
                                                   Column("id", Integer, primary_key=True),
                                                   Column("library_dataset_dataset_association_id", Integer, ForeignKey("library_dataset_dataset_association.id"), nullable=True, index=True),
                                                   Column("form_definition_id", Integer, ForeignKey("form_definition.id"), index=True),
                                                   Column("form_values_id", Integer, ForeignKey("form_values.id"), index=True))

NEW_TABLES = [
    LibraryInfoAssociation_table,
    LibraryFolderInfoAssociation_table,
    LibraryDatasetDatasetInfoAssociation_table
]


def upgrade(migrate_engine):
    print(__doc__)
    metadata.bind = migrate_engine
    metadata.reflect()

    # Drop all of the original library_item_info tables
    # NOTE: all existing library item into template data is eliminated here via table drops
    for table_name in OLD_TABLE_NAMES:
        drop_table(table_name, metadata)

    # Create all new tables above
    for table in NEW_TABLES:
        create_table(table)

    # Fix index on LibraryDatasetDatasetInfoAssociation_table for mysql
    if migrate_engine.name == 'mysql':
        # Load existing tables
        metadata.reflect()
        i = Index("ix_lddaia_ldda_id", LibraryDatasetDatasetInfoAssociation_table.c.library_dataset_dataset_association_id)
        try:
            i.create()
        except Exception:
            log.exception("Adding index 'ix_lddaia_ldda_id' to table 'library_dataset_dataset_info_association' table failed.")


def downgrade(migrate_engine):
    pass
