from flask import Flask, render_template, url_for, redirect, request, jsonify,send_from_directory,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os
import db_classes
from certificate_models import CertificateEvent, EventType, CertificateForm
import uuid
import csv
from io import StringIO








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

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# old uri 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# new uri
app.config['SQLALCHEMY_DATABASE_URI'] =\
    f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'
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


# class users(db.Model, UserMixin):
#     # this variable(id) we cant change the name to (user_id) because it will conflict with UserMixin
#     id = db.Column(db.Integer, primary_key=True, unique=True)
#     user_name = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(80), nullable=False)
    


# class RegisterForm(FlaskForm):
#     user_name = StringField(validators=[
#                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "user_name"})
    
#     id = StringField(validators=[
#                            InputRequired()], render_kw={"placeholder": "user_id"})

#     password = PasswordField(validators=[
#                              InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

#     submit = SubmitField('Register')

#     def validate_user_name(self, user_name):
#         existing_user_user_name = users.query.filter_by(
#             user_name=user_name.data).first()
#         if existing_user_user_name:
#             raise ValidationError(
#                 'That user_name already exists. Please choose a different one.')
#     def validate_id(self, id):
#         existing_user_id = users.query.filter_by(id=id.data).first()
#         if existing_user_id:
#             raise ValidationError('chose different ID')


# class LoginForm(FlaskForm):
#     user_name = StringField(validators=[
#                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "user_name"})

#     password = PasswordField(validators=[
#                              InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

#     submit = SubmitField('Login')


# Global variable to store existing event types
existing_event_types = []
# Existing route


@app.route('/')
def home():
    return render_template('login_register.html')

# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = db_classes.LoginForm()
    if form.validate_on_submit():
        user = db_classes.users.query.filter_by(user_name=form.user_name.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('index.html')

# New route for Manage Event Types


@app.route('/manage_event_types', methods=['GET', 'POST'])
def manage_event_types():
    if request.method == 'POST':
        new_type = request.form.get('newTypeName')
        if new_type:
            existing_event_types.append(new_type)

    return render_template('manage_event_types.html', existing_event_types=existing_event_types)

# New route to handle updates from the frontend

@app.route('/update_event_types', methods=['POST'])
def update_event_types():
    action = request.form.get('action')
    type_name = request.form.get('typeName')

    if action == 'add':
        existing_event_types.append(type_name)
        return jsonify({'message': f'The type "{type_name}" has been added.'})
    elif action == 'delete':
        existing_event_types.remove(type_name)
        return jsonify({'message': f'The type "{type_name}" has been deleted.'})


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
    message = ""  # Empty message by default

    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            # Read the file into a StringIO object for parsing as CSV
            file_stream = StringIO(file.read().decode('utf-8-sig'), newline=None)
            csv_reader = csv.DictReader(file_stream)  # Use DictReader to read the CSV into a dictionary

            # Check if CSV has all required headers
            required_headers = {'name', 'email', 'event_name', 'event_date', 'event_type', 'certificate_hash',
                                'date_issued'}
            if not required_headers.issubset(set(csv_reader.fieldnames)):
                message = 'The CSV file does not have the required headers.'
            else:
                # The CSV has the required headers, so save the file and the event
                file.seek(0)  # Seek back to the start of the file
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Create a new CertificateEvent instance with the file path
                new_certificate_event = CertificateEvent(
                    certificate_event_id=str(uuid.uuid4()),
                    certificate_title=form.certificate_title.data,
                    event_type_id=form.event_type.data,
                    presenter_name=form.presenter_name.data,
                    secret_phrase=form.secret_phrase.data,
                    event_date=form.date.data,
                    certificate_description=form.certificate_description.data,
                    file_path=file_path  # Save the path to the file
                )

                # Add the new event to the session and commit it to the database
                db.session.add(new_certificate_event)
                db.session.commit()

                return redirect(url_for('dashboard'))  # Redirect to the dashboard after successful upload

        else:
            message = 'Please upload a CSV file.'

    # If it's a GET request or the form is not valid, render the page with the form
    return render_template('add_certificate.html', form=form, message=message)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'csv'}

@app.route('/settings')
def settings():
    # Your code here
    return render_template('settings.html')




# register route
@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = db_classes.RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = db_classes.users(user_name=form.user_name.data, password=hashed_password, user_role= form.user_role.data, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# route to show certificate
@app.route('/certificates', methods=['GET'])
@login_required
def certificates():
    # Fetch the latest 3 certificates and all certificates from the database
    latest_certificates = db_classes.addCertificate.query.limit(3).all()
    all_certificates = db_classes.addCertificate.query.all()

    # Render the 'certificates.html' template with the certificate data
    return render_template('certificates.html', latest_certificates=latest_certificates, all_certificates=all_certificates)

@app.route('/load_all_certificates', methods=['GET'])
@login_required
def load_all_certificates():
    # Fetch all certificates from the database
    all_certificates = db_classes.addCertificate.query.all()

    # Prepare a list of certificate details for JSON response
    certificates_list = [
        {
            'certificate_title': certificate.certificate_title,
            'presenter_name': certificate.presenter_name,
            'certificate_event_id': certificate.certificate_event_id,
            'secret_key': certificate.secret_key,
            'event_date': certificate.event_date,
            'certificate_description': certificate.description,
            'file_path': certificate.file_path
        }
        for certificate in all_certificates
    ]

    # Return the list of certificate details as a JSON response
    return jsonify(certificates_list)

@app.route('/certificate_details/<certificate_event_id>', methods=['GET'])
@login_required
def certificate_details(certificate_event_id):
    # Fetch the details of a specific certificate by its event ID
    certificate = db_classes.addCertificate.query.get_or_404(certificate_event_id)

    # Render the 'certificate_details.html' template with the specific certificate details
    return render_template('certificate_details.html', certificate=certificate)

# Add routes for other actions (delete, generate, download, send) as needed


@app.route("/create_new_template", methods=['GET',"POST"])
def newtemp():
    form=db_classes.NewTemplates()
    if form.validate_on_submit():
        file = form.template_image.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        new_template = db_classes.template(template_name=form.template_name.data,template_image=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        db.session.add(new_template)
        db.session.commit()

        return "You Add New Templates Successfully."

    return render_template('create_new_template.html',form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/Select_template", methods=['GET',"POST"])
def selectTemp():
    templates=db_classes.template.query.all()
    return render_template("select_template.html",templates=templates)

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

