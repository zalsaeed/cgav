from flask import request, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from io import StringIO
import csv
import os
import uuid

from db_classes import CertificateForm, EventType, Template, CertificateEvent

from db_connection import db, app

# Local App/Library Specific Imports
import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'certificate-templates')

# Ensure the upload_folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



def add_certificate():
    form = CertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    # Retrieve active event types and templates from the database
    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in
                               active_event_types]
    # Retrieve the selected template
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    templates = Template.query.all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    if form.validate_on_submit():

        selected_template_id = form.template_choice.data
        selected_template = Template.query.filter_by(template_id=selected_template_id).first()
        template_path = selected_template.template_image

        file = form.file.data
        if file and allowed_file(file.filename):
            # Read the file into a StringIO object for parsing as CSV
            file_stream = StringIO(file.read().decode('utf-8-sig'), newline=None)
            csv_reader = csv.DictReader(file_stream)  # Use DictReader to read the CSV into a dictionary

            # Updated required headers
            required_headers = {'first_name', 'middle_name', 'last_name', 'email', 'phone', 'gender'}
            if not required_headers.issubset(set(csv_reader.fieldnames)):
                message = 'The CSV file does not have the required headers.'
            else:
                # The CSV has the required headers, so save the file and the event
                file.seek(0)  # Seek back to the start of the file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                signature_image_1 = form.signature_image_1.data
                signature_image_2 = form.signature_image_2.data

                # Path where signature images will be saved
                signatures_folder = 'signatures'  # This should be the path to the signatures folder

                if signature_image_1 and allowed_image_file(signature_image_1.filename):
                    # Construct filename and save the first signature image
                    filename_1 = secure_filename(signature_image_1.filename)
                    image_path_1 = os.path.join(signatures_folder, filename_1)
                    signature_image_1.save(image_path_1)

                if signature_image_2 and allowed_image_file(signature_image_2.filename):
                    # Construct filename and save the second signature image
                    filename_2 = secure_filename(signature_image_2.filename)
                    image_path_2 = os.path.join(signatures_folder, filename_2)
                    signature_image_2.save(image_path_2)
                else:
                    # Set second signatory details to None or empty string
                    signatory_name_2 = None
                    signatory_position_2 = None
                    image_path_2 = None

                new_certificate_event = CertificateEvent(
                    certificate_title=form.certificate_title.data,
                    event_type_id=form.event_type.data,
                    template_path=template_path,
                    presenter_name=form.presenter_name.data,
                    secret_phrase=form.secret_phrase.data,
                    event_date=form.date.data,
                    certificate_description_female=form.certificate_description_female.data,
                    certificate_description_male=form.certificate_description_male.data,
                    file_path=file_path,
                    First_Signatory_Name=form.signatory_name_1.data,
                    First_Signatory_Position=form.signatory_position_1.data,
                    First_Signatory_Path=image_path_1,
                    Second_Signatory_Name=form.signatory_name_2.data,
                    Second_Signatory_Position=form.signatory_position_2.data,
                    Second_Signatory_Path=image_path_2,
                    greeting_female=form.greeting_female.data,
                    greeting_male=form.greeting_male.data,
                    intro=form.intro.data,
                    male_recipient_title=form.male_recipient_title.data,
                    female_recipient_title=form.female_recipient_title.data,
                )


                # Add the new event to the session and commit it to the database
                try:
                    db.session.add(new_certificate_event)
                    db.session.commit()
                except Exception as e:
                    print("Failed to commit to database:", e)
                    # Optionally, roll back the session in case of failure
                    db.session.rollback()

                return redirect(url_for('certificates'))  # Redirect to the dashboard after successful upload
        else:
            message = 'Please upload a CSV file.'

    return render_template(
        'add_certificate.html',
        form=form,
        message=message,
        show_second_signatory=show_second_signatory
    )


# Ensure you have your CertificateEvent model, EventType model, and CertificateForm form class defined as needed.

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'csv'}
def allowed_image_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}