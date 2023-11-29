
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import app

db = app.db

# app = Flask(__name__)

class users(db.Model, UserMixin):
    # this variable(id) we cant change the name to (user_id) because it will conflict with UserMixin
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.Integer, nullable=False)

class RegisterForm(FlaskForm):
    user_name = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "user_name"})
    
    # id = StringField(validators=[
    #                        InputRequired()], render_kw={"placeholder": "user_id"})
    
    user_role = StringField(validators=[
                           InputRequired()], render_kw={"placeholder": "user_role"})

    password = PasswordField(validators=[
                             InputRequired(),EqualTo('confirm_password','miss match'), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    confirm_password = PasswordField(validators=[
                             InputRequired()], render_kw={"placeholder": "confirm Password"})

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

