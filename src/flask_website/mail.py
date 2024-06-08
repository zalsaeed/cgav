from flask import Flask, request, flash, render_template, redirect, url_for, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import logging
from db_classes import Certificate_table, recipient, CertificateEvent, users  # Assuming you have SQLAlchemy models defined in models.py
from db_connection import db

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

@app.route('/send_email', methods=['GET', 'POST'])
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
                                     
        return render_template('send_email.html', recipients=recipients, eventId=event_id)

    elif request.method == 'POST':
        full_event_id = request.args.get('eventId')
        event_id = full_event_id.split('=')[-1]  # Extract the numerical part
        selected_emails = request.form.getlist('emails')
        subject = request.form.get('subject')
        custom_content = request.form.get('custom-content')
        language = request.form.get('language')

        # Query the event title using the event_id
        event = CertificateEvent.query.filter_by(certificate_event_id=event_id).first()
        certificate_title = event.certificate_title if event else 'the event'
        

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

                # Query the recipient's details
                recipient_details = recipient.query.filter_by(email=email).first()

                # Construct the message
                msg = Message(f'{certificate_title}', recipients=[email], sender='no-reply@example.com')

                # Use custom or default values
                if subject and custom_content:
                    msg.subject = subject
                    msg.body = custom_content
                else:
                    if language == 'ar':
                        if recipient_details and recipient_details.gender == 'male':
                            msg.body = f'عزيزي {recipient_details.first_name} {recipient_details.last_name},\n\nفي المرفق شهادة حضورك .'
                        elif recipient_details and recipient_details.gender == 'female':
                            msg.body = f'عزيزتي {recipient_details.first_name} {recipient_details.last_name},\n\nفي المرفق شهادة حضورك  .'
                        else:
                            msg.body = f'عزيزي/تي المتدرب/ـة\n\nفي المرفق شهادة حضورك  .'
                    else:
                        if recipient_details:
                            msg.body = f"Dear {recipient_details.first_name} {recipient_details.last_name},\n\nPlease find attached your certificate for."
                        else:
                            msg.body = f"Dear User,\n\nPlease find attached your certificate."

                # Attach the certificate to the email
                with app.open_resource(certificate_filename) as certificate:
                    msg.attach(email + '_certificate.pdf', 'application/pdf', certificate.read())

                # Send the email
                mail.send(msg)
                
                # Update certificate status to indicate it has been sent
                certificate = CertificateEvent.query.get_or_404(event_id)
                certificate.sended = True
                db.session.commit()

            else:
                # No certificate file found for the user
                logger.debug("Certificate not found for %s", email)

        if subject and custom_content:
            flash("Custom emails sent successfully!", "success")
        else:
            flash("Default emails sent successfully!", "success")

        return redirect(url_for('send_email', eventId=event_id))

if __name__ == '__main__':
    app.run(debug=True)
