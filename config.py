import os

DATABASE_NAME = 'quotes2'
DATABASE_USER = 'testuser' 
DATABASE_PASSWORD = 'testpassword'
DATABASE_HOST = '10.1.1.248'
DATABASE_PORT = 5432

MACOLA_HOST = '10.1.1.3'
MACOLA_USER = 'ro'
MACOLA_PASSWORD = 'ropassword'
MACOLA_DATABASE = 'Data'


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
DEBUG = True
COOKIE_SECRET = "cookie secret"
XSRF_COOKIES = False
LOGIN_URL = "/login"
COMPRESS_RESPONSE = True

EMAIL_FROM_NAME = "from_name"
EMAIL_FROM_ADDRESS = "from_address"
EMAIL_TEMPLATE_PATH = os.path.join(TEMPLATE_PATH, "email")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "email_username"
EMAIL_PASSWORD = "email_password"

