# colorStandard Library Imports
import json
import os
import uuid

# Related Third Party Imports
from flask import jsonify, request, redirect, url_for, render_template, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import update

# Local App/Library Specific Imports
import db_connection
import db_classes
from db_classes import CertificateCustomizations, Template


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def edit_template(temp_id):
    temp = Template.query.get_or_404(temp_id)
    if request.method == 'POST':
        language = request.form.get('language')
        if language == 'arabic':
            return redirect('/artemplate/'+temp_id)
        elif language == 'english':
            return redirect('/entemplate/'+temp_id)
        elif language == 'arabic_english':
            return redirect('/bitemplate/'+temp_id)
    return render_template('img.html',temp=temp)

def newtemp():
    form = db_classes.NewTemplates()
    if form.validate_on_submit():
        file = form.template_image.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))


        new_template = Template(template_name=form.template_name.data,
                                           id = current_user.id,
                                           template_image=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)),
                                           is_active=True)
        db.session.add(new_template)
        db.session.commit()

        flash('A new template has been added successfully.')
        return redirect(url_for('selectTemp'))  # It's better to use url_for() here

    return render_template('create_new_template.html', form=form)

def artemplateEdit(temp_id):
    # temp = db_classes.Template.query.filter_by(template_name=tempname).first()
    # tempid= temp.template_id if temp else None
    temp = Template.query.get_or_404(temp_id)
    form=db_classes.customizationForm()
    json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/FakeData.json')
    ar_json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/bidata.json')
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
        if form_item == "contact_info":
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            form_websit=form.websit.data
            form_websitlinke=form.websitlinke.data
            form_X=form.X.data
            form_Xlink=form.Xlink.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                customization_data[form_item]['contact']['Web']['Websit'] = form_websit
                customization_data[form_item]['contact']['Web']['Websitlinke'] = form_websitlinke
                customization_data[form_item]['contact']['X']['X'] = form_X
                customization_data[form_item]['contact']['X']['Xlink'] = form_Xlink
        else:
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                
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
                new_customization = CertificateCustomizations(
                                                            id = current_user.id,
                                                            template_id = temp.template_id,
                                                            items_positions = customization_data )
                # Add and commit the new record to the database
                db.session.add(new_customization)
                db.session.commit()
        
    
             

    return render_template('arTepmlateEdit.html', temp=temp,data=data,arData=arData,form=form)

def entemplateEdit(temp_id):
    # temp = db_classes.Template.query.filter_by(template_name=tempname).first()
    # tempid= temp.template_id if temp else None
    temp = Template.query.get_or_404(temp_id)
    form=db_classes.customizationForm()
    json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/FakeData.json')
    # ar_json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/Arabicdata.json')
    custom_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/customization.json')

    # Read the JSON file
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # with open(ar_json_file, 'r') as file:
    #     arData = json.load(file)
    
    with open(custom_file,'r') as file:
      customization_data = json.load(file)

    
    # if request.method == 'POST':
    if form.validate_on_submit():
        form_item = form.item.data  # Assuming form.item is a Flask-WTF field
        if form_item == "contact_info":
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            form_websit=form.websit.data
            form_websitlinke=form.websitlinke.data
            form_X=form.X.data
            form_Xlink=form.Xlink.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                customization_data[form_item]['contact']['Web']['Websit'] = form_websit
                customization_data[form_item]['contact']['Web']['Websitlinke'] = form_websitlinke
                customization_data[form_item]['contact']['X']['X'] = form_X
                customization_data[form_item]['contact']['X']['Xlink'] = form_Xlink
        else:
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                
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
                new_customization = CertificateCustomizations(
                                                            id = current_user.id,
                                                            template_id = temp.template_id,
                                                            items_positions = customization_data )
                # Add and commit the new record to the database
                db.session.add(new_customization)
                db.session.commit()
        
    
             
    return render_template('enTemplateEdit.html', temp=temp,data=data,form=form)

def bitemplateEdit(temp_id):
    # temp = db_classes.Template.query.filter_by(template_name=tempname).first()
    # tempid= temp.template_id if temp else None
    temp = Template.query.get_or_404(temp_id)
    form=db_classes.customizationForm()
    json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/FakeData.json')
    ar_json_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/bidata.json')
    custom_file = os.path.abspath('../src/flask_website/FakeDataForAppearance/arcustomization.json')

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
        if form_item == "contact_info":
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            form_websit=form.websit.data
            form_websitlinke=form.websitlinke.data
            form_X=form.X.data
            form_Xlink=form.Xlink.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                customization_data[form_item]['contact']['Web']['Websit'] = form_websit
                customization_data[form_item]['contact']['Web']['Websitlinke'] = form_websitlinke
                customization_data[form_item]['contact']['X']['X'] = form_X
                customization_data[form_item]['contact']['X']['Xlink'] = form_Xlink
        else:
            form_x = form.x.data
            form_y = form.y.data
            form_h = form.h.data
            form_w = form.w.data
            form_color = form.color.data
            form_text = form.text.data
            if form_item in customization_data:
                customization_data[form_item]['x'] = float(form_x)
                customization_data[form_item]['y'] = float(form_y)
                customization_data[form_item]['h'] = float(form_h)
                customization_data[form_item]['w'] = float(form_w)
                customization_data[form_item]['color'] = form_color
                customization_data[form_item]['AltText'] = form_text
                
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
                new_customization = CertificateCustomizations(
                                                            id = current_user.id,
                                                            template_id = temp.template_id,
                                                            items_positions = customization_data )
                # Add and commit the new record to the database
                db.session.add(new_customization)
                db.session.commit()
        
             
    return render_template('biTemplateEdit.html', temp=temp,data=arData['data'],arData=arData['bidata'],form=form)

def selectTemp():
     # Assuming the user ID is stored in the id field of the User model
    if current_user.user_role == 1 :
        user_templates = Template.query.all()
    else:
        user_templates = Template.query.filter_by(id=current_user.id).all()
    return render_template("select_template.html", templates=user_templates)

def DeleteTemp(temp_id):
    tepmDelate = update(Template).where(Template.template_id == temp_id).values(is_active=False)
    db.session.execute(tepmDelate)
    db.session.commit()
    return redirect("/Select_template")
