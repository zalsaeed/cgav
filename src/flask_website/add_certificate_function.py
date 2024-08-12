from flask import request, redirect, url_for, render_template, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from io import StringIO
import csv
import os
import uuid
import logging

            
from db_classes import CertificateForm, EventType, Template, CertificateEvent,EnglishCertificateForm
from db_connection import db, app
import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

    templates = Template.query.filter_by(is_active=True).all()
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

            logger.debug("Fieldnames from CSV: %s", csv_reader.fieldnames)

            required_headers = {'arfirst_name', 'armiddle_name', 'arlast_name', 'email', 'phone', 'gender'}

            if not required_headers.issubset(set(csv_reader.fieldnames)):
                message = 'The CSV file does not have the required headers.'
                logger.debug("Missing headers in CSV file: %s", required_headers - set(csv_reader.fieldnames))

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
                template_id =form.template_choice.data,
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

                form_type = 'Arabic',
            )

            try:
                db.session.add(new_certificate_event)
                db.session.commit()

                # Retrieve the ID of the newly added certificate event
                certificate_event_id = new_certificate_event.certificate_event_id

                # Construct the URL for the event details page
                event_details_url = url_for('certificate_details', certificate_event_id=certificate_event_id)

                flash('Certificate event successfully added.')
                # Redirect to the event details page
                return redirect(event_details_url)
            except Exception as e:
                db.session.rollback()
                message = f"Failed to add certificate: {str(e)}"

    return render_template(
        'ar_form.html',  # Change the template name if necessary
        form=form,
        message=message,
        show_second_signatory=show_second_signatory
    )







