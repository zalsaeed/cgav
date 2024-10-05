from flask import render_template, url_for, redirect, flash, jsonify, request
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import update
import db_connection
import db_classes



app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = db_connection.login_manager
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db_classes.users.query.get(int(user_id))


def register():
    form = db_classes.RegisterForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Check if the email is already in use
            existing_user = db_classes.users.query.filter_by(email=form.email.data).first()
            if existing_user:
                return jsonify({'message': 'Email already used', 'status': 'error'})

            # If passwords do not match, return an error message
            if form.password.data != form.confirm_password.data:
                return jsonify({'message': 'Passwords do not match', 'status': 'error'})

            # Hash the password and add the new user
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = db_classes.users(
                password=hashed_password,
                user_role=form.user_role.data,
                email=form.email.data,
                Fname=form.Fname.data,
                Lname=form.Lname.data
            )
            db.session.add(new_user)
            db.session.commit()

            # Return success message
            return jsonify({'message': 'Registration successful', 'status': 'success', 'redirect_url': url_for('login')})

        # If validation fails, return form errors
        return jsonify({
            'message': 'Validation failed',
            'status': 'error',
            'errors': form.errors
        })
    
    # Handle GET request: render the form when the page is accessed
    return render_template('register.html', form=form)


def login():
    form = db_classes.LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = db_classes.users.query.filter_by(email=form.email.data).first()

            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return jsonify({'message': 'Login successful', 'status': 'success', 'redirect_url': url_for('certificates')})

            # Incorrect email or password
            return jsonify({'message': 'Invalid email or password', 'status': 'error'})

        # Return form validation errors (e.g., missing fields)
        return jsonify({'message': 'Validation failed', 'status': 'error', 'errors': form.errors})

    # Handle GET request: render the login page
    return render_template('login.html', form=form)


def admin():
    users_list = db_classes.users.query.all()
    user_role = current_user.user_role
    if user_role == 1:
        return render_template('admin.html',users_list=users_list)
    else:
        # flash('Access denied')
        return redirect(url_for('certificates'))
  


def update_user(id):
    form = db_classes.UpdateForm()  # Get the form instance
    user_to_edit = db_classes.users.query.get(id)  # Get the user by ID
    return render_template('update.html', form=form, user_to_edit=user_to_edit)


def delete_user(id):
    if current_user.id == id :
        flash('you are currently using this user')
        return redirect(url_for('settings'))
    else:

        user_to_delete = db_classes.users.query.get(id)
        uname = user_to_delete.Fname
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect(url_for('admin'))