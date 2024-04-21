from flask import send_from_directory, safe_join, abort
import os

def get_certificate(event_id, filename):
    output_directory = os.path.abspath("/root/src/flask_website/static/output")
    event_folder = None
    for folder_name in os.listdir(output_directory):
        if folder_name.startswith(f"{event_id}-"):
            event_folder = os.path.join(output_directory, folder_name)
            break
    
    if event_folder:
        file_path = safe_join(event_folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(event_folder, filename)
        else:
            abort(404)
    abort(404)