def en_form():
    form = CertificateForm()
    En_form = EnglishCertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.filter_by(is_active=True).all()
    form.template_choice.choices = [(str(t.template_id), t.template_name) for t in templates]

    if request.method == 'POST':

        # Validate the English form
        if not En_form.validate_on_submit():  
            for fieldName, errorMessages in En_form.errors.items():
                for err in errorMessages:
                    flash(f"{fieldName}: {err}")
            return render_template('en_form.html', form=form,En_form=En_form, message=message, show_second_signatory=show_second_signatory)

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
                return render_template('en_form.html', form=form, En_form=En_form,message=message,
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

            # Update variables to retrieve English form data
            certificate_description_female_en = En_form.certificate_description_female_en.data
            certificate_description_male_en = En_form.certificate_description_male_en.data
            greeting_female_en = En_form.greeting_female_en.data
            greeting_male_en = En_form.greeting_male_en.data
            intro_en = En_form.intro_en.data
            male_recipient_title_en = En_form.male_recipient_title_en.data
            female_recipient_title_en = En_form.female_recipient_title_en.data
                
            new_certificate_event = CertificateEvent(
                created_by=current_user.id,
                certificate_title=form.certificate_title.data,
                event_type_id=form.event_type.data,
                template_path=template_path,
                template_id =form.template_choice.data,
                presenter_name=form.presenter_name.data,
                secret_phrase=form.secret_phrase.data,
                event_date=form.date.data,
                file_path=file_path,

                First_Signatory_Name=form.signatory_name_1.data,
                First_Signatory_Position=form.signatory_position_1.data,
                First_Signatory_Path=image_path_1,  # Defined variable
                Second_Signatory_Name=form.signatory_name_2.data,
                Second_Signatory_Position=form.signatory_position_2.data,
                Second_Signatory_Path=image_path_2,  # Defined variable

                certificate_description_female_en=certificate_description_female_en,
                certificate_description_male_en=certificate_description_male_en,
                greeting_female_en=greeting_female_en,
                greeting_male_en=greeting_male_en,
                intro_en=intro_en,
                male_recipient_title_en=male_recipient_title_en,
                female_recipient_title_en=female_recipient_title_en,

                form_type = 'English',
            )

            try:
                db.session.add(new_certificate_event)
                db.session.commit()

                # Retrieve the ID of the newly added certificate event
                certificate_event_id = new_certificate_event.certificate_event_id

                # Construct the URL for the event details page
                event_details_url = url_for('certificate_details', certificate_event_id=certificate_event_id)

                flash('Certificate event successfully added.')
                # Redirect to the event details page
                return redirect(event_details_url)
            except Exception as e:
                db.session.rollback()
                message = f"Failed to add certificate: {str(e)}"

    return render_template('en_form.html', form=form, En_form=En_form, message=message, show_second_signatory=show_second_signatory)




def aren_form():
    form = CertificateForm()
    En_form = EnglishCertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    active_event_types = EventType.query.filter_by(is_active=True).all()
    form.event_type.choices = [(str(event_type.event_type_id), event_type.event_type_name) for event_type in active_event_types]

    templates = Template.query.filter_by(is_active=True).all()
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
                #logger.debug("Headers in CSV file: %s", set(csv_reader.fieldnames))
                # Check if all required headers are present in the CSV file
                if not required_headers.issubset(set(csv_reader.fieldnames)):
                    message = 'The CSV file does not have the required headers.'
                else:
                    # I removed these lines because it cased csv file to be empty 
                    # # Reset file pointer to beginning
                    # f.seek(0)

                    # # Save the file again
                    # file.save(file_path)

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

           
                    # Variables for English form data
                    # Update variables to retrieve English form data
                    certificate_description_female_en = En_form.certificate_description_female_en.data
                    certificate_description_male_en = En_form.certificate_description_male_en.data
                    greeting_female_en = En_form.greeting_female_en.data
                    greeting_male_en = En_form.greeting_male_en.data
                    intro_en = En_form.intro_en.data
                    male_recipient_title_en = En_form.male_recipient_title_en.data
                    female_recipient_title_en = En_form.female_recipient_title_en.data


                    # Variables for Arabic form data
                    certificate_description_female_ar = form.certificate_description_female.data
                    certificate_description_male_ar = form.certificate_description_male.data
                    greeting_female_ar = form.greeting_female.data
                    greeting_male_ar = form.greeting_male.data
                    intro_ar = form.intro.data
                    male_recipient_title_ar = form.male_recipient_title.data
                    female_recipient_title_ar = form.female_recipient_title.data

                    # Create a new CertificateEvent instance  
                    new_certificate_event = CertificateEvent(
                        certificate_description_female=certificate_description_female_ar,
                        certificate_description_male=certificate_description_male_ar,
                        greeting_female=greeting_female_ar,
                        greeting_male=greeting_male_ar,
                        intro=intro_ar,
                        male_recipient_title=male_recipient_title_ar,
                        female_recipient_title=female_recipient_title_ar,
                        created_by=current_user.id,

                        certificate_title=form.certificate_title.data,
                        event_type_id=form.event_type.data,
                        template_path=template_path,
                        template_id =form.template_choice.data,
                        presenter_name=form.presenter_name.data,
                        secret_phrase=form.secret_phrase.data,
                        event_date=form.date.data,
                        file_path=file_path,
                        First_Signatory_Name=form.signatory_name_1.data,
                        First_Signatory_Position=form.signatory_position_1.data,
                        First_Signatory_Path=image_path_1,  
                        Second_Signatory_Name=form.signatory_name_2.data,
                        Second_Signatory_Position=form.signatory_position_2.data,
                        Second_Signatory_Path=image_path_2,  
                    
                        certificate_description_female_en=certificate_description_female_en,
                        certificate_description_male_en=certificate_description_male_en,
                        greeting_female_en=greeting_female_en,
                        greeting_male_en=greeting_male_en,
                        intro_en=intro_en,
                        male_recipient_title_en=male_recipient_title_en,
                        female_recipient_title_en=female_recipient_title_en,

                        form_type = 'Arabic_English',
    
                    )
                    # Log the current user
                    logger.debug("Certificate event added by user ID: %s", current_user.id)

                    try:
                        # Add Arabic CertificateEvent instance to the database
                        db.session.add(new_certificate_event)
                        db.session.commit()

                        # Retrieve the ID of the newly added certificate event
                        certificate_event_id = new_certificate_event.certificate_event_id

                        # Construct the URL for the event details page
                        event_details_url = url_for('certificate_details', certificate_event_id=certificate_event_id)

                        flash('Certificate events successfully added.')

                        # Redirect to the event details page 
                        return redirect(event_details_url)
                    except Exception as e:
                        db.session.rollback()
                        message = f"Failed to add certificate: {str(e)}"


    return render_template(
        'aren_form.html',  # Change the template name if necessary
        form=form,En_form=En_form,
        message=message,
        show_second_signatory=show_second_signatory
    )






def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}
