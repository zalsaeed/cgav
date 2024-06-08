# Standard Library Imports
import os
import json
import subprocess
import logging

# Related Third Party Imports
from flask import Flask, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from flask_login import LoginManager, current_user

# Local App/Library Specific Imports
from db_classes import CertificateEvent, EventType, CertificateForm,CertificateCustomizations, Template,Certificate_table
import db_connection




app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def fetch_latest_pdf():
    # The path to the output directory, considering the Docker container's file system
    search_directory = os.path.abspath("/root/src/flask_website/static/output")

    try:
        all_folders = [os.path.join(search_directory, d) for d in os.listdir(search_directory) if os.path.isdir(os.path.join(search_directory, d))]
        latest_folder = max(all_folders, key=os.path.getmtime)

        for file in os.listdir(latest_folder):
            if file.endswith(".pdf"):
                full_file_path = os.path.join(latest_folder, file)
                # Generate the relative path from the static folder
                relative_path = os.path.relpath(full_file_path, "/root/src/flask_website/static")
                pdf_url = url_for('static', filename=relative_path.replace(os.sep, '/'))

                return jsonify({'pdfUrl': pdf_url})

        return jsonify({'error': 'No PDF found'}), 404

    except Exception as e:
        app.logger.error(f"Error in fetch_latest_pdf: {str(e)}")
        return jsonify({'error': 'An internal error occurred'}), 500

def certificate_event_id_already_stored(certificate_event_id):
    # Query the database to check if the certificate event ID already exists
    return Certificate_table.query.filter_by(certificate_event_id=certificate_event_id).first() is not None

