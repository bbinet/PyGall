"""Create the application's database.

Run this once after installing the application::

    python -m pygall.scripts.setup development.ini [-d|--drop]
"""
import logging
import sys
import os

from pyramid.paster import get_app
import transaction

from pygall import models

def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python -m pygall.scripts.setup INI_FILE [-d|--drop]")
    ini_file = sys.argv[1]
    logging.config.fileConfig(ini_file)
    log = logging.getLogger(__name__)
    app = get_app(ini_file, "PyGall")
    settings = app.registry.settings

    if len(sys.argv) > 2 and sys.argv[2] in ['-d', '--drop']:
        log.info("Dropping tables")
        models.Base.metadata.drop_all()
    # Abort if any tables exist to prevent accidental overwriting
    for table in models.Base.metadata.sorted_tables:
        log.debug("checking if table '%s' exists", table.name)
        if table.exists():
            raise RuntimeError("database table '%s' exists" % table.name)

    log.info("Creating tables")
    models.Base.metadata.create_all()

    log.info("Inserting data")
    sess = models.DBSession()
    # insert data here #
    transaction.commit()

    log.info("Generating auth.cfg file")
    with open(settings['auth_cfg'], 'w') as f:
        f.write("# This file contains the credentials of users allowed to\n" \
                "# access to the PyGall photo gallery.\n" \
                "# Currently pygall contains only one group: 'admin'.\n" \
                "# The format of each line should look like:\n" \
                "# 'username:password[:group]'\n" \
                "administrator:xGTJeDo9pPVvM:admin\n" \
                "user:vCzX.LyFC5Hqo\n")


if __name__ == "__main__":
    main()
