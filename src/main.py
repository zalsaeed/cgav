import os
import logging
import datetime
import argparse
import fpdf

import util
import configuration_loader
from csv_gen import CSVGen
from certificate import Certificate

# set up logger
for handler in logging.root.handlers[:]:  # make sure all handlers are removed
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

# Define a function to load default data from the YAML file
def load_default_data():
    with open('events/sample-event.yaml', 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def merge_with_default(data, default_data):
    key_mappings = {
        'certificate_title': 'event_title',
        'file_path': 'csv_file',
        'certificate_description_female': 'certificate_body_female', 
        'certificate_description_male': 'certificate_body_male',
        'First_Signatory_Name': 'dean_name',
        'First_Signatory_Position': 'dean_position',
        'First_Signatory_Path': 'path_to_dean_signature',
        'Second_Signatory_Name': 'csu_director_name',
        'Second_Signatory_Position': 'csu_position',
        'Second_Signatory_Path': 'path_to_csu_signature',  # Ensure this key is correctly mapped
        'greeting_female': 'female_final_greeting',
        'greeting_male': 'male_final_greeting',
        'intro': 'intro',
        'male_recipient_title': 'male_recipient_title',
        'female_recipient_title': 'female_recipient_title',
        'template_path': 'certificate_background',
        'event_date': 'event_date',
        'event_type_id': 'event_type',
        
    }

    merged_data = {}
    for app_key, default_key in key_mappings.items():
        merged_data[default_key] = data.get(app_key, default_data.get(default_key))

    return merged_data

# Placeholder function for certificate generation 
def generate_certificate(event_data, output_dir):
    # Assuming util, configuration_loader, CSVGen, Certificate, etc. are defined in your script or imported modules
    event_dir = util.make_file_name_compatible(f"{event_data['event_title']}-{datetime.datetime.now().isoformat()}")
    output_dir = os.path.join(output_dir, event_dir)
    util.make_sure_path_exists(output_dir)
    log.info(f"Saving output to: '{output_dir}'")

    # Read recipients data from CSV file specified in event_data
    list_of_recipients = util.read_csv_to_dict(event_data['csv_file'])

    log.debug(f"List of recipients: {list_of_recipients}")

    report = CSVGen()

    for recipient in list_of_recipients:
        full_name = util.get_gendered_full_name(recipient['first_name'],
                                                recipient['middle_name'],
                                                recipient['last_name'],
                                                recipient['gender'])

        certificate = Certificate(recipient_name=full_name,
                                  recipient_title=event_data['male_recipient_title'] if recipient['gender'] == "male" else event_data['female_recipient_title'],
                                  recipient_email=recipient['email'],
                                  dean_name=event_data['dean_name'],
                                  dean_position=event_data['dean_position'],
                                  path_to_dean_signature=event_data['path_to_dean_signature'],
                                  csu_director_name=event_data['csu_director_name'],
                                  csu_position=event_data['csu_position'],
                                  path_to_csu_head_signature=event_data['path_to_csu_signature'],
                                  certificate_intro=event_data['intro'],
                                  certificate_body = event_data['certificate_body_male'] if recipient['gender'] == "male" else event_data['certificate_body_female'],
                                  greeting_txt=event_data['male_final_greeting'] if recipient['gender'] == "male" else event_data['female_final_greeting'],
                                  certificate_template=event_data['certificate_background'])

        certificate.generate_certificate(output_dir)

        report.add_datapoint({
            "name": full_name,
            "email": recipient['email'],
            "event_name": event_data['event_title'],
            "event_date": event_data['event_date'],
            "event_type": event_data['event_type'],
            "certificate_hash": certificate.certificate_hash,
            "date_issued": datetime.datetime.now().date()
        })
     # Generate report CSV
    report_filename = util.make_file_name_compatible(f"{event_data['event_title']}-{event_data['event_date']}")
    report.write_to_csv(output_dir, report_filename)

    # report.write_to_csv(output_dir,
    #                     util.make_file_name_compatible(f"{event_info['event_title']}-{event_info['event_date']}"))
def main(event_data):
    # Load default data and merge with incoming data
    default_event_data = load_default_data()
    merged_event_data = merge_with_default(event_data, default_event_data)

    # Define output directory
    output_dir = "flask_website/static/output"

    # Generate certificates
    generate_certificate(merged_event_data, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate certificates based on event data.")
    parser.add_argument('--event_data', type=str, help='JSON string of event data', default=None)

    args = parser.parse_args()

    if args.event_data:
        # If event data is provided, use it
        event_data = json.loads(args.event_data)
        main(event_data)
    else:
        # If no event data is provided, use default data
        print("No event data provided, using default data.")
        main({})
