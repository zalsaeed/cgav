import json
import os
import uuid
from flask import Flask, render_template, url_for, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import  LoginManager, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import update
import db_connection
import db_classes
from certificate_models import CertificateCustomizations,Template

app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def newtemp():
    form = db_classes.NewTemplates()
    if form.validate_on_submit():
        file = form.template_image.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))


        new_template = Template(template_name=form.template_name.data,
                                           id = current_user.id,
                                           template_image=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        db.session.add(new_template)
        db.session.commit()

        flash('A new template has been added successfully.')
        return redirect(url_for('selectTemp'))  # It's better to use url_for() here

    return render_template('create_new_template.html', form=form)

def template(temp_id):
    # temp = db_classes.Template.query.filter_by(template_name=tempname).first()
    # tempid= temp.template_id if temp else None
    temp = Template.query.get_or_404(temp_id)
    form=db_classes.customizationForm()
    json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/FakeData.json')
    ar_json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/Arabicdata.json')
    custom_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/customization.json')

    # Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    with open(ar_json_file, 'r') as file:
        arData = json.load(file)
    
    with open(custom_file,'r') as file:
      customization_data = json.load(file)

    
    # if request.method == 'POST':
    if form.validate_on_submit():
        form_item = form.item.data  # Assuming form.item is a Flask-WTF field
        form_x = form.x.data
        form_y = form.y.data
        form_h = form.h.data
        form_w = form.w.data
        if form_item in customization_data:
            customization_data[form_item]['x'] = form_x
            customization_data[form_item]['y'] = form_y
            customization_data[form_item]['h'] = form_h
            customization_data[form_item]['w'] = form_w
        with open(custom_file, 'w') as file:
            json.dump(customization_data, file, indent=2)
        
        existing_customization = CertificateCustomizations.query.filter_by(
            id=current_user.id,
            template_id=temp.template_id).first()
        if existing_customization:
            # existing_customization.items_positions = customization_data
            # Reactivate the existing event type using update statement
            custom = update(CertificateCustomizations).where(CertificateCustomizations.template_id == temp.template_id and CertificateCustomizations.id == current_user.id).values(items_positions = customization_data)
            db.session.execute(custom)
            db.session.commit()
        else:
            new_customization = CertificateCustomizations(customization_id=str(uuid.uuid4()),
                                                          id = current_user.id,
                                                          template_id = temp.template_id,
                                                          items_positions = customization_data )
            # Add and commit the new record to the database
            db.session.add(new_customization)
            db.session.commit()
    flash(f'Customizations Added Successfully.')

    return render_template('anotherAppearance.html', temp=temp,data=data,arData=arData,form=form)

def selectTemp():
     # Assuming the user ID is stored in the id field of the User model
    if current_user.user_role == 1 :
        user_templates = Template.query.all()
    else:
        user_templates = Template.query.filter_by(id=current_user.id).all()
    return render_template("select_template.html", templates=user_templates)