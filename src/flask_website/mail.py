# import os 

# from flask import Flask,request,flash,render_template
# from flask_mail import Mail, Message
# from dotenv import load_dotenv

# import db_connection

# app = db_connection.app
# # db = db_connection.db
# # bcrypt = db_connection.bcrypt

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

# def send_email():
#     if request.method == 'POST':
#         selected_emails = request.form.getlist('emails')

#         # Get the custom email details from the form
#         subject = request.form.get('subject')
#         custom_content = request.form.get('custom-content')

#         # Iterate over selected emails
#         for email in selected_emails:
#             # Find the PDF file for the user
#             certificate_folder = os.path.join(os.path.dirname(__file__), 'sample-event')
#             pdf_files = [f for f in os.listdir(certificate_folder) if f.startswith(f"{email}-") and f.endswith(".pdf")]

#             if pdf_files:
#                 # Use the first PDF file found for the user
#                 certificate_filename = os.path.join(certificate_folder, pdf_files[0])

#                 # Construct the message
#                 msg = Message('Your Certificate', recipients=[email], sender='no-reply@example.com')

#                 # Use custom or default values
#                 if  subject and custom_content:
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
#                 print(f"Certificate not found for {email}")

#         # Check if custom values were used
#         if subject and custom_content:
#             flash("Custom emails sent successfully!", "success")
#         else:
#             flash("Default emails sent successfully!", "success")

#     return render_template('send_email.html')


import os
import logging

from flask import Flask, request, flash, render_template
from flask_mail import Mail, Message
from dotenv import load_dotenv

import db_connection

app = db_connection.app

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

def send_email():
    logger.debug("Inside send_email function")
    if request.method == 'POST':
        selected_emails = request.form.getlist('emails')
        logger.debug("Selected Emails: %s", selected_emails)

        # Get the custom email details from the form
        subject = request.form.get('subject')
        custom_content = request.form.get('custom-content')
        logger.debug("Subject: %s", subject)
        logger.debug("Custom Content: %s", custom_content)

        # Iterate over selected emails
        for email in selected_emails:
            # Find the PDF file for the user
            certificate_folder = os.path.join(os.path.dirname(__file__), 'static/output/sample-event-2024-01-30t18:53:15.396730')
            logger.debug("Certificate Folder: %s", certificate_folder)
            pdf_files = [f for f in os.listdir(certificate_folder) if f.startswith(f"{email}-") and f.endswith(".pdf")]
            logger.debug("PDF Files: %s", pdf_files)

            if pdf_files:
                # Use the first PDF file found for the user
                certificate_filename = os.path.join(certificate_folder, pdf_files[0])
                logger.debug("Certificate Filename: %s", certificate_filename)

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

        # Check if custom values were used
        if subject and custom_content:
            flash("Custom emails sent successfully!", "success")
        else:
            flash("Default emails sent successfully!", "success")

    return render_template('send_email.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)