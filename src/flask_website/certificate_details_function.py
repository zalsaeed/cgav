from db_classes import CertificateEvent
from flask import render_template

def certificate_details(certificate_event_id):
    # Fetch the details of a specific certificate by its event ID
    certificate = CertificateEvent.query.get_or_404(certificate_event_id)

    # Render the 'certificate_details.html' template with the specific certificate details
    return render_template('certificate_details.html', certificate=certificate)