# Standard Library Imports
import os
from io import StringIO
import uuid
import csv
import json
import subprocess
from datetime import timedelta

# Related Third Party Imports
from flask import Flask, render_template, url_for, redirect, request, jsonify, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_session import Session
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

# Local App/Library Specific Imports
import add_certificate_function
import db_classes
import setting_functions
import show_certificate_function
import delete_confirmation_function
import load_more_certificates_function
import certificate_details_function
import download_certificate_function
import preview_certificate_function
import get_certificate_function
import template_functions
import generate_functions
import preview_functions
import db_connection
import users_functions
import event_types
import mail
from api_function import verify_certificate_api

from db_classes import CertificateEvent, EventType, CertificateForm, Template


# Load environment variables from the .env file
load_dotenv()


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt


# Session configuration
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = './flask_session/'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialize session
Session(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/img/<temp_id>', methods=['GET',"POST"])
@app.route('/img/<temp_id>/<lang>', methods=['GET', 'POST'])
def img(temp_id, lang=None):
    if lang =="ar_en":
        return preview_functions.arimg(temp_id)
    else:
        return preview_functions.img(temp_id, lang)



# New route for running tests
@app.route('/run_tests', methods=['GET'])
def run_tests():
    try:
        # Run the tests using subprocess
        subprocess.run(['python3', 'tests/test_insertion.py'], check=True)
        return redirect(url_for('login'))
        
    except subprocess.CalledProcessError as e:
        return f'Error executing tests: {e}', 500

# Load translations based on the selected language
def load_translations(selected_language):
    with open(f'translations_{selected_language}.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    return translations


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


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    result = users_functions.login()
    
    # Manage session if login is successful
    if isinstance(result, dict) and result.get('status') == 'success':
        user_id = result.get('user_id')
        session['user_id'] = user_id  # Store the user ID in session
        session['logged_in'] = True  # Indicate that the user is logged in

    return result


# Admin route
@app.route('/admin')
@login_required
def admin():
    if 'logged_in' in session and session['logged_in']:
        return users_functions.admin()
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))
    
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

# Logout route
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()  # Clear the session
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_certificate', methods=['GET', 'POST'])
@login_required
def add_certificate():
    return add_certificate_function.add_certificate()

@app.route('/ar_form', methods=['GET', 'POST'])
@login_required
def ar_form():
    return add_certificate_function.ar_form()

@app.route('/en_form', methods=['GET', 'POST'])
@login_required
def en_form():
    return add_certificate_function.en_form()

@app.route('/aren_form', methods=['GET', 'POST'])
@login_required
def aren_form():
    return add_certificate_function.aren_form()


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

@app.route('/get_certificate_list/<int:event_id>', methods=['GET'])
def get_certificate_list(event_id):
    return download_certificate_function.get_certificate_list(event_id)

@app.route('/download_certificates/<int:event_id>', methods=['POST'])
def download_certificates(event_id):
    return download_certificate_function.download_certificates(event_id, request.json.get('selected_certificates'))

@app.route('/preview_certificates/<int:event_id>')
def preview_certificates(event_id):
    return preview_certificate_function.preview_certificates(event_id)

@app.route('/get_certificate/<int:event_id>/<path:filename>')
def get_certificate(event_id, filename):
    return get_certificate_function.get_certificate(event_id, filename)

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
    return template_functions.edit_template(temp_id)

@app.route('/artemplate/<temp_id>',methods=['GET',"POST"])
@login_required
def artemplate(temp_id):
    return template_functions.artemplateEdit(temp_id)

@app.route('/entemplate/<temp_id>',methods=['GET',"POST"])
@login_required
def entemplate(temp_id):
    return template_functions.entemplateEdit(temp_id)

@app.route('/bitemplate/<temp_id>',methods=['GET',"POST"])
@login_required
def bitemplate(temp_id):
    return template_functions.bitemplateEdit(temp_id)


@app.route("/Select_template", methods=['GET',"POST"])
@login_required
def selectTemp():
    return template_functions.selectTemp()

@app.route('/Delete_template/<temp_id>', methods=['GET',"POST"])
@login_required
def DeleteTemp(temp_id):
    return template_functions.DeleteTemp(temp_id)

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

