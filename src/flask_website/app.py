import json
from flask import Flask, render_template, url_for, redirect, request, jsonify,send_from_directory,flash, session
import yaml
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError, EqualTo, Email
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os
from werkzeug.security import check_password_hash, generate_password_hash
import db_classes
# from db_classes import Template
from certificate_models import CertificateEvent, EventType, CertificateForm,CertificateCustomizations,Template
import uuid
import csv
from io import StringIO
from sqlalchemy import update
from sqlalchemy.orm.session import object_session
import subprocess

from werkzeug.utils import secure_filename

# Import for custom email handling
# from flask import render_template_string
# from jinja2 import Template
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# to access the data in .env file
HOSTNAME = os.environ.get('HOSTNAME')
DB_PORT = os.environ.get('DB_PORT')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
SCHEMA = os.environ.get("SCHEMA")

app = db_classes.app
db = db_classes.db
bcrypt = db_classes.bcrypt
# old uri 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# new uri
app.config['SQLALCHEMY_DATABASE_URI'] =\
    f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'

# TimeoutError Database need to change
app.config['SQLALCHEMY_POOL_SIZE'] = 500 # you allow up to 100 concurrent connections to the database.
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600 # 3600 seconds (1 hour) means that connections will be recycled after being open for 1 hour.

app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER']='../certificate-templates'


# Mail Server Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db_classes.users.query.get(int(user_id))



@app.route('/')
def home():
    return redirect(url_for('login'))

# register route
@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = db_classes.RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = db_classes.users(password=hashed_password, user_role= form.user_role.data, email=form.email.data, Fname=form.Fname.data, Lname=form.Lname.data)
        db.session.add(new_user)
        db.session.commit()
        flash('success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = db_classes.LoginForm()
    if form.validate_on_submit():
        user = db_classes.users.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('certificates'))
    return render_template('login.html', form=form)


# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     return render_template('index.html')

#Admin route
@app.route('/admin')
@login_required
def admin():
    users_list = db_classes.users.query.all()
    user_role = current_user.user_role
    if user_role == 1:
        return render_template('admin.html',users_list=users_list)
    else:
        flash('Access denied')
        return redirect(url_for('certificates'))
    
#update user
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = db_classes.UpdateForm()
    user_to_edit = db_classes.users.query.get(id)
    existing_email = db_classes.users.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit():
        if form.email.data == user_to_edit.email:
            email_to_save = user_to_edit.email
        elif existing_email:
            flash('email already exist')
            return redirect(url_for('update_user',id=user_to_edit.id))
        else:
            email_to_save = form.email.data


        if form.password.data == user_to_edit.password:
            password_to_save = form.password.data
        else:
            password_to_save = bcrypt.generate_password_hash(form.password.data)
        user_to_edit = update(db_classes.users).where(db_classes.users.id == id).values(user_role = form.user_role.data, email = email_to_save, Fname = form.Fname.data, password = password_to_save)
        db.session.execute(user_to_edit)
        db.session.commit()
        flash('success')
        return redirect(url_for('settings'))
    else:
        return render_template('update.html',form=form,user_to_edit=user_to_edit)
    
#delete user
@app.route('/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.id == id :
        flash('you are currently using this user')
        return redirect(url_for('settings'))
    else:

        user_to_delete = db_classes.users.query.get(id)
        uname = user_to_delete.Fname
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'you deleted {uname} successfuly')
        return redirect(url_for('settings'))
        


# New route for Manage Event Types
@app.route('/manage_event_types', methods=['GET', 'POST'])
def manage_event_types():
    if request.method == 'POST':
        new_type = request.form.get('newTypeName')
        if new_type:
            # Insert the new event type into the database
            new_event_type = EventType(event_type_name=new_type, is_active=True)
            db.session.add(new_event_type)
            db.session.commit()

    # Fetch existing event types from the database
    event_types = EventType.query.filter_by(is_active=True)
    print("---event_types--------",event_types)
    return render_template('manage_event_types.html', event_types=event_types)


