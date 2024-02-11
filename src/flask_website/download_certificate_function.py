import os
import  shutil
from flask import send_from_directory

def download_certificates():
    # The path to the latest event folder
    latest_event_folder = os.path.abspath("/root/src/flask_website/static/output")

    # Create a zip file containing all PDFs in the folder
    zip_file_path = os.path.join(os.getcwd(), 'latest_event_certificates.zip')
    shutil.make_archive(zip_file_path[:-4], 'zip', latest_event_folder)

    # Send the zip file for download
    return send_from_directory(os.getcwd(), 'latest_event_certificates.zip', as_attachment=True)
