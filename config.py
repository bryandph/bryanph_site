
class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    OAUTHLIB_INSECURE_TRANSPORT = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://user@localhost/foo'
    SECRET_KEY = b'\xfbxD\xf9+\x05\xbd\x0b\xa1,\xd9\xeb\xe5\xa8<&'

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = b'\xfbxD\xf9+\x05\xbd\x0b\xa1,\xd9\xeb\xe5\xa8<&'

class TestingConfig(Config):
    TESTING = True
