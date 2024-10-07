from flask import jsonify, render_template, request
from db_classes import Certificate_table, recipient as RecipientModel, CertificateEvent , api_config
import db_connection
from flask_login import current_user


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt


saved_api_url = None  # Initialize as None or an appropriate default value


@app.route('/save_api_url', methods=['POST'])
def save_api_url():
    user_id = current_user.id if current_user.is_authenticated else None  # Assuming Flask-Login for user management
    api_url = request.json.get('apiUrl')

    if not api_url:
        return jsonify({'error': 'API URL cannot be empty!'}), 400

    if user_id is None:
        return jsonify({'error': 'User must be logged in to save an API URL.'}), 403

    try:
        new_api_config = api_config(user_id=user_id, api_url=api_url)
        db.session.add(new_api_config)
        db.session.commit()
        return jsonify({'message': 'API URL saved successfully!', 'apiUrl': api_url}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400




def verify_certificate_api(certificate_hash):
    # Query for the certificate based on the hash
    certificate = Certificate_table.query.filter_by(certificate_hash=certificate_hash).first()
    if certificate:
        recipient_data = RecipientModel.query.filter_by(recipient_id=certificate.recipient_id).first()
        certificate_event = CertificateEvent.query.filter_by(
            certificate_event_id=certificate.certificate_event_id).first()

        recipient_name = recipient_data.first_name + ' ' + recipient_data.last_name if recipient_data else "Unknown Recipient"

        return jsonify({
            'valid': True,
            'certificate_details': {
                'recipient_name': recipient_name,
                'certificate_title': certificate_event.certificate_title if certificate_event else "Unknown Title",
                'presenter_name': certificate_event.presenter_name if certificate_event else "Unknown Presenter",
                'event_date': certificate_event.event_date.strftime(
                    "%Y-%m-%d") if certificate_event and certificate_event.event_date else None,
            }
        }), 200
    else:
        return jsonify({'valid': False, 'error': 'Certificate is invalid or not found.'}), 404



@app.route('/manage_api_url')
def manage_api_url():
    # Assuming api_config has a user_id field linking to the users table
    last_api = api_config.query.filter_by(user_id=current_user.id).order_by(api_config.id.desc()).first()
    last_api_url = last_api.api_url if last_api else "No API URL saved yet"
    return render_template('manage_api_url.html', api_url=last_api_url)


