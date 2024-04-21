from flask import  jsonify, url_for
import os

def preview_certificates(event_id):
    output_directory = os.path.abspath("/root/src/flask_website/static/output")
    event_folder = None
    for folder_name in os.listdir(output_directory):
        if folder_name.startswith(f"{event_id}-"):
            event_folder = os.path.join(output_directory, folder_name)
            break

    if event_folder:
        certificates = [url_for('get_certificate', event_id=event_id, filename=f) for f in os.listdir(event_folder) if f.endswith('.pdf')]
        return jsonify({'certificates': certificates})
    
    return jsonify({'error': 'No certificates available for preview'}), 404