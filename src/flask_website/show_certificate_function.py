from db_classes import CertificateEvent
from flask import render_template
from flask_login import current_user

def certificates():
    # try:
        # Fetch the latest 3 certificates created by the current user from the database
        latest_certificates = CertificateEvent.query.filter_by(created_by=current_user.id).limit(3).all()

        # Render the 'certificates.html' template with the certificate data
        return render_template('certificates.html', latest_certificates=latest_certificates)

    # except Exception as e:
        # Handle any exceptions gracefully
        # return render_template('error.html', error=str(e))