@app.route('/update_event_types', methods=['POST'])
def update_event_types():
    data = request.get_json()
    action = data.get('action')
    type_name = data.get('typeName')
    
    if action == 'add':
        existing_event_type = EventType.query.filter_by(event_type_name=type_name, is_active=False).first()

        if existing_event_type:
            # Reactivate the existing event type using update statement
            stmt = update(EventType).where(EventType.event_type_name == type_name).values(is_active=True)
            db.session.execute(stmt)
            db.session.commit()
            return jsonify({'message': f'The type "{type_name}" has been reactivated.'})
        else:
            # Add a new event type
            new_event_type = EventType(event_type_name=type_name, is_active=True)
            db.session.add(new_event_type)
            db.session.commit()
            return jsonify({'message': f'The type "{type_name}" has been added.'})
    elif action == 'delete':
        try:
            stmt = update(EventType).where(EventType.event_type_name == type_name).values(is_active=False)
            db.session.execute(stmt)
            db.session.commit()
            return jsonify({'message': f'The type "{type_name}" has been deleted.'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'An error occurred while updating the database: {str(e)}'})

    # Default return statement
    return jsonify({'error': 'Invalid action provided.'})

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'certificate-templates')

# Ensure the upload_folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    form = CertificateForm()
    message = ""
    show_second_signatory = 'second_signatory' in request.args

    # Initialize form choices
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
                    certificate_event_id=str(uuid.uuid4()),
                    certificate_title=form.certificate_title.data,
                    event_type_id=form.event_type.data,
                    template_id =form.template_choice.data,
                    template_path=template_path,
                    presenter_name=form.presenter_name.data,
                    secret_phrase=form.secret_phrase.data,
                    event_date=form.date.data,
                    certificate_description_female=form.certificate_description_female.data,
                    certificate_description_male=form.certificate_description_male.data,
                    file_path=file_path,

                    First_Signatory_Path=image_path_1,

                    Second_Signatory_Path=image_path_2,

                    male_recipient_title_en=form.male_recipient_title_en.data,
                    male_recipient_title_ar=form.male_recipient_title_ar.data,
                    female_recipient_title_en=form.female_recipient_title_en.data,
                    female_recipient_title_ar=form.female_recipient_title_ar.data,
                    intro_en=form.intro_en.data,
                    intro_ar=form.intro_ar.data,
                    greeting_female_en=form.greeting_female_en.data,
                    greeting_female_ar=form.greeting_female_ar.data,
                    greeting_male_en=form.greeting_male_en.data,
                    greeting_male_ar=form.greeting_male_ar.data,
                    signatory_name_1_en=form.signatory_name_1_en.data,
                    signatory_name_1_ar=form.signatory_name_1_ar.data,
                    signatory_position_1_en=form.signatory_position_1_en.data,
                    signatory_position_1_ar=form.signatory_position_1_ar.data,
                    signatory_name_2_en=form.signatory_name_2_en.data,
                    signatory_name_2_ar=form.signatory_name_2_ar.data,
                    signatory_position_2_en=form.signatory_position_2_en.data,
                    signatory_position_2_ar=form.signatory_position_2_ar.data
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


@app.route('/settings')
@login_required
def settings():
    user = current_user
    # Pass the user's first and last name to the template
    return render_template('settings.html', first_name=user.Fname, last_name=user.Lname)






@app.route('/settings/change_name', methods=['GET', 'POST'])
@login_required
def change_name():
    form = db_classes.ChangeNameForm()
    if form.validate_on_submit():
        current_user.Fname = form.name.data.split()[0]  # assuming the first name is the first word
        current_user.Lname = ' '.join(form.name.data.split()[1:])  # rest of the parts are considered as the last name
        db.session.commit()
        flash('Your name has been updated.', 'success')
        return redirect(url_for('settings'))
    return render_template('change_name.html', form=form)

 

