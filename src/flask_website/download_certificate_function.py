from db_classes import CertificateEvent
from db_connection import db

import os
import tempfile
import shutil
from flask import send_from_directory, jsonify


def download_certificates(event_id, selected_certificates=None):
    output_directory = os.path.abspath("/root/src/flask_website/static/output")
    event_folder = None
    for folder_name in os.listdir(output_directory):
        if folder_name.startswith(f"{event_id}-"):
            event_folder = os.path.join(output_directory, folder_name)
            break

    if event_folder is None:
        return "Event folder not found", 404

    zip_file_name = f'event_{event_id}_certificates.zip'
    zip_file_path = os.path.join(os.getcwd(), zip_file_name)

    if selected_certificates:
        # Create a zip file with selected certificates
        with tempfile.TemporaryDirectory() as temp_dir:
            for certificate in selected_certificates:
                certificate_path = os.path.join(event_folder, certificate)
                if os.path.isfile(certificate_path):
                    shutil.copy(certificate_path, temp_dir)

            shutil.make_archive(zip_file_path[:-4], 'zip', temp_dir)
    else:
        # Create a zip file with all certificates in the event folder
        shutil.make_archive(zip_file_path[:-4], 'zip', event_folder)

    # Update certificate status
    certificate = CertificateEvent.query.get_or_404(event_id)
    certificate.downloaded = True
    db.session.commit()

    return send_from_directory(os.getcwd(), zip_file_name, as_attachment=True)

def get_certificate_list(event_id):
    output_directory = os.path.abspath("/root/src/flask_website/static/output")
    event_folder = None
    for folder_name in os.listdir(output_directory):
        if folder_name.startswith(f"{event_id}-"):
            event_folder = os.path.join(output_directory, folder_name)
            break

    if event_folder is None:
        return jsonify({"error": "Event folder not found"}), 404

    certificates = [f for f in os.listdir(event_folder) if f.endswith('.pdf')]
    return jsonify({"certificates": certificates})

