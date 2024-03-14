# Standard Library Imports
import os
from io import StringIO
import uuid
import csv

# Related Third Party Imports
from flask import Flask, render_template, url_for, redirect, request, jsonify, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import update
from sqlalchemy.orm.session import object_session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import subprocess

# Local App/Library Specific Imports
import add_certificate_function
import db_classes
import setting_functions
import show_certificate_function
import delete_confirmation_function
import load_more_certificates_function
import certificate_details_function
import download_certificate_function
import template_functions
import generate_functions
import db_connection
import users_functions
import event_types
import mail
from api_function import verify_certificate_api

from db_classes import CertificateEvent, EventType, CertificateForm, Template

# Load environment variables from the .env file
load_dotenv()

# to access the data in .env file
# HOSTNAME = os.environ.get('HOSTNAME')
# DB_PORT = os.environ.get('DB_PORT')
# MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
# MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
# MYSQL_USER = os.environ.get('MYSQL_USER')
# MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
# SCHEMA = os.environ.get("SCHEMA")

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt
# old uri 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# new uri
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'

# TimeoutError Database need to change
# app.config['SQLALCHEMY_POOL_SIZE'] = 500 # you allow up to 100 concurrent connections to the database.
# app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600 # 3600 seconds (1 hour) means that connections will be recycled after being open for 1 hour.

# app.config['SECRET_KEY'] = 'thisisasecretkey'
# app.config['UPLOAD_FOLDER']='../certificate-templates'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Add a new route for running tests
@app.route('/run_tests', methods=['GET'])
def run_tests():
    try:
        # Run the tests using subprocess
        subprocess.run(['python3', 'tests/test_insertion.py'], check=True)
        return redirect(url_for('login'))
        
    except subprocess.CalledProcessError as e:
        return f'Error executing tests: {e}', 500
    
@login_manager.user_loader
def load_user(user_id):
    return db_classes.users.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/sample')
def sample():
    return render_template('samples.html')

# register route
@ app.route('/register', methods=['GET', 'POST'])
def register():
    return users_functions.register()


# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    return users_functions.login()


#Admin route
@app.route('/admin')
@login_required
def admin():
    return users_functions.admin()
    
#update user
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    return users_functions.update_user(id)
    
#delete user
@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    return users_functions.delete_user(id)
        

# New route for Manage Event Types
@app.route('/manage_event_types', methods=['GET', 'POST'])
@login_required
def manage_event_types():
    return event_types.manage_event_types()


@app.route('/update_event_types', methods=['POST'])
def update_event_types():
    return event_types.update_event_types()

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_certificate', methods=['GET', 'POST'])
@login_required
def add_certificate():
    return add_certificate_function.add_certificate()

@app.route('/settings')
@login_required
def settings():
    return setting_functions.settings()

@app.route('/settings/change_name', methods=['GET', 'POST'])
@login_required
def change_name():
    return setting_functions.change_name()
 

@app.route('/settings/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    return setting_functions.change_email()

@app.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    return setting_functions.change_password()

@app.route('/get_user_info')
@login_required
def get_user_info():
    user_info = {
        'Fname': current_user.Fname,
        'Lname': current_user.Lname,
        'email': current_user.email
    }
    return jsonify(user_info)

@app.route('/api/verify_certificate/<certificate_hash>', methods=['GET'])
def route_verify_certificate(certificate_hash):
    return verify_certificate_api(certificate_hash)



# route to show certificate
@app.route('/certificates', methods=['GET'])
@login_required
def certificates():
    return show_certificate_function.certificates()


@app.route('/load_more_certificates', methods=['GET'])
@login_required
def load_more_certificates():
    return load_more_certificates_function.load_more_certificates()


@app.route('/certificate_details/<certificate_event_id>', methods=['GET'])
@login_required
def certificate_details(certificate_event_id):
    return certificate_details_function.certificate_details(certificate_event_id)

# Add routes for other actions ( generate, download, send) as needed

# Route for the delete confirmation page (from database)
@app.route('/delete_confirmation/<certificate_event_id>', methods=['GET', 'POST'])
@login_required
def delete_confirmation(certificate_event_id):
    return delete_confirmation_function.delete_confirmation(certificate_event_id) 

@app.route('/download_certificates/<int:event_id>', methods=['GET'])
def download_certificates(event_id):
    return download_certificate_function.download_certificates(event_id)

@app.route("/create_new_template", methods=['GET', "POST"])
@login_required
def newtemp():
    return template_functions.newtemp()



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/Select_template/<temp_id>',methods=['GET',"POST"])
@login_required
def template(temp_id):
    return template_functions.template(temp_id)



@app.route("/Select_template", methods=['GET',"POST"])
@login_required
def selectTemp():
    return template_functions.selectTemp()

@app.route('/fetch_latest_pdf', methods=['GET'])
def fetch_latest_pdf():
    return generate_functions.fetch_latest_pdf()



@app.route('/run_main_script/<temp_id>', methods=['POST'])
def run_main_script(temp_id):
    return generate_functions.run_main_script(temp_id)


@app.route('/generate_certificate/<certificate_event_id>', methods=['POST'])
@login_required
def generate_certificate(certificate_event_id):
    return generate_functions.generate_certificate(certificate_event_id)

@app.route('/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
    return mail.send_email()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