@app.route('/settings/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = db_classes.ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Your email has been updated.', 'success')
        return redirect(url_for('settings'))
    return render_template('change_email.html', form=form)



    # Route and form for changing password
@app.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = db_classes.ChangePasswordForm()
    message = None  # Initialize the message variable

    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            if form.new_password.data == form.confirm_new_password.data:
                # Set new password with bcrypt and decode it to string
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                current_user.password = hashed_password
                db.session.commit()
                message = 'Your password has been updated successfully.'
            else:
                message = 'New password and confirmation do not match.'
        else:
            message = 'Incorrect old password.'

    # Pass the message to the template. If the message is None, nothing will be displayed.
    return render_template('change_password.html', form=form, message=message)


@app.route('/get_user_info')
@login_required
def get_user_info():
    user_info = {
        'Fname': current_user.Fname,
        'Lname': current_user.Lname,
        'email': current_user.email
    }
    return jsonify(user_info)

class Certificate(db.Model):
    __tablename__ = 'Certificate'
    hash = db.Column(db.String(25), primary_key=True)
    recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
    certificate_event_id = db.Column(db.String(255), db.ForeignKey('addCertificate.certificate_event_id'))

class VerifyCertificateForm(FlaskForm):
    certificate_hash = StringField('Certificate Code', validators=[DataRequired()])
    submit = SubmitField('Verify')


@app.route('/api/verify_certificate', methods=['POST'])
def verify_certificate_api():
    data = request.get_json()

    certificate_hash = data.get('certificate_hash')
    if not certificate_hash:
        return jsonify({'error': 'Missing certificate hash'}), 400

    certificate = Certificate.query.filter_by(hash=certificate_hash).first()
    if certificate:
        return jsonify({
            'message': 'Certificate is valid.',
            'certificate_details': {
                'recipient_id': certificate.recipient_id,
                'certificate_event_id': certificate.certificate_event_id
            }
        }), 200
    else:
        return jsonify({'error': 'Certificate is invalid or not found.'}), 404




# route to show certificate
@app.route('/certificates', methods=['GET'])
@login_required
def certificates():
    # Fetch the latest 3 certificates and all certificates from the database
    latest_certificates = CertificateEvent.query.limit(3).all()
    all_certificates = CertificateEvent.query.all()

    # Render the 'certificates.html' template with the certificate data
    return render_template('certificates.html', latest_certificates=latest_certificates, all_certificates=all_certificates)


