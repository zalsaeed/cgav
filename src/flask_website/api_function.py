from flask import jsonify
# Adjust imports to match the correct class names and file structure
from db_classes import Certificate_table as CertificateTable
from db_classes import recipient as Recipient
from db_classes import CertificateEvent as AddCertificate


import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt


db = db_connection.db

def verify_certificate_api(certificate_hash):
    # Query for the certificate based on the hash
    certificate = CertificateTable.query.filter_by(certificate_hash=certificate_hash).first()
    if certificate:
        recipient = Recipient.query.filter_by(recipient_id=certificate.recipient_id).first()
        certificate_event = AddCertificate.query.filter_by(certificate_event_id=certificate.certificate_event_id).first()

        recipient_name = recipient.first_name + ' ' + recipient.last_name if recipient else "Unknown Recipient"

        return jsonify({
            'valid': True,
            'certificate_details': {
                'recipient_name': recipient_name,
                'certificate_title': certificate_event.certificate_title if certificate_event else "Unknown Title",
                'presenter_name': certificate_event.presenter_name if certificate_event else "Unknown Presenter",
                'event_date': certificate_event.event_date.strftime("%Y-%m-%d") if certificate_event and certificate_event.event_date else None,
            }
        }), 200
    else:
        return jsonify({'valid': False, 'error': 'Certificate is invalid or not found.'}), 404
