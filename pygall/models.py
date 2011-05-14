from sqlalchemy import Column, Integer, Unicode
import sqlahelper

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

def populate():
    session = DBSession()
    model = MyModel(name=u'root', value=55)
    session.add(model)
    session.flush()