@app.route('/load_more_certificates', methods=['GET'])
@login_required
def load_more_certificates():
    try:
        # Get the number of certificates to load and the excluded IDs from the query parameters
        loaded_count = int(request.args.get('loaded_count', 0))
        exclude_ids = request.args.get('exclude_ids', '').split(',')

        # Fetch additional certificates from the database, excluding the ones already loaded
        additional_certificates = CertificateEvent.query \
            .filter(CertificateEvent.certificate_event_id.notin_(exclude_ids)) \
            .offset(loaded_count) \
            .limit(3) \
            .all()

        # Prepare a list of additional certificate details for JSON response
        additional_certificates_list = [
            {
                'certificate_title': certificate.certificate_title,
                'presenter_name': certificate.presenter_name,
                'certificate_event_id': certificate.certificate_event_id,
                'event_date': certificate.event_date.strftime('%Y-%m-%d'),
                'certificate_description_female': certificate.certificate_description_female,
                'file_path': certificate.file_path if hasattr(certificate, 'file_path') else None
            }
            for certificate in additional_certificates
        ]

        # Return the list of additional certificate details as a JSON response
        return jsonify(additional_certificates_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/certificate_details/<certificate_event_id>', methods=['GET'])
@login_required
def certificate_details(certificate_event_id):
    # Fetch the details of a specific certificate by its event ID
    certificate = CertificateEvent.query.get_or_404(certificate_event_id)

    # Render the 'certificate_details.html' template with the specific certificate details
    return render_template('certificate_details.html', certificate=certificate)

# Add routes for other actions ( generate, download, send) as needed

# Route for the delete confirmation page (from database)
@app.route('/delete_confirmation/<certificate_event_id>', methods=['GET', 'POST'])
@login_required
def delete_confirmation(certificate_event_id):
    certificate = CertificateEvent.query.get_or_404(certificate_event_id)

    # Check if the certificate is already attached to a session
    existing_session = object_session(certificate)

    if existing_session:
        existing_session.expunge(certificate)

    if request.method == 'POST':
        try:
            # Verify the event name for confirmation
            event_name = request.json.get('event_name', '')

            if event_name == certificate.certificate_title:
                # Delete the certificate
                db.session.delete(certificate)
                db.session.commit()

                # Send email notification
                send_delete_confirmation_email(certificate)

                # Provide a success response
                return jsonify({'success': True}), 200  # Return 200 OK status

            else:
                # Provide an error response (incorrect event name)
                return jsonify({'success': False, 'error': 'Incorrect event name'}), 400

        except Exception as e:
            # Provide an error response (server error)
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('delete_confirmation.html', certificate=certificate)

# Function to send email notification
def send_delete_confirmation_email(certificate):
    recipient_email = app.config['MAIL_USERNAME']  # Assuming recipient_email is a string or list

    if isinstance(recipient_email, str):
        recipient_email = [recipient_email]  # Convert the string to a list with a single element

    # Extract information from the certificate object
    certificate_title = certificate.certificate_title
    presenter_name = certificate.presenter_name
    # Add more fields as needed

    # Construct the email message
    subject = f'Certificate Deleted: {certificate_title}'
    body = f'Dear user,\n\nYour certificate "{certificate_title}" presented by {presenter_name} has been deleted successfully.'

    msg = Message(subject, recipients=recipient_email, sender=app.config['MAIL_USERNAME'])
    msg.body = body
    mail.send(msg)


@app.route("/create_new_template", methods=['GET', "POST"])
def newtemp():
    form = db_classes.NewTemplates()
    if form.validate_on_submit():
        file = form.template_image.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))


        new_template = Template(template_name=form.template_name.data,
                                           id = current_user.id,
                                           template_image=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        db.session.add(new_template)
        db.session.commit()

        flash('A new template has been added successfully.')
        return redirect(url_for('selectTemp'))  # It's better to use url_for() here

    return render_template('create_new_template.html', form=form)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/Select_template/<temp_id>',methods=['GET',"POST"])
def template(temp_id):
    # temp = db_classes.Template.query.filter_by(template_name=tempname).first()
    # tempid= temp.template_id if temp else None
    temp = Template.query.get_or_404(temp_id)
    form=db_classes.customizationForm()
    json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/FakeData.json')
    ar_json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/Arabicdata.json')
    custom_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/customization.json')

    # Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    with open(ar_json_file, 'r') as file:
        arData = json.load(file)
    
    with open(custom_file,'r') as file:
      customization_data = json.load(file)

    
    # if request.method == 'POST':
    if form.validate_on_submit():
        form_item = form.item.data  # Assuming form.item is a Flask-WTF field
        form_x = form.x.data
        form_y = form.y.data
        form_h = form.h.data
        form_w = form.w.data
        if form_item in customization_data:
            customization_data[form_item]['x'] = form_x
            customization_data[form_item]['y'] = form_y
            customization_data[form_item]['h'] = form_h
            customization_data[form_item]['w'] = form_w
        with open(custom_file, 'w') as file:
            json.dump(customization_data, file, indent=2)
        
        existing_customization = CertificateCustomizations.query.filter_by(
            id=current_user.id,
            template_id=temp.template_id).first()
        if existing_customization:
            # existing_customization.items_positions = customization_data
            # Reactivate the existing event type using update statement
            custom = update(CertificateCustomizations).where(CertificateCustomizations.template_id == temp.template_id and CertificateCustomizations.id == current_user.id).values(items_positions = customization_data)
            db.session.execute(custom)
            db.session.commit()
        else:
            new_customization = CertificateCustomizations(customization_id=str(uuid.uuid4()),
                                                          id = current_user.id,
                                                          template_id = temp.template_id,
                                                          items_positions = customization_data )
            # Add and commit the new record to the database
            db.session.add(new_customization)
            db.session.commit()

    return render_template('anotherAppearance.html', temp=temp,data=data,arData=arData,form=form)


@app.route("/Select_template", methods=['GET',"POST"])
def selectTemp():
     # Assuming the user ID is stored in the id field of the User model
    user_templates = Template.query.filter_by(id=current_user.id).all()
    return render_template("select_template.html", templates=user_templates)

########
@app.route('/preview_certificate', methods=['POST'])
def preview_certificate():
    try:
        # Get the selected template and other details from the request
        data = request.get_json()
        selected_template = data.get('selected_template')

        # Load default event data
        with open('events/sample-event.yaml', 'r') as file:
            event_data = yaml.safe_load(file)

        # Update the template path with the selected template
        event_data['certificate_background'] = selected_template

        # Run main.py with updated event data
        result = subprocess.run(['python', 'main.py', '--event_data', json.dumps(event_data)], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result.stderr})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

