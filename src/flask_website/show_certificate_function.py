from db_classes import CertificateEvent
from flask import render_template

def certificates():
    # Fetch the latest 3 certificates and all certificates from the database
    latest_certificates = CertificateEvent.query.limit(3).all()
    all_certificates = CertificateEvent.query.all()

    # Render the 'certificates.html' template with the certificate data
    return render_template('certificates.html', latest_certificates=latest_certificates, all_certificates=all_certificates)