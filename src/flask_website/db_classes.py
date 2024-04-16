# Standard Library Imports
from werkzeug.utils import secure_filename
import uuid

# Related Third Party Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField,SubmitField, IntegerField, TextAreaField,SelectField, DateField
from wtforms.validators import InputRequired, DataRequired, Length,ValidationError, EqualTo, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship

# Local App/Library Specific Imports
import db_connection


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt
# app = Flask(__name__)

# ================= Classes related to DataBase ===========================
class users(db.Model, UserMixin):
    # this variable(id) we cant change the name to (user_id) because it will conflict with UserMixin
    id = db.Column(db.Integer, primary_key=True, unique=True)
    Fname = db.Column(db.String(40), nullable=False)
    Lname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.Integer, nullable=True)

def generate_recipient_id():
    return str(uuid.uuid4())

class recipient(db.Model):
    __tablename__ = 'recipient'
    recipient_id = db.Column(db.String(255), primary_key=True, default=generate_recipient_id)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.String(5))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))

class instructor(db.Model):
    __tablename__ = 'instructor'
    instructor_id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.String(5))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))

class CertificateEvent(db.Model):
    __tablename__ = 'addCertificate'
    certificate_event_id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer)
    customization_id = db.Column(db.String(255))
    certificate_title = db.Column(db.String(255))
    event_type_id = db.Column(db.Integer, db.ForeignKey('Event_type.event_type_id'))  # Foreign key relationship
    template_path = db.Column(db.String(255))
    template_id = db.Column(db.Integer, db.ForeignKey('template.template_id'))
    event_type = relationship('EventType', backref='certificates')
    presenter_name = db.Column(db.String(255))  # New field
    secret_phrase = db.Column(db.String(255))  # New field
    event_date = db.Column(db.DateTime)  # New field
    certificate_description_female = db.Column(db.Text)
    certificate_description_male = db.Column(db.Text)
    file_path = db.Column(db.String(255))  # New field, to store file path if needed
    First_Signatory_Name = db.Column(db.String(255))
    First_Signatory_Position = db.Column(db.String(255))
    First_Signatory_Path = db.Column(db.String(255))
    Second_Signatory_Name = db.Column(db.String(255))
    Second_Signatory_Position = db.Column(db.String(255))
    Second_Signatory_Path = db.Column(db.String(255))
    greeting_female = db.Column(db.String(255))  # New field for female greeting
    greeting_male = db.Column(db.String(255))    
    intro = db.Column(db.String(255))
    male_recipient_title = db.Column(db.String(255))
    female_recipient_title = db.Column(db.String(255))
   
    #En columns 
    intro_en = db.Column(db.String(255))
    female_recipient_title_en = db.Column(db.String(255))
    male_recipient_title_en = db.Column(db.String(255))
    greeting_female_en = db.Column(db.String(255))
    greeting_male_en = db.Column(db.String(255))    
    certificate_description_female_en = db.Column(db.Text)
    certificate_description_male_en = db.Column(db.Text)
    #End En columns 
    
    downloaded = db.Column(db.Boolean, default=False)  # New field to indicate if the event was downloaded
    sended = db.Column(db.Boolean, default=False)  # New field to indicate if the event was sent
    generated_ = db.Column(db.Boolean, default=False)  # New field to indicate if the event was generated
    # secret_key = db.Column(db.String(255)) 
    # recipient_id = db.Column(db.String(255))
    
class Template(db.Model):
    __tablename__ = 'template'
    template_id = db.Column(db.Integer, primary_key=True, unique=True )
    id = db.Column(db.Integer)
    template_name = db.Column(db.String(30), nullable=False)
    template_image = db.Column(db.String(300), nullable=False)

class CertificateCustomizations(db.Model):
    __tablename__ = 'CertificateCustomizations'
    customization_id = db.Column(db.String(255), primary_key=True)
    template_id = db.Column(db.String(255))
    id = db.Column(db.Integer)
    items_positions = db.Column(db.JSON)
    # Add other customization fields as needed
    # ...


class EventType(db.Model):
    __tablename__ = 'Event_type'  
    event_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

class Certificate_table(db.Model):
    __tablename__ = 'Certificate_table'
    certificate_hash = db.Column(db.String(25), primary_key=True)
    recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
    certificate_event_id = db.Column(db.Integer, db.ForeignKey('addCertificate.certificate_event_id'))

# ======== Classes related to Flask Forms =================================================================
    
