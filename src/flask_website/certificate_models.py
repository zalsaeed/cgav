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
    template = db.relationship('Template', backref='certificates')
    presenter_name = db.Column(db.String(255))  # New field
    secret_phrase = db.Column(db.String(255))  # New field
    event_date = db.Column(db.DateTime)  # New field
    certificate_description_female = db.Column(db.Text)
    certificate_description_male = db.Column(db.Text)
    file_path = db.Column(db.String(255))  # New field, to store file path if needed
    male_recipient_title = db.Column(db.String(255))
    female_recipient_title = db.Column(db.String(255))
    intro_en = db.Column(db.String(255))  # Introduction in English
    intro_ar = db.Column(db.String(255))  # Introduction in Arabic
    greeting_female_en = db.Column(db.Text)  # Female greeting in English
    greeting_female_ar = db.Column(db.Text)  # Female greeting in Arabic
    greeting_male_en = db.Column(db.Text)  # Male greeting in English
    greeting_male_ar = db.Column(db.Text)  # Male greeting in Arabic
    signatory_name_1_en = db.Column(db.String(255))  # First signatory name in English
    signatory_name_1_ar = db.Column(db.String(255))  # First signatory name in Arabic
    signatory_position_1_en = db.Column(db.String(255))  # First signatory position in English
    signatory_position_1_ar = db.Column(db.String(255))  # First signatory position in Arabic
    signatory_name_2_en = db.Column(db.String(255))  # Second signatory name in English
    signatory_name_2_ar = db.Column(db.String(255))  # Second signatory name in Arabic
    signatory_position_2_en = db.Column(db.String(255))  # Second signatory position in English
    signatory_position_2_ar = db.Column(db.String(255))
    Second_Signatory_Path = db.Column(db.String(255))
    First_Signatory_Path = db.Column(db.String(255))
    male_recipient_title_en = db.Column(db.String(255))
    male_recipient_title_ar = db.Column(db.String(255))
    female_recipient_title_en = db.Column(db.String(255))
    female_recipient_title_ar = db.Column(db.String(255))

# Certificates classes
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
    #greeting_female = StringField('Greeting for Females', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for her success"})
    #greeting_male = StringField('Greeting for Males', validators=[DataRequired()], render_kw={"placeholder": "Best wishes for his success"})
    event_type = SelectField('Event Type', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])

    intro_en = StringField('Introduction (English)', validators=[DataRequired()])
    intro_ar = StringField('Introduction (Arabic)', validators=[DataRequired()])
    greeting_female_en = StringField('Greeting for Females (English)', validators=[DataRequired()])
    greeting_female_ar = StringField('Greeting for Females (Arabic)', validators=[DataRequired()])
    greeting_male_en = StringField('Greeting for Males (English)', validators=[DataRequired()])
    greeting_male_ar = StringField('Greeting for Males (Arabic)', validators=[DataRequired()])
    signatory_name_1_en = StringField('First Signatory Name (English)', validators=[DataRequired()])
    signatory_name_1_ar = StringField('First Signatory Name (Arabic)', validators=[DataRequired()])
    signatory_position_1_en = StringField('First Signatory Position (English)', validators=[DataRequired()])
    signatory_position_1_ar = StringField('First Signatory Position (Arabic)', validators=[DataRequired()])
    signatory_name_2_en = StringField('Second Signatory Name (English)')
    signatory_name_2_ar = StringField('Second Signatory Name (Arabic)')
    signatory_position_2_en = StringField('Second Signatory Position (English)')
    signatory_position_2_ar = StringField('Second Signatory Position (Arabic)')

    certificate_description_female = TextAreaField('Event Description for Female', validators=[DataRequired()])
    certificate_description_male = TextAreaField('Event Description for Male', validators=[DataRequired()])
    #intro = StringField('Intro', validators=[DataRequired()], render_kw={"placeholder": "تشهد كلية الحاسب"})
    male_recipient_title_en = StringField('Male Recipient Title (English)', validators=[DataRequired()])
    male_recipient_title_ar = StringField('Male Recipient Title (Arabic)', validators=[DataRequired()])
    female_recipient_title_en = StringField('Female Recipient Title (English)', validators=[DataRequired()])
    female_recipient_title_ar = StringField('Female Recipient Title (Arabic)', validators=[DataRequired()])

    #signatory_name_1 = StringField('First Signatory Name', validators=[DataRequired()])
    #signatory_position_1 = StringField('First Signatory Position', validators=[DataRequired()])
    signature_image_1 = FileField('First Signature Image', validators=[
        FileRequired(message='First signature image is required.'),
        FileAllowed(['png', 'jpg', 'jpeg'], 'Only PNG and JPEG images are accepted.')
    ])

    # Fields for the second signatory
    #signatory_name_2 = StringField('Second Signatory Name')
    #signatory_position_2 = StringField('Second Signatory Position')
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