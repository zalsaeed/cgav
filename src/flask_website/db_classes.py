from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField,IntegerField,FloatField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError, EqualTo, Email
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import db_connection

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt
# app = Flask(__name__)

class users(db.Model, UserMixin):
    # this variable(id) we cant change the name to (user_id) because it will conflict with UserMixin
    id = db.Column(db.Integer, primary_key=True, unique=True)
    Fname = db.Column(db.String(40), nullable=False)
    Lname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.Integer, nullable=True)

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


# Certificates classes
# class Template(db.Model):
#     __tablename__ = 'template'
#     template_id = db.Column(db.Integer, primary_key=True, unique=True )
#     id = db.Column(db.Integer)
#     template_name = db.Column(db.String(30), nullable=False)
#     template_image = db.Column(db.String(300), nullable=False)


# class Event_type(db.Model):
#     event_type_id = db.Column(db.Integer, primary_key=True)
#     #duplicate event_type_id = db.Column(db.Integer, primary_key=True)
#     is_active = db.Column(db.Boolean, default=True)

class recipient(db.Model):
    recipient_id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.String(5))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))

class instructor(db.Model):
    instructor_id = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    middle_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    gender = db.Column(db.String(5))
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))

# class CertificateCustomizations(db.Model):
#     customization_id = db.Column(db.String(255), primary_key=True)
#     template_id = db.Column(db.String(255), db.ForeignKey('template.template_id'))
#     id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     title_position_x = db.Column(db.Integer)
#     title_position_y = db.Column(db.Integer)
#     # Add other customization fields as needed
#     # ...
#     template = db.relationship('template', backref='customizations')
#     user = db.relationship('users', backref='customizations')

# class addCertificate(db.Model):
#     __tablename__ = 'addCertificate'

#     certificate_event_id = db.Column(db.String(255), primary_key=True)
#     certificate_title = db.Column(db.String(255))
#     event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.event_type_id'))
#     recipient_id = db.Column(db.String(255), db.ForeignKey('recipient.recipient_id'))
#     customization_id = db.Column(db.String(255), db.ForeignKey('certificate_customizations.customization_id'))
#     template_id = db.Column(db.String(255), db.ForeignKey('template.template_id'))
#     instructor_id = db.Column(db.String(255), db.ForeignKey('instructor.instructor_id'))
#     event_start_date = db.Column(db.DateTime)
#     event_end_date = db.Column(db.DateTime)
#     description = db.Column(db.String(320))
#     secret_key = db.Column(db.String(255))
#     presenter_name = db.Column(db.String(255))
#     secret_phrase = db.Column(db.String(255))
#     event_date = db.Column(db.DateTime)
#     certificate_description = db.Column(db.String(255))
#     file_path = db.Column(db.String(255))  # Assuming the file path is a string

#     event_type = db.relationship('Event_type', backref='certificates')
#     recipient = db.relationship('recipient', backref='certificates')
#     customization = db.relationship('CertificateCustomizations', backref='certificates')
#     template = db.relationship('template', backref='certificates')
#     instructor = db.relationship('instructor', backref='certificates')

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
