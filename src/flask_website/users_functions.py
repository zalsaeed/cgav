from flask import render_template, url_for, redirect, flash
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

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = db_classes.users(password=hashed_password, user_role= form.user_role.data, email=form.email.data, Fname=form.Fname.data, Lname=form.Lname.data)
        db.session.add(new_user)
        db.session.commit()
        flash('success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


def login():
    form = db_classes.LoginForm()
    if form.validate_on_submit():
        user = db_classes.users.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('certificates'))
    return render_template('login.html', form=form)


def admin():
    users_list = db_classes.users.query.all()
    user_role = current_user.user_role
    if user_role == 1:
        return render_template('admin.html',users_list=users_list)
    else:
        flash('Access denied')
        return redirect(url_for('certificates'))
  

# def update_user(id):
#     form = db_classes.UpdateForm()
#     user_to_edit = db_classes.users.query.get(id)
#     existing_email = db_classes.users.query.filter_by(email=form.email.data).first()
#     if form.validate_on_submit():
#         if form.email.data == user_to_edit.email:
#             email_to_save = user_to_edit.email
#         elif existing_email:
#             flash('email already exist')
#             return redirect(url_for('update_user',id=user_to_edit.id))
#         else:
#             email_to_save = form.email.data


#         if form.password.data == user_to_edit.password:
#             password_to_save = form.password.data
#         else:
#             password_to_save = bcrypt.generate_password_hash(form.password.data)
#         user_to_edit = update(db_classes.users).where(db_classes.users.id == id).values(user_role = form.user_role.data, email = email_to_save, Fname = form.Fname.data, password = password_to_save)
#         db.session.execute(user_to_edit)
#         db.session.commit()
#         flash('success')
#         return redirect(url_for('admin'))
#     else:
#         return render_template('update.html',form=form,user_to_edit=user_to_edit)
def update_user(id):
    form = db_classes.UpdateForm()  # Get the form instance
    user_to_edit = db_classes.users.query.get(id)  # Get the user by ID

    # # Check if the form is submitted and valid
    # if form.validate_on_submit():

    #     # Check if the email is the same or already exists in another user's profile
    #     if form.email.data == user_to_edit.email:
    #         email_to_save = user_to_edit.email  # No change in email
    #     else:
    #         existing_email = db_classes.users.query.filter_by(email=form.email.data).first()
    #         if existing_email:  # Check if the email is already taken
    #             flash('Email already exists', 'danger')
    #             return redirect(url_for('update_user', id=user_to_edit.id))  # Redirect back to the form
    #         email_to_save = form.email.data  # Use the new email if no conflict

    #     # Check if the password field is filled
    #     if form.password.data:
    #         if bcrypt.check_password_hash(user_to_edit.password, form.password.data):
    #             password_to_save = user_to_edit.password  # Keep the current password if it's the same
    #         else:
    #             password_to_save = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Hash the new password
    #     else:
    #         password_to_save = user_to_edit.password  # Keep the current password if the field is empty

    #     # Update the user object with the form data
    #     user_to_edit.Fname = form.Fname.data
    #     user_to_edit.Lname = form.Lname.data
    #     user_to_edit.email = email_to_save
    #     user_to_edit.user_role = form.user_role.data
    #     user_to_edit.password = password_to_save

    #     # Commit the changes to the database
    #     db.session.commit()

    #     flash('User updated successfully', 'success')  # Flash success message
    #     return redirect(url_for('admin'))  # Redirect to the admin page

    # else:
    #     # If the form is not valid or it's a GET request, render the update page
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