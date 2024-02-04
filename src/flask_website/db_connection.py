import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from flask_mail import Mail
# Load environment variables from the .env file
load_dotenv()

# to access the data in .env file
HOSTNAME = os.environ.get('HOSTNAME')
DB_PORT = os.environ.get('DB_PORT')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
SCHEMA = os.environ.get("SCHEMA")

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


app.config['SQLALCHEMY_DATABASE_URI'] =\
    f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'

# TimeoutError Database need to change
app.config['SQLALCHEMY_POOL_SIZE'] = 500 # you allow up to 100 concurrent connections to the database.
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600 # 3600 seconds (1 hour) means that connections will be recycled after being open for 1 hour.

app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER']='../certificate-templates'


# Mail Server Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