def run_main_script(temp_id):
    try:
        customization = CertificateCustomizations.query.filter_by(template_id=temp_id).first()
        template= Template.query.filter_by(template_id=temp_id).first()
        event_data = {
            'template_path': template.template_image,
        }
        if customization:
            items_positions={
                "Certificate_Title":customization.items_positions["Certificate_Title"],
                "Intro": customization.items_positions["Intro"],
                "recipient_title":customization.items_positions["recipient_title"],
                "recipient_name":customization.items_positions["recipient_name"],
                "body":customization.items_positions["body"] ,
                "final_greeting":customization.items_positions["final_greeting"] ,
                "contact_info":customization.items_positions["contact_info"],
                "signature_1": customization.items_positions["signature_1"],
                "signature_2": customization.items_positions["signature_2"]}
        else:
            items_positions={}

        # script_path = os.path.join(os.getcwd(), 'main.py')
        result = subprocess.run(['python', 'main.py', '--event_data', json.dumps(event_data), '--items_positions', json.dumps(items_positions)], capture_output=True, text=True)
        return jsonify({'success': True, 'output': result.stdout})
    
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_certificate(certificate_event_id):

        # # Check if the certificate event ID is already stored
        # if certificate_event_id_already_stored(certificate_event_id):
        #     return jsonify({'success': False, 'error': 'Certificate event ID already exists'}), 400


        certificate = CertificateEvent.query.get(certificate_event_id)
        customization = CertificateCustomizations.query.filter_by(template_id=certificate.template_id).first()
        
        items_positions={}
        if not certificate:
            return jsonify({'success': False, 'error': 'Certificate not found'}), 404

        # Prepare event data based on the form type
        if certificate.form_type == 'Arabic':
            event_data = {
                'certificate_event_id': int(certificate.certificate_event_id),
                'certificate_title': certificate.certificate_title,
                'event_type': certificate.event_type_id,
                'template_path': certificate.template_path,
                'presenter_name': certificate.presenter_name,
                'secret_phrase': certificate.secret_phrase,
                'event_date': certificate.event_date.strftime('%Y-%m-%d'),
                'certificate_description_female': certificate.certificate_description_female,
                'certificate_description_male': certificate.certificate_description_male,
                'file_path': certificate.file_path,
                'First_Signatory_Name': certificate.First_Signatory_Name,
                'First_Signatory_Position': certificate.First_Signatory_Position,
                'First_Signatory_Path': certificate.First_Signatory_Path,
                'Second_Signatory_Name': certificate.Second_Signatory_Name,
                'Second_Signatory_Position': certificate.Second_Signatory_Position,
                'Second_Signatory_Path': certificate.Second_Signatory_Path,
                'greeting_female': certificate.greeting_female,
                'greeting_male': certificate.greeting_male,
                'intro': certificate.intro,
                'male_recipient_title': certificate.male_recipient_title,
                'female_recipient_title': certificate.female_recipient_title,
                'form_type': certificate.form_type,
            }

        
        elif certificate.form_type == 'English':
            event_data = {
                'certificate_event_id': int(certificate.certificate_event_id),
                'certificate_title': certificate.certificate_title,
                'event_type': certificate.event_type_id,
                'template_path': certificate.template_path,
                'presenter_name': certificate.presenter_name,
                'secret_phrase': certificate.secret_phrase,
                'event_date': certificate.event_date.strftime('%Y-%m-%d'),
                'file_path': certificate.file_path,
                'First_Signatory_Name': certificate.First_Signatory_Name,
                'First_Signatory_Position': certificate.First_Signatory_Position,
                'First_Signatory_Path': certificate.First_Signatory_Path,
                'Second_Signatory_Name': certificate.Second_Signatory_Name,
                'Second_Signatory_Position': certificate.Second_Signatory_Position,
                'Second_Signatory_Path': certificate.Second_Signatory_Path,
                'certificate_description_female_en': certificate.certificate_description_female_en,
                'certificate_description_male_en': certificate.certificate_description_male_en,
                'greeting_female_en': certificate.greeting_female_en,
                'greeting_male_en': certificate.greeting_male_en,
                'intro_en': certificate.intro_en,
                'male_recipient_title_en': certificate.male_recipient_title_en,
                'female_recipient_title_en': certificate.female_recipient_title_en,
                'form_type': certificate.form_type,
            }
        elif certificate.form_type == 'Arabic_English':
            # Combine Arabic and English form data
            event_data = {
                # Arabic form data
                'certificate_description_female': certificate.certificate_description_female,
                'certificate_description_male': certificate.certificate_description_male,
                'greeting_female': certificate.greeting_female,
                'greeting_male': certificate.greeting_male,
                'intro': certificate.intro,
                'male_recipient_title': certificate.male_recipient_title,
                'female_recipient_title': certificate.female_recipient_title,

                # English form data
                'certificate_description_female_en': certificate.certificate_description_female_en,
                'certificate_description_male_en': certificate.certificate_description_male_en,
                'greeting_female_en': certificate.greeting_female_en,
                'greeting_male_en': certificate.greeting_male_en,
                'intro_en': certificate.intro_en,
                'male_recipient_title_en': certificate.male_recipient_title_en,
                'female_recipient_title_en': certificate.female_recipient_title_en,

                # Common data
                'certificate_event_id': int(certificate.certificate_event_id),
                'certificate_title': certificate.certificate_title,
                'event_type': certificate.event_type_id,
                'template_path': certificate.template_path,
                'presenter_name': certificate.presenter_name,
                'secret_phrase': certificate.secret_phrase,
                'event_date': certificate.event_date.strftime('%Y-%m-%d'),
                'file_path': certificate.file_path,
                'First_Signatory_Name': certificate.First_Signatory_Name,
                'First_Signatory_Position': certificate.First_Signatory_Position,
                'First_Signatory_Path': certificate.First_Signatory_Path,
                'Second_Signatory_Name': certificate.Second_Signatory_Name,
                'Second_Signatory_Position': certificate.Second_Signatory_Position,
                'Second_Signatory_Path': certificate.Second_Signatory_Path,
                'form_type': certificate.form_type,
            }
        if customization:
            if certificate.form_type == 'Arabic_English':
                items_positions={
                    "Certificate_Title":customization.items_positions["Certificate_Title"],
                    "Intro": customization.items_positions["Intro"],
                    "recipient_title":customization.items_positions["recipient_title"],
                    "recipient_name":customization.items_positions["recipient_name"],
                    "body":customization.items_positions["body"] ,
                    "final_greeting":customization.items_positions["final_greeting"] ,
                    "contact_info":customization.items_positions["contact_info"],
                    "signature_1": customization.items_positions["signature_1"],
                    "signature_2": customization.items_positions["signature_2"],
                    "Intro_en": customization.items_positions["Intro_en"],
                    "recipient_title_en":customization.items_positions["recipient_title_en"],
                    "recipient_name_en":customization.items_positions["recipient_name_en"],
                    "body_en":customization.items_positions["body_en"] ,
                    "final_greeting_en":customization.items_positions["final_greeting_en"] ,
                    }
            else:
                items_positions={
                    "Certificate_Title":customization.items_positions["Certificate_Title"],
                    "Intro": customization.items_positions["Intro"],
                    "recipient_title":customization.items_positions["recipient_title"],
                    "recipient_name":customization.items_positions["recipient_name"],
                    "body":customization.items_positions["body"] ,
                    "final_greeting":customization.items_positions["final_greeting"] ,
                    "contact_info":customization.items_positions["contact_info"],
                    "signature_1": customization.items_positions["signature_1"],
                    "signature_2": customization.items_positions["signature_2"]}
        else:
                items_positions={}
        
        try:
            certificate_exists = CertificateEvent.query.get(certificate_event_id) is not None
            if not certificate_exists:
                return jsonify({'success': False, 'error': 'Certificate not found'}), 404

            stmt = update(CertificateEvent).where(CertificateEvent.certificate_event_id == certificate_event_id).values(secret_phrase="ggGBs2hu9j")
            db.session.execute(stmt)
            certificate.generated_ = True
            db.session.commit()
            

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
        
        logging.info("Retrieved data: %s", event_data)
        logging.info("Retrieved positions: %s", items_positions)
        # result = subprocess.run(['python', 'main.py', '--event_data', json.dumps(event_data), '--items_positions', json.dumps(items_positions)], capture_output=True, text=True)
        script_path = os.path.abspath(os.path.join('', 'flask_website', 'main.py'))
        result = subprocess.run(['python', script_path, '--event_data', json.dumps(event_data), '--items_positions', json.dumps(items_positions)], capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result.stderr})
   
    