######
@app.route('/fetch_latest_pdf', methods=['GET'])
def fetch_latest_pdf():
    # The path to the output directory, considering the Docker container's file system
    search_directory = os.path.abspath("/root/src/flask_website/static/output")

    try:
        all_folders = [os.path.join(search_directory, d) for d in os.listdir(search_directory) if os.path.isdir(os.path.join(search_directory, d))]
        latest_folder = max(all_folders, key=os.path.getmtime)

        for file in os.listdir(latest_folder):
            if file.endswith(".pdf"):
                full_file_path = os.path.join(latest_folder, file)
                # Generate the relative path from the static folder
                relative_path = os.path.relpath(full_file_path, "/root/src/flask_website/static")
                pdf_url = url_for('static', filename=relative_path.replace(os.sep, '/'))

                return jsonify({'pdfUrl': pdf_url})

        return jsonify({'error': 'No PDF found'}), 404

    except Exception as e:
        app.logger.error(f"Error in fetch_latest_pdf: {str(e)}")
        return jsonify({'error': 'An internal error occurred'}), 500


@app.route('/run_main_script/<temp_id>', methods=['POST'])
def run_main_script(temp_id):
    try:
        customization = CertificateCustomizations.query.filter_by(template_id=temp_id).first()
        template= Template.query.filter_by(template_id=temp_id).first()
        event_data = {
            'template_path': template.template_image,
        }
        if customization:
            items_positions={
                "Certificate_Title":customization.items_positions["Certificate_Title"],
                "Intro": customization.items_positions["Intro"],
                "recipient_title":customization.items_positions["recipient_title"],
                "recipient_name":customization.items_positions["recipient_name"],
                "body":customization.items_positions["body"] ,
                "final_greeting":customization.items_positions["final_greeting"] ,
                "contact_info":customization.items_positions["contact_info"],
                "signature_1": customization.items_positions["signature_1"],
                "signature_2": customization.items_positions["signature_2"]}
        else:
            items_positions={}
        # Adjust the path according to your folder structure
        # script_path = os.path.join(os.getcwd(), 'main.py')
        result = subprocess.run(['python', 'main.py', '--event_data', json.dumps(event_data), '--items_positions', json.dumps(items_positions)], capture_output=True, text=True)
        return jsonify({'success': True, 'output': result.stdout})
    
    except subprocess.CalledProcessError as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/generate_certificate/<certificate_event_id>', methods=['POST'])
