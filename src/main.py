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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Command line utility for CGAV.")
    parser.add_argument("-e", "--event", type=str, default="events/sample-event.yaml",
                        help="The file for event information settings.")
    # parser.add_argument("-o", "--output", type=str, default="output",
    #                     help="The output directory where all certificates will be saved.")
    parser.add_argument("-o", "--output", type=str, default="flask_website/static/output",
                        help="The output directory where all certificates will be saved.")

    # get arguments
    args = parser.parse_args()

    event_info = configuration_loader.Settings()
    event_info.read_yaml(open(os.path.abspath(args.event)))

    event_dir = util.make_file_name_compatible(f"{event_info['event_title']}-{datetime.datetime.today().isoformat()}")
    output_dir = os.path.abspath(f"{args.output}/{event_dir}")
    util.make_sure_path_exists(output_dir)
    log.info(f"Saving output to: '{output_dir}'")

    list_of_recipients = util.read_csv_to_dict(str(event_info['csv_file']))

    log.debug(f"List of recipients: {list_of_recipients}")

    report = CSVGen()

    for recipient in list_of_recipients:

        full_name = util.get_gendered_full_name(recipient['first_name'],
                                                recipient['middle_name'],
                                                recipient['last_name'],
                                                recipient['gender'])

        certificate = Certificate(recipient_name=full_name,
                                  recipient_title=str(event_info['male_recipient_title']) if recipient['gender'] == "male" else str(event_info['female_recipient_title']),
                                  recipient_email=recipient['email'],
                                  dean_name=str(event_info['dean_name']),
                                  dean_position=str(event_info['dean_position']),
                                  path_to_dean_signature=str(event_info['path_to_dean_signature']),
                                  csu_director_name=str(event_info['csu_director_name']),
                                  csu_position=str(event_info['csu_position']),
                                  path_to_csu_head_signature=str(event_info['path_to_csu_signature']),
                                  certificate_intro=str(event_info['intro']),
                                  certificate_body=str(event_info['male_certificate_body']) if recipient['gender'] == "male" else str(event_info['female_certificate_body']),
                                  greeting_txt=str(event_info['male_final_greeting']) if recipient['gender'] == "male" else str(event_info['female_final_greeting']),
                                  certificate_template=str(event_info['certificate_background']))

        certificate.generate_certificate(output_dir)

        report.add_datapoint({
            "name": full_name,
            "email": recipient['email'],
            "event_name": event_info['event_title'],
            "event_date": event_info['event_date'],
            "event_type": event_info['event_type'],
            "certificate_hash": certificate.certificate_hash,
            "date_issued": datetime.datetime.today().date()
        })

    report.write_to_csv(output_dir,
                        util.make_file_name_compatible(f"{event_info['event_title']}-{event_info['event_date']}"))
