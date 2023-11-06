from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired,DataRequired , Length, ValidationError
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Global variable to store existing event types
existing_event_types = []

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['UPLOAD_FOLDER']='../certificate-templates'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

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
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
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


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