@login_required
def generate_certificate(certificate_event_id):
    try:
        certificate = CertificateEvent.query.get(certificate_event_id)
        customization = CertificateCustomizations.query.filter_by(template_id=certificate.template_id).first()
        if not certificate:
            return jsonify({'success': False, 'error': 'Certificate not found'}), 404

        event_data = {
            'certificate_event_id': str(certificate.certificate_event_id),
            'certificate_title': certificate.certificate_title,
            'event_type_id': certificate.event_type_id,
            'template_path': certificate.template_path,
            'presenter_name': certificate.presenter_name,
            'secret_phrase': certificate.secret_phrase,
            'event_date': certificate.event_date.strftime('%Y-%m-%d'),
            'certificate_description_female': certificate.certificate_description_female,
            'certificate_description_male': certificate.certificate_description_male,
            'file_path': certificate.file_path,
            'First_Signatory_Name': certificate.First_Signatory_Name,
            'First_Signatory_Position': certificate.First_Signatory_Position,
            'First_Signatory_Path': certificate.First_Signatory_Path,
            'Second_Signatory_Name': certificate.Second_Signatory_Name,
            'Second_Signatory_Position': certificate.Second_Signatory_Position,
            'Second_Signatory_Path': certificate.Second_Signatory_Path,
            'greeting_female': certificate.greeting_female,
            'greeting_male': certificate.greeting_male,
            'intro': certificate.intro,
            'male_recipient_title': certificate.male_recipient_title,
            'female_recipient_title': certificate.female_recipient_title,
            # ... add other fields as needed ...
        }

        if customization:
            items_positions={
                "Certificate_Title":customization.items_positions["Certificate_Title"],
                "Intro": customization.items_positions["Intro"],
                "recipient_title":customization.items_positions["recipient_title"],
                "recipient_name":customization.items_positions["recipient_name"],
                "body":customization.items_positions["body"] ,
                "final_greeting":customization.items_positions["final_greeting"] ,
                "contact_info":customization.items_positions["contact_info"],
                "signature_1": customization.items_positions["signature_1"],
                "signature_2": customization.items_positions["signature_2"]}
        else:
            items_positions={}
        result = subprocess.run(['python', 'main.py', '--event_data', json.dumps(event_data), '--items_positions', json.dumps(items_positions)], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': result.stderr})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/send_email', methods=['GET', 'POST'])
@login_required
def send_email():
    if request.method == 'POST':
        selected_emails = request.form.getlist('emails')

        # Get the custom email details from the form
        subject = request.form.get('subject')
        custom_content = request.form.get('custom-content')

        # Iterate over selected emails
        for email in selected_emails:
            # Find the PDF file for the user
            certificate_folder = os.path.join(os.path.dirname(__file__), 'sample-event')
            pdf_files = [f for f in os.listdir(certificate_folder) if f.startswith(f"{email}-") and f.endswith(".pdf")]

            if pdf_files:
                # Use the first PDF file found for the user
                certificate_filename = os.path.join(certificate_folder, pdf_files[0])

                # Construct the message
                msg = Message('Your Certificate', recipients=[email], sender='no-reply@example.com')

                # Use custom or default values
                if  subject and custom_content:
                    msg.subject = subject
                    msg.body = custom_content
                else:
                    msg.body = 'Dear User,\n\nPlease find attached your certificate.'

                # Attach the certificate to the email
                with app.open_resource(certificate_filename) as certificate:
                    msg.attach(email + '_certificate.pdf', 'application/pdf', certificate.read())

                # Send the email
                mail.send(msg)
            else:
                # No certificate file found for the user
                print(f"Certificate not found for {email}")

        # Check if custom values were used
        if subject and custom_content:
            flash("Custom emails sent successfully!", "success")
        else:
            flash("Default emails sent successfully!", "success")

    return render_template('send_email.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

