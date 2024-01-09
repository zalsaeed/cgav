import os
import unittest

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base


HOSTNAME = os.environ.get('HOSTNAME')
DB_PORT = os.environ.get('DB_PORT')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
SCHEMA = os.environ.get("SCHEMA")

class TestUsingFlaskSQLAlchemy(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] =\
            f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'
        self.db = SQLAlchemy(self.app)
        self.bcrypt = Bcrypt(self.app)

        # we map the tables we already have in the database
        # to an object named base
        self.base = automap_base()
        self.base.prepare(autoload_with=self.db.engine)

    

    

    

    def test_insert_row_in_users_table(self):

        info = {
            "Fname": "omar",
            "Lname": "khalid",
            "email": "test@test.com",
            "password": "12345678",
            "user_role": 1
        }

        hashed_password = self.bcrypt.generate_password_hash(info["password"])

        # sanity check, show the tables names!
        users_table = self.base.classes.users
        session = self.db.session

        session.add(users_table(
                                Fname=info['Fname'],
                                Lname=info['Lname'],
                                email=info["email"],
                                password=hashed_password,
                                user_role=info["user_role"]))
        session.commit()



if __name__ == '__main__':
    unittest.main()