class RegisterForm(FlaskForm):
    Fname = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "first name"})
    Lname = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "last name"})
    
    email = StringField(validators=[
                           InputRequired(), Email("This field requires a valid email address")], render_kw={"placeholder": "email"})
    
    user_role = StringField(validators=[
                           ], render_kw={"placeholder": "user_role"})

    password = PasswordField(validators=[
                             InputRequired(),EqualTo('confirm_password','miss match'), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    confirm_password = PasswordField(validators=[
                             InputRequired()], render_kw={"placeholder": "confirm Password"})

    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_email = users.query.filter_by(
            email=email.data).first()
        if existing_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')
    def validate_id(self, id):
        existing_user_id = users.query.filter_by(id=id.data).first()
        if existing_user_id:
            
            raise ValidationError('chose different ID')
 
class LoginForm(FlaskForm):
    email = StringField(validators=[
                           InputRequired(), Email("This field requires a valid email address")], render_kw={"placeholder": "email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

#update user
class UpdateForm(FlaskForm):
    Fname = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "first name"})
    email = StringField(validators=[
                           InputRequired(), Email("This field requires a valid email address")], render_kw={"placeholder": "email"})
    password = StringField(validators=[
                             InputRequired()], render_kw={"placeholder": "Password"})
    
    user_role = StringField(validators=[
                           ], render_kw={"placeholder": "user_role"})

    submit = SubmitField('save')

class CertificateForm(FlaskForm):
    
    certificate_title = StringField('Event Title', validators=[DataRequired()])
    created_by = db.Column(db.Integer)
    presenter_name = StringField('Presenter Name', validators=[DataRequired()])
    secret_phrase = StringField('Secret Phrase', validators=[DataRequired()])
    template_choice = SelectField('Certificate Template', choices=[])
    greeting_female = StringField('Greeting for Females', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for her success"})
    greeting_male = StringField('Greeting for Males', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for his success"})
    event_type = SelectField('Event Type', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    certificate_description_female = TextAreaField('Event Description for Female', validators=[DataRequired()])
    certificate_description_male = TextAreaField('Event Description for Male', validators=[DataRequired()])
    intro = StringField('Intro', validators=[DataRequired()], render_kw={"placeholder": "The Computer College testifies that"})
    male_recipient_title = StringField('Male Recipient Title', validators=[DataRequired()], render_kw={"placeholder": "Trainee:(Male)"})
    female_recipient_title = StringField('Female Recipient Title', validators=[DataRequired()], render_kw={"placeholder": "Trainee:(Female)"})  
    signatory_name_1 = StringField('First Signatory Name', validators=[DataRequired()])
    signatory_position_1 = StringField('First Signatory Position', validators=[DataRequired()])
    signature_image_1 = FileField('First Signature Image', validators=[
        FileRequired(message='First signature image is required.'),
        FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG and JPEG images are accepted.')
    ])

    # Fields for the second signatory
    signatory_name_2 = StringField('Second Signatory Name')
    signatory_position_2 = StringField('Second Signatory Position')
    # signature_image_2 = FileField('Second Signature Image', validators=[
    #     FileRequired(message='Second signature image is required.'),
    #     FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG and JPEG images are accepted.')
    # ])
    signature_image_2 = FileField('Second Signature Image', validators=[
        FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG and JPEG images are accepted.')
    ])

    submit = SubmitField('Submit')
    file = FileField('Attendance File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Submit')

class EnglishCertificateForm(FlaskForm):
    intro_en = StringField('Intro', validators=[DataRequired()], render_kw={"placeholder": "The Computer College testifies that"})
    female_recipient_title_en = StringField('Female Recipient Title', validators=[DataRequired()], render_kw={"placeholder": "Trainee:(Female)"})
    male_recipient_title_en = StringField('Male Recipient Title', validators=[DataRequired()], render_kw={"placeholder": "Trainee:(Male)"})
    greeting_female_en = StringField('Greeting for Females', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for her success"})
    greeting_male_en = StringField('Greeting for Males', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for his success"})
    certificate_description_female_en = TextAreaField('Event Description for Female', validators=[DataRequired()])
    certificate_description_male_en = TextAreaField('Event Description for Male', validators=[DataRequired()])
    
class NewTemplates(FlaskForm):
    template_name= StringField('*Template Name', validators=[DataRequired(), Length(min=2, max=30)])
    template_image= FileField('*Upload Background', validators=[DataRequired()])
    submit= SubmitField('Add')



class ChangeEmailForm(FlaskForm):
        email = StringField('New Email', validators=[DataRequired(), Email()])
        submit = SubmitField('Change Email')

        def validate_email(self, email):
            existing_email = users.query.filter_by(
            email=email.data).first()
            if existing_email:
                raise ValidationError(
                    'That email already exists. Please choose a different one.')
            
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        EqualTo('confirm_new_password', message='Passwords must match.')])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

class ChangeNameForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    submit = SubmitField('Change Name')

class customizationForm(FlaskForm):
    item = StringField()
    x = IntegerField('*x_postion')
    y = IntegerField('*y_postion')
    h = IntegerField('*Height')
    w = IntegerField('*Width')
    submit = SubmitField('Save')

# class Certificate(db.Model):
#     hash = db.Column(db.String(25), primary_key=True)
#     recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
#     certificate_event_id = db.Column(db.String(255), db.ForeignKey('addCertificate.certificate_event_id'))

class VerifyCertificateForm(FlaskForm):
    certificate_hash = StringField('Certificate Code', validators=[DataRequired()])
    submit = SubmitField('Verify')
