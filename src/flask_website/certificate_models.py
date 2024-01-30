# certificate_models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, Text, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from sqlalchemy.orm import relationship


# Assuming the db object will be imported from elsewhere, like your main app.py
# This import line is assuming the db instance is initialized in a file named 'extensions.py'
from extensions import db

class CertificateEvent(db.Model):
    __tablename__ = 'addCertificate'
    certificate_event_id = db.Column(db.String(255), primary_key=True)
    customization_id = db.Column(db.String(255))
    certificate_title = db.Column(db.String(255))
    event_type_id = db.Column(db.Integer, db.ForeignKey('Event_type.event_type_id'))  # Foreign key relationship
    template_path = db.Column(db.String(255))
    template_id = db.Column(db.Integer, db.ForeignKey('template.template_id'))
    # Define the relationship to EventType
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
    secret_key = db.Column(db.String(255)) 
    recipient_id = db.Column(db.String(255))
    
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
# class EventType(db.Model):
#     __tablename__ = 'Event_type' 
#     event_type_id = db.Column(db.String(50), primary_key=True)
#     event_type_name = db.Column(db.String(255))
#     is_active = db.Column(db.Boolean, default=True)

class EventType(db.Model):
    __tablename__ = 'Event_type'  # Ensure this matches the table name in the database
    event_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_type_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

class CertificateForm(FlaskForm):
    certificate_title = StringField('Event Title', validators=[DataRequired()])
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

# class Signature(db.Model):
    # __tablename__ = 'signatures'
    # id = db.Column(db.Integer, primary_key=True)
    # certificate_event_id = db.Column(db.String(255), db.ForeignKey('addCertificate.certificate_event_id'))
    # signatory_name = db.Column(db.String(255))
    # signatory_position = db.Column(db.String(255))
    # signature_image_path = db.Column(db.String(255))  # Path to the stored signature image file
# 
    # certificate_event = relationship('CertificateEvent', backref='signatures')
# 

class Certificate(db.Model):
    __tablename__ = 'Certificate'
    hash = db.Column(db.String(25), primary_key=True)
    recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
    certificate_event_id = db.Column(db.String(255), db.ForeignKey('CertificateEvent.certificate_event_id'))
   
# class Certificate(db.Model):
#     __tablename__ = 'Certificate'
#     # hash = db.Column(db.String(25), primary_key=True)
#     # recipient_id = db.Column(db.String(255))
#     # certificate_event_id = db.Column(db.String(255))