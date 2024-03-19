from flask import request, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from io import StringIO
import csv
import os
import uuid

from db_classes import CertificateForm, EventType, Template, CertificateEvent
from db_connection import db, app
import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'certificate-templates')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



def add_certificate():
    if request.method == 'POST':
        language = request.form.get('language')
        if language == 'arabic':
            return redirect('/ar_form')
        elif language == 'english':
            return redirect('/en_form')
        elif language == 'arabic_english':
            return redirect('/aren_form')
    return render_template('add_certificate.html')


def ar_form():
    form = CertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    if request.method == 'POST':
        if not form.validate_on_submit():  # Validate the form
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(f"{fieldName}: {err}")
            return render_template('ar_form.html', form=form, message=message, show_second_signatory=show_second_signatory)

        # Process form submission
        selected_template_id = form.template_choice.data
        selected_template = Template.query.filter_by(template_id=selected_template_id).first()
        template_path = selected_template.template_image

        file = form.file.data
        if file and allowed_file(file.filename):
            file_stream = StringIO(file.read().decode('utf-8-sig'), newline=None)
            csv_reader = csv.DictReader(file_stream)
            required_headers = {'arfirst_name', 'armiddle_name', 'arlast_name', 'ar_email', 'ar_phone', 'ar_gender'}

            if not required_headers.issubset(set(csv_reader.fieldnames)):
                message = 'The CSV file does not have the required headers.'
                return render_template('ar_form.html', form=form, message=message,
                                       show_second_signatory=show_second_signatory)

            file.seek(0)
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            signature_image_1 = form.signature_image_1.data
            signature_image_2 = form.signature_image_2.data
            signatures_folder = 'signatures'

            image_path_1 = None
            image_path_2 = None

            if signature_image_1 and allowed_image_file(signature_image_1.filename):
                filename_1 = secure_filename(signature_image_1.filename)
                image_path_1 = os.path.join(signatures_folder, filename_1)
                signature_image_1.save(image_path_1)

            if signature_image_2 and allowed_image_file(signature_image_2.filename):
                filename_2 = secure_filename(signature_image_2.filename)
                image_path_2 = os.path.join(signatures_folder, filename_2)
                signature_image_2.save(image_path_2)

            # Process signatures if needed

            new_certificate_event = CertificateEvent(
                created_by=current_user.id,
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
                First_Signatory_Path=image_path_1,  # Defined variable
                Second_Signatory_Name=form.signatory_name_2.data,
                Second_Signatory_Position=form.signatory_position_2.data,
                Second_Signatory_Path=image_path_2,  # Defined variable
                greeting_female=form.greeting_female.data,
                greeting_male=form.greeting_male.data,
                intro=form.intro.data,
                male_recipient_title=form.male_recipient_title.data,
                female_recipient_title=form.female_recipient_title.data,
            )

            try:
                db.session.add(new_certificate_event)
                db.session.commit()
                flash('Certificate event successfully added.')
                return redirect(url_for('certificates'))  # Fixed redirect here
            except Exception as e:
                db.session.rollback()
                message = f"Failed to add certificate: {str(e)}"
        else:
            message = 'Please upload a CSV file.'

    return render_template(
        'ar_form.html',  # Change the template name if necessary
        form=form,
        message=message,
        show_second_signatory=show_second_signatory
    )







