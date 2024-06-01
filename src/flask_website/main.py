import os
import logging
import datetime
import argparse
import fpdf

import util
import configuration_loader
from csv_gen import CSVGen
from certificate import Certificate , BilingualCertificate

from db_classes import recipient, Certificate_table
from db_connection import db, app
import sqlalchemy.exc

# set up logger
for handler in logging.root.handlers[:]:  
    logging.root.removeHandler(handler)

logging_level = logging.DEBUG
logging_format = logging.Formatter('%(asctime)s: %(levelname)s [%(name)s:%(funcName)s:%(lineno)d] - %(message)s')
logging.root.setLevel(logging_level)
h = logging.StreamHandler()
h.setFormatter(logging_format)
logging.root.addHandler(h)

log = logging.getLogger(__name__)


import argparse
import json
import yaml
import uuid


def generate_recipient_id():
    # Generate a random UUID and convert it to a string
    return str(uuid.uuid4())

def store_recipient_info(recipient_data,first_name,middle_name,last_name):
    # Check if recipient already exists
    existing_recipient = recipient.query.filter_by(email=recipient_data['email']).first()
    
    if existing_recipient:
        # Update existing recipient information
        existing_recipient.first_name = first_name
        existing_recipient.middle_name = middle_name
        existing_recipient.last_name = last_name
        existing_recipient.gender = recipient_data['gender']
        existing_recipient.phone_number = recipient_data.get('phone_number', None)  # Optional phone number
        db.session.commit()
        return existing_recipient.recipient_id  # Use the correct attribute name here
    else:
        # Create new recipient entry
        new_recipient = recipient(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender=recipient_data['gender'],
            email=recipient_data['email'],
            phone_number=recipient_data.get('phone_number', None),  # Optional phone number
        )
        db.session.add(new_recipient)
        db.session.commit()
        return new_recipient.recipient_id  # And here as well


def store_certificate_hash(certificate_hash, recipient_id, event_id):
    # Configure the logger to output log messages to the console
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

    try:
        # Create and add the new certificate
        new_certificate = Certificate_table(
            certificate_hash=certificate_hash,
            recipient_id=recipient_id,
            certificate_event_id=event_id
        )
        db.session.add(new_certificate)
        db.session.commit()
        log.info("Certificate stored successfully.")
        return "Certificate stored successfully."

    except sqlalchemy.exc.IntegrityError as e:
        log.error(f"IntegrityError: {e}")
        db.session.rollback()
        return "Error: Certificate Already Exists."
       

