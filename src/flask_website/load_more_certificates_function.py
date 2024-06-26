from db_classes import CertificateEvent
from flask import request, jsonify
from flask_login import current_user

def load_more_certificates():
    try:
        # Get the number of certificates already loaded
        loaded_count = int(request.args.get('loaded_count', 0))

        # Fetch additional certificates from the database, excluding the ones already loaded
        additional_certificates = CertificateEvent.query \
            .filter(CertificateEvent.created_by == current_user.id) \
            .order_by(CertificateEvent.certificate_event_id.asc()) \
            .offset(loaded_count) \
            .limit(3) \
            .all()

        # Prepare a list of additional certificate details for JSON response
        additional_certificates_list = [
            {
                'certificate_title': certificate.certificate_title,
                'presenter_name': certificate.presenter_name,
                'certificate_event_id': certificate.certificate_event_id,
                'event_date': certificate.event_date.strftime('%Y-%m-%d'),
                'event_type_name': certificate.event_type.event_type_name,
                'certificate_description_female': certificate.certificate_description_female,
                'file_path': certificate.file_path if hasattr(certificate, 'file_path') else None
            }
            for certificate in additional_certificates
        ]

        # Return the list of additional certificate details as a JSON response
        return jsonify(additional_certificates_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
