from db_classes import CertificateEvent
from flask import request, jsonify, render_template
from flask_mail import Message
from sqlalchemy.orm.session import object_session
import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt


def delete_confirmation(certificate_event_id):
    certificate = CertificateEvent.query.get_or_404(certificate_event_id)

    # Check if the certificate is already attached to a session
    existing_session = object_session(certificate)

    if existing_session:
        existing_session.expunge(certificate)

    if request.method == 'POST':
        try:
            # Verify the event name for confirmation
            event_name = request.json.get('event_name', '')

            if event_name == certificate.certificate_title:
                # Delete the certificate
                db.session.delete(certificate)
                db.session.commit()

                # Send email notification
               # send_delete_confirmation_email(certificate)

                # Provide a success response
                return jsonify({'success': True}), 200  # Return 200 OK status

            else:
                # Provide an error response (incorrect event name)
                return jsonify({'success': False, 'error': 'Incorrect event name'}), 400

        except Exception as e:
            # Provide an error response (server error)
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('delete_confirmation.html', certificate=certificate)


# Function to send email notification
#def send_delete_confirmation_email(certificate):
#    recipient_email = app.config['MAIL_USERNAME']  # Assuming recipient_email is a string or list
#
#    if isinstance(recipient_email, str):
#        recipient_email = [recipient_email]  # Convert the string to a list with a single element
#
#    # Extract information from the certificate object
#    certificate_title = certificate.certificate_title
#    presenter_name = certificate.presenter_name
#    # Add more fields as needed
#
#    # Construct the email message
#    subject = f'Certificate Deleted: {certificate_title}'
#    body = f'Dear user,\n\nYour certificate "{certificate_title}" presented by {presenter_name} has been deleted successfully.'
#
#    msg = Message(subject, recipients=recipient_email, sender=app.config['MAIL_USERNAME'])
#    msg.body = body
#    db_connection.mail.send(msg)