# Define a function to load default data from the YAML file
def load_default_data():
    with open('./events/sample-event.yaml', 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def load_default_cutomization():
    with open('./customization/customization.json', 'r') as file:
        default_customization = json.load(file)
    return default_customization

def merge_with_default(data, default_data):
    key_mappings = {
        'certificate_event_id': 'certificate_event_id',
        'certificate_title': 'event_title',
        'event_type': 'event_type',
        'template_path': 'template_path',
        'presenter_name': 'presenter_name',
        'secret_phrase': 'secret_phrase',
        'event_date': 'event_date',
        'file_path': 'csv_file',
        'First_Signatory_Name': 'First_Signatory_Name',
        'First_Signatory_Position': 'First_Signatory_Position',
        'First_Signatory_Path': 'First_Signatory_Path',
        'Second_Signatory_Name': 'Second_Signatory_Name',
        'Second_Signatory_Position': 'Second_Signatory_Position',
        'Second_Signatory_Path': 'Second_Signatory_Path',
        'form_type': 'form_type',
    }

    # Add mappings for Arabic & English form
    if data.get('form_type') == 'Arabic':
        key_mappings.update({
            'certificate_description_female': 'certificate_description_female',
            'certificate_description_male': 'certificate_description_male',
            'greeting_female': 'greeting_female',
            'greeting_male': 'greeting_male',
            'intro': 'intro',
            'male_recipient_title': 'male_recipient_title',
            'female_recipient_title': 'female_recipient_title',
        })
    elif data.get('form_type') == 'English':
        key_mappings.update({
            'certificate_description_female_en': 'certificate_description_female',
            'certificate_description_male_en': 'certificate_description_male',
            'greeting_female_en': 'greeting_female',
            'greeting_male_en': 'greeting_male',
            'intro_en': 'intro',
            'male_recipient_title_en': 'male_recipient_title',
            'female_recipient_title_en': 'female_recipient_title',
        })
    elif data.get('form_type') == 'Arabic_English':
        key_mappings.update({
            # Arabic form data
            'certificate_description_female': 'certificate_description_female',
            'certificate_description_male': 'certificate_description_male',
            'greeting_female': 'greeting_female',
            'greeting_male': 'greeting_male',
            'intro': 'intro',
            'male_recipient_title': 'male_recipient_title',
            'female_recipient_title': 'female_recipient_title',

            # English form data
            'certificate_description_female_en': 'certificate_description_female_en',
            'certificate_description_male_en': 'certificate_description_male_en',
            'greeting_female_en': 'greeting_female_en',
            'greeting_male_en': 'greeting_male_en',
            'intro_en': 'intro_en',
            'male_recipient_title_en': 'male_recipient_title_en',
            'female_recipient_title_en': 'female_recipient_title_en',
        })

    merged_data = {}
    for app_key, default_key in key_mappings.items():
        merged_data[default_key] = data.get(app_key, default_data.get(default_key))
    print(merged_data)
    return merged_data


def merge_customization_data(customization, default_customization):
    merged_customization = {}

    for key, value in default_customization.items():
        # Use the value from customization if it exists, otherwise use the default value
        merged_customization[key] = customization.get(key, value)

    return merged_customization


def generate_certificate(event_data, output_dir, item_positions):
    # Assuming util, configuration_loader, CSVGen, Certificate, etc. are defined in your script or imported modules
    event_dir = util.make_file_name_compatible(f"{event_data['certificate_event_id']}-{event_data['event_title']}-{datetime.datetime.now().isoformat()}")
    output_dir = os.path.join(output_dir, event_dir)
    util.make_sure_path_exists(output_dir)
    log.info(f"Saving output to: '{output_dir}'")

    # Read recipients data from CSV file specified in event_data
    list_of_recipients = util.read_csv_to_dict(event_data['csv_file'])

    log.debug(f"List of recipients: {list_of_recipients}")

    report = CSVGen()

    for recipient_data in list_of_recipients:
        log.debug("Before checking form type: %s", event_data['form_type'])
        # Determine the appropriate field names based on the form type
        if event_data['form_type'] == 'Arabic':
            first_name = recipient_data['arfirst_name']
            middle_name = recipient_data['armiddle_name']
            last_name = recipient_data['arlast_name']
            

        elif event_data['form_type'] == 'English':
            first_name = recipient_data['first_name']
            middle_name = recipient_data['middle_name']
            last_name = recipient_data['last_name']

        if event_data['form_type'] == 'Arabic_English':
            first_name_ar = recipient_data['arfirst_name']
            middle_name_ar = recipient_data['armiddle_name']
            last_name_ar = recipient_data['arlast_name']

            first_name_en = recipient_data['first_name'] if 'first_name' in recipient_data else recipient_data['arfirst_name']
            middle_name_en = recipient_data['middle_name'] if 'middle_name' in recipient_data else recipient_data['armiddle_name']
            last_name_en = recipient_data['last_name'] if 'last_name' in recipient_data else recipient_data['arlast_name']

        if (event_data['form_type'] == 'Arabic' or event_data['form_type'] == 'English'):
            
            full_name = util.get_gendered_full_name(first_name, middle_name, last_name, recipient_data['gender'],event_data['form_type'])
            
            # Store recipient info and get recipient ID
            recipient_id = store_recipient_info(recipient_data,first_name,middle_name,last_name)
            log.debug(f"Recipient ID: {recipient_id}")
            certificate = Certificate(recipient_name=full_name,
                                    recipient_title=event_data['male_recipient_title'] if recipient_data['gender'] == "male" else event_data['female_recipient_title'],
                                    recipient_email=recipient_data['email'],
                                    
                                    dean_name=event_data['First_Signatory_Name'],
                                    dean_position=event_data['First_Signatory_Position'],
                                    path_to_dean_signature=event_data['First_Signatory_Path'],
                                    csu_director_name=event_data['Second_Signatory_Name'],
                                    csu_position=event_data['Second_Signatory_Position'],
                                    path_to_csu_head_signature=event_data['Second_Signatory_Path'],
                                    certificate_intro=event_data['intro'],

                                    certificate_body=event_data['certificate_description_male'] if recipient_data['gender'] == "male" else event_data['certificate_description_female'],
                                    greeting_txt=event_data['greeting_male'] if recipient_data['gender'] == "male" else event_data['greeting_female'],
                                    certificate_template=event_data['template_path'],
                                    certificate_event_id=event_data['certificate_event_id'])
            
        elif event_data['form_type'] == 'Arabic_English':
                
            full_name_ar = util.get_gendered_full_name(first_name_ar, middle_name_ar, last_name_ar, recipient_data['gender'],event_data['form_type'])
            full_name_en = util.get_gendered_full_name(first_name_en, middle_name_en, last_name_en, recipient_data['gender'],event_data['form_type'])
            
            # Store recipient info and get recipient ID
            recipient_id = store_recipient_info(recipient_data,first_name_ar,middle_name_ar,last_name_ar)
            log.debug(f"Recipient ID: {recipient_id}")

            certificate = BilingualCertificate(
                                    # Arabic
                                    recipient_name=full_name_ar,
                                    recipient_title=event_data['male_recipient_title'] if recipient_data['gender'] == "male" else event_data['female_recipient_title'],
                                    recipient_email=recipient_data['email'],
                                    certificate_intro=event_data['intro'],
                                    certificate_body=event_data['certificate_description_male'] if recipient_data['gender'] == "male" else event_data['certificate_description_female'],
                                    greeting_txt=event_data['greeting_male'] if recipient_data['gender'] == "male" else event_data['greeting_female'],

                                    # English
                                    recipient_name_en=full_name_en,
                                    recipient_title_en=event_data['male_recipient_title_en'] if recipient_data['gender'] == "male" else event_data['female_recipient_title_en'],
                                    intro_en=event_data['intro_en'],
                                    certificate_body_en=event_data['certificate_description_male_en'] if recipient_data['gender'] == "male" else event_data['certificate_description_female_en'],
                                    greeting_txt_en=event_data['greeting_male_en'] if recipient_data['gender'] == "male" else event_data['greeting_female_en'],

                                    dean_name=event_data['First_Signatory_Name'],
                                    dean_position=event_data['First_Signatory_Position'],
                                    path_to_dean_signature=event_data['First_Signatory_Path'],
                                    csu_director_name=event_data['Second_Signatory_Name'],
                                    csu_position=event_data['Second_Signatory_Position'],
                                    path_to_csu_head_signature=event_data['Second_Signatory_Path'],

                                    certificate_template=event_data['template_path'],
                                    certificate_event_id=event_data['certificate_event_id'])

        certificate.generate_certificate(output_dir, item_positions)

        if (event_data['form_type'] == 'Arabic' or event_data['form_type'] == 'English'):
            report.add_datapoint({
                "name": full_name,
                "email": recipient_data['email'],
                "event_name": event_data['event_title'],
                "event_date": event_data['event_date'],
                "event_type": event_data['event_type'],
                "certificate_hash": certificate.certificate_hash,
                "date_issued": datetime.datetime.now().date()
            })

        elif event_data['form_type'] == 'Arabic_English':
            report.add_datapoint({
                "name_ar": full_name_ar,
                "name_en": full_name_en,
                "email": recipient_data['email'],
                "event_name": event_data['event_title'],
                "event_date": event_data['event_date'],
                "event_type": event_data['event_type'],
                "certificate_hash": certificate.certificate_hash,
                "date_issued": datetime.datetime.now().date()
            })

        # # Store recipient info and get recipient ID
        # recipient_id = store_recipient_info(recipient_data,first_name,middle_name,last_name)
        # log.debug(f"Recipient ID: {recipient_id}")

        # Store certificate hash
        hash = certificate.certificate_hash
        log.debug(f"Hash ID: {hash}")

        store_certificate_hash(hash, recipient_id, event_data['certificate_event_id'])

    # Generate report CSV
    report_filename = util.make_file_name_compatible(f"{event_data['certificate_event_id']}-{event_data['event_title']}-{event_data['event_date']}")
    report.write_to_csv(output_dir, report_filename)


def main(event_data, item_positions):
    # Load default data and merge with incoming data
    default_event_data = load_default_data()
    default_customization = load_default_cutomization()

    merged_event_data = merge_with_default(event_data, default_event_data)
    merged_customization = merge_customization_data(item_positions, default_customization)

    # Define output directory
    output_dir = "flask_website/static/output"

    # Generate certificates
    generate_certificate(merged_event_data, output_dir, merged_customization)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate certificates based on event data.")
    parser.add_argument('--event_data', type=str, help='JSON string of event data', default=None)
    parser.add_argument('--items_positions', type=str, help='Items positions as JSON', default=None)
    args = parser.parse_args()

    if args.event_data and args.items_positions:
        # If event data is provided, use it
        event_data = json.loads(args.event_data)
        items_positions=json.loads(args.items_positions)
        main(event_data,items_positions)
    elif args.event_data and (not args.items_positions):
        event_data = json.loads(args.event_data)
        items_positions = load_default_cutomization()
        main(event_data,items_positions)
    else:
        # If no event data is provided, use default data
        print("No event data provided, using default data.")
        # event_data = load_default_data()
        items_positions = load_default_cutomization()
        main({},items_positions)
