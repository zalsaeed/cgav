# Standard Library Imports
import os
from io import StringIO
import uuid
import csv

# Related Third Party Imports
from flask import Flask, render_template, url_for, redirect, request, jsonify, send_from_directory, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import update
from sqlalchemy.orm.session import object_session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Local App/Library Specific Imports
import add_certificate_function
import db_classes
import setting_functions
import show_certificate_function
import delete_confirmation_function
import load_more_certificates_function
import certificate_details_function
import download_certificate_function
import template_functions
import generate_functions
import db_connection
from db_classes import CertificateEvent, EventType, CertificateForm, Template

# Load environment variables from the .env file
load_dotenv()

# to access the data in .env file
# HOSTNAME = os.environ.get('HOSTNAME')
# DB_PORT = os.environ.get('DB_PORT')
# MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
# MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
# MYSQL_USER = os.environ.get('MYSQL_USER')
# MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
# SCHEMA = os.environ.get("SCHEMA")

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt
# old uri 
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# new uri
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'

# TimeoutError Database need to change
# app.config['SQLALCHEMY_POOL_SIZE'] = 500 # you allow up to 100 concurrent connections to the database.
# app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600 # 3600 seconds (1 hour) means that connections will be recycled after being open for 1 hour.

# app.config['SECRET_KEY'] = 'thisisasecretkey'
# app.config['UPLOAD_FOLDER']='../certificate-templates'


# # Mail Server Configuration
# app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
# app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
# app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() == 'true'
# app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL').lower() == 'true'
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
# app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db_classes.users.query.get(int(user_id))



@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/sample')
def sample():
    return render_template('samples.html')

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
@login_required
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



#app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'certificate-templates')

# Ensure the upload_folder exists
#os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route('/add_certificate', methods=['GET', 'POST'])
@login_required
def add_certificate():
    return add_certificate_function.add_certificate()


# Ensure you have your CertificateEvent model, EventType model, and CertificateForm form class defined as needed.

#def allowed_file(filename):
#    return '.' in filename and \
#        filename.rsplit('.', 1)[1].lower() in {'csv'}
#def allowed_image_file(filename):
#    return '.' in filename and \
#        filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


@app.route('/settings')
@login_required
def settings():
    return setting_functions.settings()
#     user = current_user
#     # Pass the user's first and last name to the template
#     return render_template('settings.html', first_name=user.Fname, last_name=user.Lname)






@app.route('/settings/change_name', methods=['GET', 'POST'])
@login_required
def change_name():
    return setting_functions.change_name()
#     form = db_classes.ChangeNameForm()
#     if form.validate_on_submit():
#         current_user.Fname = form.name.data.split()[0]  # assuming the first name is the first word
#         current_user.Lname = ' '.join(form.name.data.split()[1:])  # rest of the parts are considered as the last name
#         db.session.commit()
#         flash('Your name has been updated.', 'success')
#         return redirect(url_for('settings'))
#     return render_template('change_name.html', form=form)

 

@app.route('/settings/change_email', methods=['GET', 'POST'])
@login_required
def change_email():
    return setting_functions.change_email()
#     form = db_classes.ChangeEmailForm()
#     if form.validate_on_submit():
#         current_user.email = form.email.data
#         db.session.commit()
#         flash('Your email has been updated.', 'success')
#         return redirect(url_for('settings'))
#     return render_template('change_email.html', form=form)



    # Route and form for changing password
@app.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    return setting_functions.change_password()
#     form = db_classes.ChangePasswordForm()
#     message = None  # Initialize the message variable

#     if form.validate_on_submit():
#         if bcrypt.check_password_hash(current_user.password, form.old_password.data):
#             if form.new_password.data == form.confirm_new_password.data:
#                 # Set new password with bcrypt and decode it to string
#                 hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
#                 current_user.password = hashed_password
#                 db.session.commit()
#                 message = 'Your password has been updated successfully.'
#             else:
#                 message = 'New password and confirmation do not match.'
#         else:
#             message = 'Incorrect old password.'

#     # Pass the message to the template. If the message is None, nothing will be displayed.
#     return render_template('change_password.html', form=form, message=message)


@app.route('/get_user_info')
@login_required
def get_user_info():
    user_info = {
        'Fname': current_user.Fname,
        'Lname': current_user.Lname,
        'email': current_user.email
    }
    return jsonify(user_info)

# class Certificate(db.Model):
#     __tablename__ = 'Certificate'
#     hash = db.Column(db.String(25), primary_key=True)
#     recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
#     certificate_event_id = db.Column(db.String(255), db.ForeignKey('addCertificate.certificate_event_id'))

#class VerifyCertificateForm(FlaskForm):
#    certificate_hash = StringField('Certificate Code', validators=[DataRequired()])
#    submit = SubmitField('Verify')


@app.route('/api/verify_certificate/<secret_key>', methods=['GET'])
def verify_certificate_api(secret_key):
    certificate = CertificateEvent.query.filter_by(secret_key=secret_key).first()
    if certificate:
        # Use a fake recipient name as a placeholder
        fake_recipient_name = "سمية بنت ناصر الناصر"

        return jsonify({
            'valid': True,
            'certificate_details': {
                'recipient_name': fake_recipient_name,  # Static placeholder value
                'certificate_title': certificate.certificate_title,
                'presenter_name': certificate.presenter_name,
                'event_date': certificate.event_date.strftime("%Y-%m-%d") if certificate.event_date else None,
                # Include any other fields you want to return
            }
        }), 200
    else:
        return jsonify({'valid': False, 'error': 'Certificate is invalid or not found.'}), 404






# route to show certificate
@app.route('/certificates', methods=['GET'])
@login_required
def certificates():
    return show_certificate_function.certificates()


@app.route('/load_more_certificates', methods=['GET'])
@login_required
def load_more_certificates():
    return load_more_certificates_function.load_more_certificates()


@app.route('/certificate_details/<certificate_event_id>', methods=['GET'])
@login_required
def certificate_details(certificate_event_id):
    return certificate_details_function.certificate_details(certificate_event_id)

# Add routes for other actions ( generate, download, send) as needed

# Route for the delete confirmation page (from database)
@app.route('/delete_confirmation/<certificate_event_id>', methods=['GET', 'POST'])
@login_required
def delete_confirmation(certificate_event_id):
    return delete_confirmation_function.delete_confirmation(certificate_event_id) 

@app.route('/download_latest_event_certificates', methods=['GET'])
def download_latest_event_certificates():
    return download_certificate_function.download_certificates()

@app.route("/create_new_template", methods=['GET', "POST"])
@login_required
def newtemp():
    return template_functions.newtemp()



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/Select_template/<temp_id>',methods=['GET',"POST"])
@login_required
def template(temp_id):
    return template_functions.template(temp_id)



@app.route("/Select_template", methods=['GET',"POST"])
@login_required
def selectTemp():
    return template_functions.selectTemp()

@app.route('/fetch_latest_pdf', methods=['GET'])
def fetch_latest_pdf():
    return generate_functions.fetch_latest_pdf()



@app.route('/run_main_script/<temp_id>', methods=['POST'])
def run_main_script(temp_id):
    return generate_functions.run_main_script(temp_id)


@app.route('/generate_certificate/<certificate_event_id>', methods=['POST'])
@login_required
def generate_certificate(certificate_event_id):
    return generate_functions.generate_certificate(certificate_event_id)

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
                db_connection.mail.send(msg)
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

