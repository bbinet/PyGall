"""The application's model objects"""
from pygall.model import meta

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    meta.Session.configure(bind=engine)
    meta.engine = engine


from pygall.model.photo import PyGallPhoto, PyGallTag

