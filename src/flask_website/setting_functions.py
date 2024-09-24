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

def settings(id):
    user = db_classes.users.query.get_or_404(id)
    # Pass the user's first and last name to the template
    return render_template('settings.html', user=user)

def change_name(id):
    user_to_edit = db_classes.users.query.get_or_404(id)
    form = db_classes.ChangeNameForm()
    if form.validate_on_submit():
        user_to_edit.Fname = form.name.data.split()[0]  # assuming the first name is the first word
        user_to_edit .Lname = ' '.join(form.name.data.split()[1:])  # rest of the parts are considered as the last name
        db.session.commit()
        flash('User name has been updated.', 'success')
        return render_template('settings.html', user=user_to_edit)
    return render_template('change_name.html', form=form , user=user_to_edit)

def change_email(id):
    user_to_edit = db_classes.users.query.get_or_404(id)
    form = db_classes.ChangeEmailForm()
    if form.validate_on_submit():
        user_to_edit.email = form.email.data
        db.session.commit()
        flash('User email has been updated.', 'success')
        return render_template('settings.html', user=user_to_edit)
    return render_template('change_email.html', form=form ,user=user_to_edit)

def change_password(id):
    user_to_edit = db_classes.users.query.get_or_404(id)
    form = db_classes.ChangePasswordForm()
    message = None  # Initialize the message variable
    try:
        if form.validate_on_submit():
            if bcrypt.check_password_hash(user_to_edit.password, form.old_password.data):
                if form.new_password.data == form.confirm_new_password.data:
                    # Set new password with bcrypt and decode it to string
                    hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                    user_to_edit.password = hashed_password
                    db.session.commit()
                    flash('Your password has been updated successfully.')
                    return render_template('settings.html', user=user_to_edit)
                else:
                    message = 'New password and confirmation do not match.'
            else:
                message = 'Incorrect old password.'
    except ValueError as e:
            # Handle the invalid salt error
             message = 'Incorrect old password.'

    # Pass the message to the template. If the message is None, nothing will be displayed.
    return render_template('change_password.html', form=form, message=message,user=user_to_edit)