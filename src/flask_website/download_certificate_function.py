import os
import shutil
from flask import send_from_directory

def download_certificates(event_id):
    # Define the path to the output directory
    output_directory = os.path.abspath("/root/src/flask_website/static/output")

    # Search for the folder corresponding to the event ID
    event_folder = None
    for folder_name in os.listdir(output_directory):
        if folder_name.startswith(f"{event_id}-"):
            event_folder = os.path.join(output_directory, folder_name)
            break

    if event_folder is None:
        return "Event folder not found", 404

    # Create a zip file containing the contents of the event folder
    zip_file_name = f'event_{event_id}_certificates.zip'
    zip_file_path = os.path.join(os.getcwd(), zip_file_name)
    shutil.make_archive(zip_file_path[:-4], 'zip', event_folder)

    # Send the zip file for download
    return send_from_directory(os.getcwd(), zip_file_name, as_attachment=True)