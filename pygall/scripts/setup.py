import os
import pkg_resources
import sys
import transaction

from paste.deploy.loadwsgi import appconfig
from sqlalchemy import engine_from_config

from pygall.models import initialize_sql
from pygall.models import Base
from pygall.models import DBSession
#from pygall.models import MyModel

def main(argv=sys.argv):
    dist = pkg_resources.get_distribution('pygall')
    root = dist.location
    config = 'config:' + os.path.join(root, 'development.ini')
    settings = appconfig(config, "PyGall")
    engine = engine_from_config(settings, 'sqlalchemy.')

    initialize_sql(engine)

    Base.metadata.create_all(engine)
    #session = DBSession()
    #model = MyModel(name=u'root',value=55)
    #session.add(model)
    #session.flush()
    #transaction.commit()
