import os
import unittest

import pymysql.cursors
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table
from sqlalchemy.ext.automap import automap_base

# get env variables
try:
    HOSTNAME = os.environ.get('HOSTNAME')
    DB_PORT = os.environ.get('DB_PORT')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
    MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    SCHEMA = os.environ.get("SCHEMA")
except Exception as e:
    raise ValueError(f"One or more of the env keys is missing. {e}")


class TestUsingPyMySQL(unittest.TestCase):

    def setUp(self):

        # Connect to the database
        self.connection = pymysql.connect(host=HOSTNAME,
                                          port=int(DB_PORT),
                                          user=MYSQL_DATABASE,
                                          password=MYSQL_ROOT_PASSWORD,
                                          database=SCHEMA,
                                          cursorclass=pymysql.cursors.DictCursor)

    def test_we_have_a_connection(self):
        """
        A simple test to check that we have an open connection.
        """
        self.assertTrue(self.connection.open)

    def test_insert_row_in_users_table(self):
        """
        A more thorough test to check that we can insert some data to the system,
        fetch the same inserted data, compare it to the original set we have,
        and finally delete the inserted data to keep the database clean.
        """

        info = {
            "id": "test_id",
            "user_name": "test_username",
            "email": "test@test.com",
            "password": "test_password",
            "user_role": 1
        }

        # insert the data we have
        with self.connection.cursor() as cursor:
            sql_insert = ("INSERT INTO `users` (`id`, `user_name`, `email`, `password`, `user_role`) "
                          "VALUES (%s, %s, %s, %s, %s);")
            cursor.execute(sql_insert, (info['id'], info['user_name'], info["email"], info["password"],
                                        info["user_role"]))
        self.connection.commit()

        # fetch back the same data inserted
        with self.connection.cursor() as cursor:
            # Read a single record
            sql_lookup = "SELECT * FROM `users` WHERE `id`=%s;"
            cursor.execute(sql_lookup, (info["id"]))
            result = cursor.fetchone()  # this should be a dictionary

            self.assertIsInstance(result, dict)

            self.assertEqual(info['id'], result['id'])
            self.assertEqual(info['user_name'], result['user_name'])
            self.assertEqual(info['email'], result['email'])
            self.assertEqual(info['password'], result['password'])
            self.assertEqual(info['user_role'], result['user_role'])

        # remove the data from the database
        with self.connection.cursor() as cursor:
            sql_delete = f"DELETE FROM `users` WHERE (`id` =%s);"
            cursor.execute(sql_delete, (info["id"]))

        self.connection.commit()

    def tearDown(self):
        self.connection.close()


class TestUsingFlaskSQLAlchemy(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] =\
            f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'
        self.db = SQLAlchemy(self.app)

        # we map the tables we already have in the database
        # to an object named base
        self.base = automap_base()
        self.base.prepare(autoload_with=self.db.engine)

    def test_we_have_a_connection(self):
        self.assertTrue(self.db.session.execute('SELECT 1'))

    def test_got_expected_tables(self):
        """
        Sanity check, go over all the tables names we got from
        SQLAlchemy and make sure they match what we expect!
        """

        # these are the tables we defined in our .sql script
        list_of_tables = ['users', 'Template', 'Event_type', 'recipient', 'instructor', 'signs',
                          'CertificateCustomizations', 'addCertificate', 'Certificate', 'CertificateSigns', 'demo']

        # loop over tables name from SQLAlchemy
        for table_name in self.base.classes.keys():
            self.assertIn(table_name, list_of_tables)

    def test_we_got_the_correct_columns_names_from_the_users_table(self):
        """
        We want to make sure the columns in the users table (as an example)
        are as we expect.
        """
        users_table_columns_names = ['users.id', 'users.user_name', 'users.email',
                                     'users.password', 'users.user_role']

        # get the users table from the base object (the reflection object)
        users_table = self.base.classes.users

        # this will return the columns names and other object-based keys
        # print(users_table.__dict__.keys())

        # a better solution is to get the table and then check the columns
        table_obj = users_table.__dict__['__table__']
        self.assertIsInstance(table_obj, Table)
        for column_name in table_obj.columns:
            self.assertIn(str(column_name), users_table_columns_names)

    def test_insert_row_in_users_table(self):
        """
        A thorough test to check that we can insert some data to the system,
        fetch the same inserted data, compare it to the original set we have,
        and finally delete the inserted data to keep the database clean.
        """

        info = {
            "id": "test_id2",
            "user_name": "test_username2",
            "email": "test@test.com2",
            "password": "test_password2",
            "user_role": 2
        }

        # sanity check, show the tables names!
        users_table = self.base.classes.users
        session = self.db.session

        session.add(users_table(id=info["id"],
                                user_name=info['user_name'],
                                email=info["email"],
                                password=info["password"],
                                user_role=info["user_role"]))
        session.commit()

        result = session.query(users_table).filter_by(id=info["id"]).first()
        # print(result.__dict__)  # to see what we got

        self.assertEqual(info['id'], result.id)
        self.assertEqual(info['user_name'], result.user_name)
        self.assertEqual(info['email'], result.email)
        self.assertEqual(info['password'], result.password)
        self.assertEqual(info['user_role'], result.user_role)

        session.query(users_table).filter_by(id=info["id"]).delete()
        session.commit()


if __name__ == '__main__':
    unittest.main()
