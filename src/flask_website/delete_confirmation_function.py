from db_classes import CertificateEvent, Certificate_table
from flask import request, jsonify, render_template
import os
import shutil
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

        # Check if the certificate was either sent, downloaded, or generated
        if event.sended or event.downloaded:
            # Send email notification about the deletion attempt
            try:
                mail.send_delete_confirmation_email(certificate_event_id)
            except Exception as e:
                return jsonify({'success': False, 'error': 'Failed to send deletion notification email: ' + str(e)}), 500

        # Attempt to delete the event folder if generated
        if event.generated_:
            output_directory = os.path.abspath("/root/src/flask_website/static/output")
            event_folder = None
            for folder_name in os.listdir(output_directory):
                if folder_name.startswith(f"{certificate_event_id}-"):
                    event_folder = os.path.join(output_directory, folder_name)
                    break
            
            if event_folder:
                try:
                    shutil.rmtree(event_folder)
                except Exception as e:
                    return jsonify({'success': False, 'error': 'Failed to delete event folder: ' + str(e)}), 500

        try:
            # First delete dependent records
            Certificate_table.query.filter_by(certificate_event_id=certificate_event_id).delete()

            # Now attempt to delete the event
            db.session.delete(event)
            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Deletion failed: ' + str(e)}), 500

    return render_template('delete_confirmation.html', event=event)