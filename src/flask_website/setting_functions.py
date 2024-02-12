# Standard Library Imports
from flask import Flask, render_template, url_for, redirect, flash, session

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

# Local App/Library Specific Imports
import db_connection
import db_classes


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def settings():
    user = current_user
    # Pass the user's first and last name to the template
    return render_template('settings.html', first_name=user.Fname, last_name=user.Lname)

def change_name():
    form = db_classes.ChangeNameForm()
    if form.validate_on_submit():
        current_user.Fname = form.name.data.split()[0]  # assuming the first name is the first word
        current_user.Lname = ' '.join(form.name.data.split()[1:])  # rest of the parts are considered as the last name
        db.session.commit()
        flash('Your name has been updated.', 'success')
        return redirect(url_for('settings'))
    return render_template('change_name.html', form=form)

def change_email():
    form = db_classes.ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Your email has been updated.', 'success')
        return redirect(url_for('settings'))
    return render_template('change_email.html', form=form)

def change_password():
    form = db_classes.ChangePasswordForm()
    message = None  # Initialize the message variable

    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            if form.new_password.data == form.confirm_new_password.data:
                # Set new password with bcrypt and decode it to string
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                current_user.password = hashed_password
                db.session.commit()
                message = 'Your password has been updated successfully.'
            else:
                message = 'New password and confirmation do not match.'
        else:
            message = 'Incorrect old password.'

    # Pass the message to the template. If the message is None, nothing will be displayed.
    return render_template('change_password.html', form=form, message=message)