# certificate_models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, Text, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

# Assuming the db object will be imported from elsewhere, like your main app.py
# This import line is assuming the db instance is initialized in a file named 'extensions.py'
from extensions import db

class CertificateEvent(db.Model):
    __tablename__ = 'addCertificate'
    certificate_event_id = db.Column(db.String(255), primary_key=True)
    certificate_title = db.Column(db.String(255))
    event_type_id = db.Column(db.String(255))  # Make sure this references an existing event type
    presenter_name = db.Column(db.String(255))  # New field
    secret_phrase = db.Column(db.String(255))  # New field
    event_date = db.Column(db.DateTime)  # New field
    certificate_description = db.Column(db.Text)  # New field
    file_path = db.Column(db.String(255))  # New field, to store file path if needed
    # ... any additional fields ...

class EventType(db.Model):
    __tablename__ = 'Event_type'  # Ensure this matches the table name in the database
    event_type_id = db.Column(db.String(50), primary_key=True)
    event_type_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

class CertificateForm(FlaskForm):
    certificate_title = StringField('Certificate Title', validators=[DataRequired()])
    presenter_name = StringField('Presenter Name', validators=[DataRequired()])
    secret_phrase = StringField('Secret Phrase', validators=[DataRequired()])
    event_type = SelectField('Event Type', choices=[
        ('type1', 'Event Type 1'),
        ('type2', 'Event Type 2'),
        ('type3', 'Event Type 3')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    certificate_description = TextAreaField('Certificate Description', validators=[DataRequired()])
    file = FileField('Attendance File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Submit')
