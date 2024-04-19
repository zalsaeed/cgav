from flask import jsonify, render_template, request
from db_classes import db, CertificateEvent, Certificate_table, recipient
import db_connection
import mail

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt



def delete_confirmation(certificate_event_id):
    event = CertificateEvent.query.get_or_404(certificate_event_id)

    if request.method == 'POST':
        event_name = request.json.get('event_name', '')

        if event_name != event.certificate_title:
            return jsonify({'success': False, 'error': 'Incorrect event name'}), 400


        # Send email notification about the deletion attempt
        if event.sended or event.downloaded:
            try:
                mail.send_delete_confirmation_email(certificate_event_id)
            except Exception as e:
                return jsonify({'success': False, 'error': 'Failed to send deletion notification email: ' + str(e)}), 500

        # Collect all recipients associated with the event
        associated_recipients = Certificate_table.query.filter_by(certificate_event_id=certificate_event_id).all()
        recipient_ids = {rec.recipient_id for rec in associated_recipients}

        # Delete the Certificate_table records first
        Certificate_table.query.filter_by(certificate_event_id=certificate_event_id).delete()

        try:
            # Delete the event
            db.session.delete(event)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Event deletion failed: ' + str(e)}), 500

        # Delete recipients if they are not linked to any other events
        for rec_id in recipient_ids:
            if not Certificate_table.query.filter_by(recipient_id=rec_id).first():
                recipient_to_delete = recipient.query.get(rec_id)
                db.session.delete(recipient_to_delete)

        try:
            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Recipient deletion failed: ' + str(e)}), 500

    return render_template('delete_confirmation.html', event=event)
