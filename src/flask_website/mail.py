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
        include_event_info = request.form.get('include_event_info')  # Retrieve checkbox value

        # Query the event title using the event_id
        event = CertificateEvent.query.filter_by(certificate_event_id=event_id).first()
        certificate_title = event.certificate_title if event else 'the event'
        
        # Initialize event details based on selected language
        if language == 'ar':
            event_details = f"\n\nعنوان الحدث: {certificate_title}\nتاريخ الحدث: {event.event_date.strftime('%Y-%m-%d')}\n"
        else:  # Default to English if language is not specified or invalid
            event_details = f"\n\nEvent Title: {certificate_title}\nEvent Date: {event.event_date.strftime('%Y-%m-%d')}\n"

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
                msg = Message(subject=subject if subject else f'{certificate_title}', recipients=[email], sender='no-reply@example.com')

                # Add additional recipient details to the event details
                recipient_name = f"{recipient_details.first_name} {recipient_details.last_name}" if recipient_details else "N/A"
                
                # Add recipient name to event details based on language
                if language == 'ar':
                    event_details += f"اسم المتلقي: {recipient_name}\n"
                else:
                    event_details += f"Recipient Name: {recipient_name}\n"

                # Add presenter name based on language
                if language == 'ar':
                    event_details += f"اسم المقدم: {event.presenter_name}\n"
                else:
                    event_details += f"Presenter Name: {event.presenter_name}\n"

                # Construct email body based on custom or default values and checkbox selection
                if custom_content:
                    msg.body = custom_content
                else:
                    if language == 'ar':
                        if recipient_details and recipient_details.gender == 'male':
                            msg.body = f'عزيزي {recipient_details.first_name} {recipient_details.last_name},\n\nفي المرفق شهادة حضورك .'
                        elif recipient_details and recipient_details.gender == 'female':
                            msg.body = f'عزيزتي {recipient_details.first_name} {recipient_details.last_name},\n\nفي المرفق شهادة حضورك .'
                        else:
                            msg.body = f'عزيزي/تي المتدرب/ـة\n\nفي المرفق شهادة حضورك .'
                    else:
                        if recipient_details:
                            msg.body = f"Dear {recipient_details.first_name} {recipient_details.last_name},\n\nPlease find attached your certificate for."
                        else:
                            msg.body = f"Dear User,\n\nPlease find attached your certificate."

                    # Check if checkbox for event information is selected
                    if include_event_info == 'yes':
                        if language == 'ar':
                            msg.body += "\n\nمعلومات الحدث:" + event_details
                        else:
                            msg.body += "\n\nEvent Information:" + event_details
                            
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

# Function to send delete email notification (delete_confirm_function.py)
def send_delete_confirmation_email(event_id):
    # Fetch the event
    event = db.session.query(CertificateEvent).get(event_id)
    if not event:
        return "Event not found", 404

    # Fetch the administrator's email from the user who created the event
    admin = db.session.query(users).get(event.created_by)
    if not admin:
        return "Administrator not found", 404
    admin_email = admin.email

    # Collect emails from associated recipients
    recipients = db.session.query(recipient).join(Certificate_table, Certificate_table.recipient_id == recipient.recipient_id)\
                        .filter(Certificate_table.certificate_event_id == event_id).all()
    num_recipients = len(recipients)  # Number of recipients affected

    # Event details for email
    event_date_str = event.event_date.strftime('%Y-%m-%d')
    subject = f'Event Deletion Notification: {event.certificate_title}'

    # Detailed message for administrators
    admin_body = f"""
    Event Deletion Details
    
    Event Title: {event.certificate_title}
    Event Date: {event.event_date.strftime('%Y-%m-%d')}
    Event Type: {event.event_type.event_type_name}
    Presented by: {event.presenter_name}
    Event Description:
    """

    if event.certificate_description_male:
        admin_body += f"    Male (AR): {event.certificate_description_male}\n"
    if event.certificate_description_female:
        admin_body += f"    Female (AR): {event.certificate_description_female}\n"
    if event.certificate_description_male_en:
        admin_body += f"    Male (EN): {event.certificate_description_male_en}\n"
    if event.certificate_description_female_en:
        admin_body += f"    Female (EN): {event.certificate_description_female_en}\n"

    if event.greeting_male:
        admin_body += f"Greeting for Male (AR): {event.greeting_male}\n"
    if event.greeting_female:
        admin_body += f"Greeting for Female (AR): {event.greeting_female}\n"
    if event.greeting_male_en:
        admin_body += f"Greeting for Male (EN): {event.greeting_male_en}\n"
    if event.greeting_female_en:
        admin_body += f"Greeting for Female (EN): {event.greeting_female_en}\n"

    # Adding recipient titles if they exist
    if event.male_recipient_title:
        admin_body += f"Male Recipient Title (AR): {event.male_recipient_title}\n"
    if event.female_recipient_title:
        admin_body += f"Female Recipient Title (AR): {event.female_recipient_title}\n"
    if event.male_recipient_title_en:
        admin_body += f"Male Recipient Title (EN): {event.male_recipient_title_en}\n"
    if event.female_recipient_title_en:
        admin_body += f"Female Recipient Title (EN): {event.female_recipient_title_en}\n"

    # Introductory message if it exists
    if event.intro:
        admin_body += f"Intro Message: {event.intro}\n"
    if event.intro_en:
        admin_body += f"Intro Message (EN): {event.intro_en}\n"

    admin_body += f"""
    Number of Recipients Affected: {num_recipients}
    Certificates Sent: {'Yes' if event.sended else 'No'}
    Certificates Downloaded: {'Yes' if event.downloaded else 'No'}
    Generated Certificates: {'Yes' if event.generated_ else 'No'}
    Secret Phrase: {event.secret_phrase if event.secret_phrase else 'N/A'}
    File Path: {event.file_path if event.file_path else 'N/A'}
    Template Used: {event.template_path if event.template_path else 'N/A'}
    First Signatory: {event.First_Signatory_Name if event.First_Signatory_Name else 'N/A'}, Position: {event.First_Signatory_Position if event.First_Signatory_Position else 'N/A'}
    Second Signatory: {event.Second_Signatory_Name if event.Second_Signatory_Name else 'N/A'}, Position: {event.Second_Signatory_Position if event.Second_Signatory_Position else 'N/A'}
    
    The event and all associated data have been permanently deleted from the system. This includes all digital records and files related to the event.
    """



    # Send detailed email to administrator
    admin_msg = Message(subject, recipients=[admin_email], sender='no-reply@example.com')
    admin_msg.body = admin_body
    try:
        mail.send(admin_msg)
    except Exception as e:
        return f"Failed to send administrative email: {str(e)}", 500

    # Notify each recipient with a personalized message
    for r in recipients:
        recipient_body = f"Dear {r.first_name} {r.last_name},\n\nWe regret to inform you that the event titled '{event.certificate_title}', scheduled for {event_date_str}, has been permanently deleted from our system. As a result, your certificate for this event will no longer be verifiable via our System."
        recipient_msg = Message(subject, recipients=[r.email], sender='no-reply@example.com')
        recipient_msg.body = recipient_body
        try:
            mail.send(recipient_msg)
        except Exception as e:
            return f"Failed to send email to {r.email}: {str(e)}", 500

    return "Emails sent successfully", 200

if __name__ == '__main__':
    app.run(debug=True)
