# import os
# import logging

# from flask import Flask, request, flash, render_template
# from flask_mail import Mail, Message
# from dotenv import load_dotenv

# import db_connection

# app = db_connection.app

# # Load environment variables from the .env file
# load_dotenv()

# # Mail Server Configuration
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'true'
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# mail = Mail(app)

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# def send_email():
#     logger.debug("Inside send_email function")
#     if request.method == 'POST':
#         selected_emails = request.form.getlist('emails')
#         logger.debug("Selected Emails: %s", selected_emails)

#         # Get the custom email details from the form
#         subject = request.form.get('subject')
#         custom_content = request.form.get('custom-content')
#         logger.debug("Subject: %s", subject)
#         logger.debug("Custom Content: %s", custom_content)

#         # Iterate over selected emails
#         for email in selected_emails:
#             # Find the PDF file for the user
#             certificate_folder = os.path.join(os.path.dirname(__file__), 'static/output/sample-event-2024-01-30t18:53:15.396730')
#             logger.debug("Certificate Folder: %s", certificate_folder)
#             pdf_files = [f for f in os.listdir(certificate_folder) if f.startswith(f"{email}-") and f.endswith(".pdf")]
#             logger.debug("PDF Files: %s", pdf_files)

#             if pdf_files:
#                 # Use the first PDF file found for the user
#                 certificate_filename = os.path.join(certificate_folder, pdf_files[0])
#                 logger.debug("Certificate Filename: %s", certificate_filename)

#                 # Construct the message
#                 msg = Message('Your Certificate', recipients=[email], sender='no-reply@example.com')

#                 # Use custom or default values
#                 if subject and custom_content:
#                     msg.subject = subject
#                     msg.body = custom_content
#                 else:
#                     msg.body = 'Dear User,\n\nPlease find attached your certificate.'

#                 # Attach the certificate to the email
#                 with app.open_resource(certificate_filename) as certificate:
#                     msg.attach(email + '_certificate.pdf', 'application/pdf', certificate.read())

#                 # Send the email
#                 mail.send(msg)
#             else:
#                 # No certificate file found for the user
#                 logger.debug("Certificate not found for %s", email)

#         # Check if custom values were used
#         if subject and custom_content:
#             flash("Custom emails sent successfully!", "success")
#         else:
#             flash("Default emails sent successfully!", "success")

#     return render_template('send_email.html')

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True)


from flask import Flask, request, flash, render_template, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging
from db_classes import Certificate_table, recipient  # Assuming you have SQLAlchemy models defined in models.py

app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Mail Server Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#@app.route('/send_email', methods=['GET', 'POST'])
def send_email():
    event_id = None  # Initialize event_id outside the conditional blocks
    # logger.debug("Event ID from request: %s", event_id)
    if request.method == 'GET':
        # Retrieve the event ID from the query parameter
        event_id = request.args.get('eventId')
        logger.debug("Event ID from GET request: %s", event_id)
        # Define the path to the output directory
        output_directory = os.path.abspath("/root/src/flask_website/static/output")

        # Search for the folder corresponding to the event ID
        event_folder = None
        for folder_name in os.listdir(output_directory):
            if folder_name.startswith(f"{event_id}-"):
                event_folder = os.path.join(output_directory, folder_name)
                break

        # if event_folder is None:
        #     return "Event folder not found", 404
        
        # Query the database to retrieve recipient emails based on the event ID
        recipients = recipient.query.join(Certificate_table, recipient.recipient_id == Certificate_table.recipient_id)\
                                     .filter(Certificate_table.certificate_event_id == event_id)\
                                     .all()
                                     
        return render_template('send_email.html', recipients=recipients)

    elif request.method == 'POST':
        full_event_id = request.args.get('eventId')
        event_id = full_event_id.split('=')[-1]  # Extract the numerical part
        selected_emails = request.form.getlist('emails')
        subject = request.form.get('subject')
        custom_content = request.form.get('custom-content')

        # Use the event_id obtained in the GET request
        # if not event_id:
        #     return "Event ID is missing", 400

        for email in selected_emails:
            # Define the path to the output directory
            output_directory = os.path.abspath("/root/src/flask_website/static/output")

            # Search for the folder corresponding to the event ID
            event_folder = None
            logger.debug("Event ID from POST request: %s", event_id)
            for folder_name in os.listdir(output_directory):
                if folder_name.startswith(f"{event_id}-"):
                    event_folder = os.path.join(output_directory, folder_name)
                    break

            if event_folder is None:
                return "Event folder not found", 404

            # Search for the PDF file corresponding to the email
            pdf_files = [f for f in os.listdir(event_folder) if f.startswith(f"{email}-") and f.endswith(".pdf")]

            if pdf_files:
                # Use the first PDF file found for the user
                certificate_filename = os.path.join(event_folder, pdf_files[0])

                # Construct the message
                msg = Message('Your Certificate', recipients=[email], sender='no-reply@example.com')

                # Use custom or default values
                if subject and custom_content:
                    msg.subject = subject
                    msg.body = custom_content
                else:
                    msg.body = 'Dear User,\n\nPlease find attached your certificate.'

                # Attach the certificate to the email
                with app.open_resource(certificate_filename) as certificate:
                    msg.attach(email + '_certificate.pdf', 'application/pdf', certificate.read())

                # Send the email
                mail.send(msg)
            else:
                # No certificate file found for the user
                logger.debug("Certificate not found for %s", email)

        if subject and custom_content:
            flash("Custom emails sent successfully!", "success")
        else:
            flash("Default emails sent successfully!", "success")

        return redirect(url_for('send_email'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