def en_form():
    form = CertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    if request.method == 'POST':
        if not form.validate_on_submit():  # Validate the form
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(f"{fieldName}: {err}")
            return render_template('en_form.html', form=form, message=message, show_second_signatory=show_second_signatory)

        # Process form submission
        selected_template_id = form.template_choice.data
        selected_template = Template.query.filter_by(template_id=selected_template_id).first()
        template_path = selected_template.template_image

        file = form.file.data
        if file and allowed_file(file.filename):
            file_stream = StringIO(file.read().decode('utf-8-sig'), newline=None)
            csv_reader = csv.DictReader(file_stream)
            required_headers = {'first_name', 'middle_name', 'last_name', 'email', 'phone', 'gender'}

            if not required_headers.issubset(set(csv_reader.fieldnames)):
                message = 'The CSV file does not have the required headers.'
                return render_template('en_form.html', form=form, message=message,
                                       show_second_signatory=show_second_signatory)

            file.seek(0)
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            signature_image_1 = form.signature_image_1.data
            signature_image_2 = form.signature_image_2.data
            signatures_folder = 'signatures'

            image_path_1 = None
            image_path_2 = None

            if signature_image_1 and allowed_image_file(signature_image_1.filename):
                filename_1 = secure_filename(signature_image_1.filename)
                image_path_1 = os.path.join(signatures_folder, filename_1)
                signature_image_1.save(image_path_1)

            if signature_image_2 and allowed_image_file(signature_image_2.filename):
                filename_2 = secure_filename(signature_image_2.filename)
                image_path_2 = os.path.join(signatures_folder, filename_2)
                signature_image_2.save(image_path_2)

            # Process signatures if needed

            new_certificate_event = CertificateEvent(
                created_by=current_user.id,
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
                First_Signatory_Path=image_path_1,  # Defined variable
                Second_Signatory_Name=form.signatory_name_2.data,
                Second_Signatory_Position=form.signatory_position_2.data,
                Second_Signatory_Path=image_path_2,  # Defined variable
                greeting_female=form.greeting_female.data,
                greeting_male=form.greeting_male.data,
                intro=form.intro.data,
                male_recipient_title=form.male_recipient_title.data,
                female_recipient_title=form.female_recipient_title.data,
            )

            try:
                db.session.add(new_certificate_event)
                db.session.commit()
                flash('Certificate event successfully added.')
                return redirect(url_for('certificates'))  # Fixed redirect here
            except Exception as e:
                db.session.rollback()
                message = f"Failed to add certificate: {str(e)}"
        else:
            message = 'Please upload a CSV file.'

    return render_template(
        'en_form.html',  # Change the template name if necessary
        form=form,
        message=message,
        show_second_signatory=show_second_signatory
    )



def aren_form():
    form = CertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    if form.validate_on_submit():
        selected_template_id = form.template_choice.data
        selected_template = Template.query.filter_by(template_id=selected_template_id).first()
        template_path = selected_template.template_image

        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the file for processing

            # Now, process the CSV file from the saved location
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                csv_reader = csv.DictReader(f)

                # Set of required headers
                required_headers = {
                    'first_name','middle_name','last_name','arfirst_name','armiddle_name','arlast_name','email','phone','gender'
                }

                # Check if all required headers are present in the CSV file
                if not required_headers.issubset(set(csv_reader.fieldnames)):
                    message = 'The CSV file does not have the required headers.'
                else:
                    # Reset file pointer to beginning
                    f.seek(0)

                    # Save the file again
                    file.save(file_path)

                    # Process signature images
                    signature_image_1 = form.signature_image_1.data
                    signature_image_2 = form.signature_image_2.data
                    signatures_folder = 'signatures'

                    # Save first signature image if provided
                    if signature_image_1 and allowed_image_file(signature_image_1.filename):
                        filename_1 = secure_filename(signature_image_1.filename)
                        image_path_1 = os.path.join(signatures_folder, filename_1)
                        signature_image_1.save(image_path_1)

                    # Initialize image_path_2 with None
                    image_path_2 = None

                    # Save second signature image if provided
                    if signature_image_2 and allowed_image_file(signature_image_2.filename):
                        filename_2 = secure_filename(signature_image_2.filename)
                        image_path_2 = os.path.join(signatures_folder, filename_2)
                        signature_image_2.save(image_path_2)

                    # Create a new CertificateEvent instance
                    new_certificate_event = CertificateEvent(
                        created_by=current_user.id,
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

                    try:
                        # Commit the new CertificateEvent to the database
                        db.session.add(new_certificate_event)
                        db.session.commit()
                        return redirect(url_for('certificates'))
                    except Exception as e:
                        db.session.rollback()
                        message = f"Failed to add certificate: {str(e)}"
        else:
            message = 'Please upload a CSV file.'

    return render_template(
        'aren_form.html',  # Change the template name if necessary
        form=form,
        message=message,
        show_second_signatory=show_second_signatory
    )






def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}
