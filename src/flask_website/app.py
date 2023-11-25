from flask import Flask, render_template, url_for, redirect, request, jsonify,send_from_directory,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os
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
    return users.query.get(int(user_id))


class users(db.Model, UserMixin):
    # this variable(id) we cant change the name to (user_id) because it will conflict with UserMixin
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    


class RegisterForm(FlaskForm):
    user_name = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "user_name"})
    
    id = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "user_id"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_user_name(self, user_name):
        existing_user_user_name = users.query.filter_by(
            user_name=user_name.data).first()
        if existing_user_user_name:
            raise ValidationError(
                'That user_name already exists. Please choose a different one.')
    def validate_id(self, id):
        existing_user_id = users.query.filter_by(id=id.data).first()
        if existing_user_id:
            raise ValidationError('chose different ID')


class LoginForm(FlaskForm):
    user_name = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "user_name"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class NewTemplates(FlaskForm):
    templatesName= StringField('*Template Name', validators=[DataRequired(), Length(min=2, max=30)])
    templatesImage= FileField('*Upload Background', validators=[DataRequired()])
    submit= SubmitField('Add')

# Global variable to store existing event types
existing_event_types = []
# Global variable to store existing templates
templates=[]

# Existing route


@app.route('/')
def home():
    return render_template('login_register.html')

# login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(user_name=form.user_name.data).first()
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


@app.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    return render_template('add_certificate.html')

# register route
@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = users(user_name=form.user_name.data, password=hashed_password, id=form.id.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# New route to confirm delete from the database

@app.route('/delete_certificate', methods=['GET', 'POST'])
def delete_certificate():
    if request.method == 'POST':
        certificate_name = request.form.get('certificateName')

        certificate = Certificate.query.filter_by(name=certificate_name).first()

        # If certificate is found in the database
        if certificate:
            db.session.delete(certificate)
            db.session.commit()
            return redirect(url_for(
                'certificates_content_page'))  # Replace 'certificates_content_page' with the correct route name for certificates content page.

        else:
            # Return back to the same page with an error message
            return render_template('delete_certificate.html',
                                   error="Certificate name is incorrect. Please try again and make sure of the correct name.")

    return render_template('delete_certificate.html')

@app.route("/create_new_template", methods=['GET',"POST"])
def newtemp():
    form=NewTemplates()
    if form.validate_on_submit():
        file = form.templatesImage.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        template = {
            'name': form.templatesName.data,
            'image_path': os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        }
        templates.append(template)
        # For test only
        # print(templates)

        return "You Add New Templates Successfully."

    return render_template('create_new_template.html',form=form)


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

