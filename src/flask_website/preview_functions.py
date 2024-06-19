import json
import os
from flask import send_from_directory
from typing import List, Dict
import yaml
import textwrap

# Related Third Party Imports
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.font_manager import FontProperties
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from PIL import Image 

# Local App/Library Specific Imports
import db_connection
import db_classes
from db_classes import  Template
import util
import configuration_loader


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt





def load_default_data():
    with open(os.path.abspath('events/sample-event.yaml'), 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def load_default_endata():
    with open(os.path.abspath('events/en-sample-event.yaml'), 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def load_default_bidata():
    with open(os.path.abspath('events/bi-sample-event.yaml'), 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def img(temp_id, lang):
    if db_classes.CertificateCustomizations.query.filter_by(template_id=temp_id).first():
        customization = db_classes.CertificateCustomizations.query.filter_by(template_id=temp_id).first().items_positions
    else: 
        with open('./customization/customization.json', 'r') as file:
            customization = json.load(file)
    if lang=="en":
        default_data = load_default_endata()
    else:
        default_data = load_default_data() #load sampl recepent information form yml file 
    
    recipient_title=f"{default_data.get('male_recipient_title', 'Default male_recipient_titleText')}"
    certificate_intro=f"{default_data.get('intro', 'Default Intro Text')}"
    certificate_body=f"{default_data.get('male_certificate_body', 'Default male_certificate_body Text')}"
    greeting_txt=f"{default_data.get('male_final_greeting', 'Default male_final_greeting Text')}"
    dean_name=f"{default_data.get('dean_name', 'Default dean_name Text')}"
    dean_position=f"{ default_data.get('dean_position', 'Default dean_position Text')}"
    path_to_dean_signature=f"{default_data.get('path_to_dean_signature', 'Default path_to_dean_signature Text')}"
    csu_director_name=f"{default_data.get('csu_director_name', 'Default csu_director_name Text')}"
    csu_position=f"{ default_data.get('csu_position', 'Default csu_position Text')}"
    path_to_csu_head_signature=f"{default_data.get('path_to_csu_signature', 'Default path_to_csu_signature Text')}"

    template= Template.query.filter_by(template_id=temp_id).first()
    if customization:
            # Extract values for Certificate_Title
            certificate_intro_values = customization.get("Intro", {})

            intro_x=certificate_intro_values.get("x",0)
            intro_y=certificate_intro_values.get("y",0)
            intro_w=certificate_intro_values.get("w",0)
            intro_h=certificate_intro_values.get("h",0)
            intro_alt=certificate_intro_values.get("AltText")
            intro_color=certificate_intro_values.get("color","black")

            recipient_title_values = customization.get("recipient_title", {})
            title_x=recipient_title_values.get("x",0)
            title_y=recipient_title_values.get("y",0)
            title_w=recipient_title_values.get("w",0)
            title_h=recipient_title_values.get("h",0)
            title_alt=recipient_title_values.get("AltText")
            title_color=recipient_title_values.get("color","black")

            recipient_name_values = customization.get("recipient_name", {})
            name_x=recipient_name_values.get("x",0)
            name_y=recipient_name_values.get("y",0) 
            name_w=recipient_name_values.get("w",0)
            name_h=recipient_name_values.get("h",0)
            name_alt=recipient_name_values.get("AltText")
            name_color=recipient_name_values.get("color","black")

            body_values = customization.get("body", {})
            body_x=body_values.get("x",0)
            body_y=body_values.get("y",0)
            body_w=body_values.get("w",0)
            body_h=body_values.get("h",0)
            body_alt=body_values.get("AltText")
            body_color=body_values.get("color","black")

            final_greeting_values = customization.get("final_greeting", {})
            greeting_x=final_greeting_values.get("x",0)
            greeting_y=final_greeting_values.get("y",0)
            greeting_alt=final_greeting_values.get("AltText")
            greeting_color=final_greeting_values.get("color","black")


            contact_info_values = customization.get("contact_info", {})
            contact_info_x=contact_info_values.get("x",0)
            contact_info_y=contact_info_values.get("y",0)
            contact_info_color=contact_info_values.get("color","black")
            Websit_value = contact_info_values.get("contact", {}).get("Web", {}).get("Websit", "")
            Websitlinke_value = contact_info_values.get("contact", {}).get("Web", {}).get("Websitlinke", "")
            x_value = contact_info_values.get("contact", {}).get("X", {}).get("X", "")
            xlink_value = contact_info_values.get("contact", {}).get("X", {}).get("Xlink", "")

            signature_1_values =customization.get("signature_1", {})
            signature_1_x = signature_1_values.get("x",0)
            signature_1_y = signature_1_values.get("y",0)
            signature_1_w = signature_1_values.get("w",0)
            signature_1_h = signature_1_values.get("h",0)
            signature_1_alt=signature_1_values.get("AltText")
            signature_1_color = signature_1_values.get("color","black")

            signature_2_values =customization.get("signature_2", {})
            signature_2_x = signature_2_values.get("x",0)
            signature_2_y = signature_2_values.get("y",0)
            signature_2_w = signature_2_values.get("w",0)
            signature_2_h = signature_2_values.get("h",0)
            signature_2_alt=signature_2_values.get("AltText")
            signature_2_color = signature_2_values.get("color","black")
    dpi = 300
    # img = mpimg.imread(template.template_image ,format='RGBA')
    pil_img = Image.open(template.template_image)# Convert float image to uint8

    # # Resize the image to fit A4 landscape dimensions
    resized_img = pil_img.resize(size=(1122,793))
    matplotlib.rcParams['pdf.fonttype'] = 42 
   
    # Create a figure with A4 landscape dimensions
    fig_width = 3.74
    fig_height = 2.64 
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), frameon=False)
    # Display the resized image without axes and stretching it to fill the entire figure
    ax.imshow(resized_img, aspect='auto')

    # Turn off axis
    ax.axis('off')

    # Specify the path to your custom Arabic font
    font_path = os.path.abspath('fonts/SakkalMajalla/majallab.ttf')
    font_path2 = os.path.abspath('fonts/Amiri/Amiri-Regular.ttf')
    font_size = 9 # Font size

    if (x_value and xlink_value ) and not (Websit_value and Websitlinke_value):
         contact_info = {
                1: ["img/x-logo.png", x_value, xlink_value],
                2: ["img/checkmark.png", "ggGBs2hu9j", None]
                }
    elif (Websit_value and Websitlinke_value) and not (x_value and xlink_value ) :
        contact_info = {
                    1: ["img/globe.png",Websit_value, Websitlinke_value],
                    2: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    elif (Websit_value and Websitlinke_value) and (x_value and xlink_value ):
        contact_info = {
                    1: ["img/globe.png",Websit_value, Websitlinke_value],
                    2: ["img/x-logo.png", x_value, xlink_value],
                    3: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    else:
        contact_info = {
                    1: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    add=0
    a=0
    # Iterate over contact info
    for key, value in contact_info.items():
        # Add text annotation with URL as a tooltip
        img_path = value[0]
        img = plt.imread(img_path)
        # Calculate the scaling factor
        zoom = 4 / max(img.shape[:2])
        imagebox = OffsetImage(img, zoom=zoom)
        ab_image = AnnotationBbox(imagebox, xy=(contact_info_x, contact_info_y-add),xybox=(contact_info_x-0.07, contact_info_y-add),boxcoords='axes fraction', frameon=False)
        ax.add_artist(ab_image)

        ax.annotate(value[1], xy=(contact_info_x, contact_info_y-add), xytext=(contact_info_x, contact_info_y-add),
                                textcoords='axes fraction', ha='center', va='center',
                                fontsize=6, color=contact_info_color, fontproperties=FontProperties(fname=font_path),url=value[2])
        add = add+0.035
        a= a+20
    # # Use textwrap to break the text into multiple lines
    if (body_alt):
        certificate_body = body_values.get("AltText")

    # Split the wrapped text into individual lines
    body_lines = util.break_string_into_chunks(certificate_body, 58)
    y_position = body_y
    for line in body_lines:
        ax.text(body_x, y_position, get_display(reshape(line)), fontsize=font_size, color= body_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
        y_position -= 0.06 # Move to the next line
    
    # Add the text to the figure
    if (intro_alt):
        ax.text(intro_x, intro_y,get_display(reshape(intro_alt)), fontsize=font_size, color= intro_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(intro_x, intro_y,get_display(reshape(certificate_intro)), fontsize=font_size, color= intro_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (title_alt):
        ax.text(title_x, title_y,get_display(reshape(title_alt)) ,fontsize=font_size, color=title_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(title_x, title_y,get_display(reshape(recipient_title)) ,fontsize=font_size, color=title_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (name_alt):
        ax.text(name_x, name_y,get_display(reshape(name_alt)) ,fontsize=font_size, color=name_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    elif lang== "en":
        ax.text(name_x, name_y,get_display(reshape("Maha Moahammed Alhamad")) ,fontsize=font_size, color=name_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(name_x, name_y,get_display(reshape(" راكان عبدالصمد العبدالله")) ,fontsize=font_size, color=name_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    # ax.text((145, y_position),male_certificate_body_to_draw, fill='black', font=font)
    # if (signature_1_x != 0.0 and signature_1_y != 0.0) and (signature_1_w != 0.0 and signature_1_h != 0.0):
    img = plt.imread(path_to_dean_signature)
            # Calculate the scaling factor
    zoom = 35 / max(img.shape[:2])
    imagebox = OffsetImage(img, zoom=zoom)
    ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(signature_1_x, signature_1_y+0.07),boxcoords='axes fraction', frameon=False)
    ax.add_artist(ab_image)
        # Define the coordinates for the line as axes fraction
    x1, y1 = signature_1_x-0.1, signature_1_y+0.05 # Starting point
    x2, y2 = signature_1_x+0.1, signature_1_y+0.05# Ending point

        # Draw the line
    ax.plot([x1, x2], [y1, y2], color='black', linewidth=0.3, transform=ax.transAxes)
    if (signature_1_alt):
        ax.text(signature_1_x,  signature_1_y-0.04,get_display(reshape(signature_1_alt)), fontsize=6, color=signature_1_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(signature_1_x,  signature_1_y,get_display(reshape(dean_position)) , fontsize=6, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(signature_1_x,  signature_1_y-0.04,get_display(reshape(dean_name)), fontsize=6, color=signature_1_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(signature_1_x,  signature_1_y,get_display(reshape(dean_position)) , fontsize=6, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        
    if (signature_2_x == 0.01 and signature_2_y == 0.01) and (signature_2_w == 0.01 and signature_2_h == 0.01):
      print("signature 2 hidden")
    else:
        img = plt.imread(path_to_csu_head_signature)
                # Calculate the scaling factor
        zoom = 35 / max(img.shape[:2])
        imagebox = OffsetImage(img, zoom=zoom)
        ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(signature_2_x, signature_2_y+0.07),boxcoords='axes fraction', frameon=False)
        ax.add_artist(ab_image)
        # Define the coordinates for the line as axes fraction
        x11, y11 = signature_2_x-0.1, signature_2_y+0.05 # Starting point
        x22, y22 = signature_2_x+0.1,signature_2_y+0.05  # Ending point

        # Draw the line
        ax.plot([x11, x22], [y11, y22], color='black', linewidth=0.3, transform=ax.transAxes)
        if (signature_2_alt):
            ax.text(signature_2_x,  signature_2_y-0.04,get_display(reshape(signature_2_alt)), fontsize=6, color=signature_2_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
            ax.text(signature_2_x,  signature_2_y,get_display(reshape(csu_position)) , fontsize=6, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        else:
            ax.text(signature_2_x,  signature_2_y-0.04,get_display(reshape(csu_director_name)), fontsize=6, color=signature_2_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
            ax.text(signature_2_x,  signature_2_y,get_display(reshape(csu_position)) , fontsize=6, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        
    
    if (greeting_alt):
        ax.text(greeting_x,  greeting_y,get_display(reshape(greeting_alt)), fontsize=6, color=greeting_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(greeting_x,  greeting_y,get_display(reshape(greeting_txt)), fontsize=6, color=greeting_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    # Adjust the position of the axes to fill the entire figure
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    static_folder = os.path.join(app.root_path, 'static')
    # Save the figure without any padding as PNG in the static folder
    output_filename = 'generated_image.png'
    output_path = os.path.join(static_folder, output_filename)
    fig.savefig(output_path, dpi=dpi, pad_inches=0, transparent=True)

    # Close the figure to release resources
    plt.close(fig)
    return send_from_directory(os.path.join(app.root_path, 'static'), 'generated_image.png', as_attachment=True)
    

def arimg(temp_id):
    default_data = load_default_bidata()
    # Arabic
    recipient_title=f"{default_data.get('male_recipient_title', 'Default male_recipient_titleText')}"
    certificate_intro=f"{default_data.get('intro', 'Default Intro Text')}"
    certificate_body=f"{default_data.get('male_certificate_body', 'Default male_certificate_body Text')}"
    greeting_txt=f"{default_data.get('male_final_greeting', 'Default male_final_greeting Text')}"

    # English
    recipient_title_en=f"{default_data.get('recipient_title_en', 'Default recipient_title_en Text')}"
    intro_en=f"{default_data.get('intro_en', 'Default Intro_en Text')}"
    certificate_body_en=f"{default_data.get('male_certificate_body_en', 'Default male_certificate_body_en Text')}"
    greeting_txt_en=f"{default_data.get('male_final_greeting_en', 'Default male_final_greeting_en Text')}"

    dean_name=f"{default_data.get('dean_name', 'Default dean_name Text')}"
    dean_position=f"{ default_data.get('dean_position', 'Default dean_position Text')}"
    path_to_dean_signature=f"{default_data.get('path_to_dean_signature', 'Default path_to_dean_signature Text')}"
    csu_director_name=f"{default_data.get('csu_director_name', 'Default csu_director_name Text')}"
    csu_position=f"{ default_data.get('csu_position', 'Default csu_position Text')}"
    path_to_csu_head_signature=f"{default_data.get('path_to_csu_signature', 'Default path_to_csu_signature Text')}"

    template= Template.query.filter_by(template_id=temp_id).first()

    if db_classes.CertificateCustomizations.query.filter_by(template_id=temp_id).first():
        customization = db_classes.CertificateCustomizations.query.filter_by(template_id=temp_id).first().items_positions
    else: 
        with open('./customization/arcustomization.json', 'r') as file:
            customization = json.load(file)
    if customization:
            # Extract values for Certificate_Title
            certificate_intro_values = customization.get("Intro", {})

            intro_x=certificate_intro_values.get("x",0)
            intro_y=certificate_intro_values.get("y",0)
            intro_w=certificate_intro_values.get("w",0)
            intro_h=certificate_intro_values.get("h",0)
            intro_color=certificate_intro_values.get("color","black")

            certificate_intro_en_values = customization.get("Intro_en", {})
            intro_x_en=certificate_intro_en_values.get("x",0)
            intro_y_en=certificate_intro_en_values.get("y",0)
            intro_w_en=certificate_intro_en_values.get("w",0)
            intro_color_en=certificate_intro_en_values.get("color","black")

            recipient_title_values = customization.get("recipient_title", {})
            title_x=recipient_title_values.get("x",0)
            title_y=recipient_title_values.get("y",0)
            title_w=recipient_title_values.get("w",0)
            title_h=recipient_title_values.get("h",0)
            title_color=recipient_title_values.get("color","black")

            recipient_title_values_en = customization.get("recipient_title_en", {})
            title_x_en=recipient_title_values_en.get("x",0)
            title_y_en=recipient_title_values_en.get("y",0)
            title_w_en=recipient_title_values_en.get("w",0)
            title_color_en=recipient_title_values_en.get("color","black")

            recipient_name_values = customization.get("recipient_name", {})
            name_x=recipient_name_values.get("x",0)
            name_y=recipient_name_values.get("y",0) 
            name_w=recipient_name_values.get("w",0)
            name_h=recipient_name_values.get("h",0)
            name_color=recipient_name_values.get("color","black")


            recipient_name_values_en = customization.get("recipient_name_en", {})
            name_x_en=recipient_name_values_en.get("x",0)
            name_y_en=recipient_name_values_en.get("y",0) 
            name_w_en=recipient_name_values_en.get("w",0)
            name_color_en=recipient_name_values_en.get("color","black")

            body_values = customization.get("body", {})
            body_x=body_values.get("x",0)
            body_y=body_values.get("y",0)
            body_w=body_values.get("w",0)
            body_h=body_values.get("h",0)
            body_color=body_values.get("color","black")


            body_values_en = customization.get("body_en", {})
            body_x_en=body_values_en.get("x",0)
            body_y_en=body_values_en.get("y",0)
            body_w_en=body_values_en.get("w",0)
            body_color_en=body_values_en.get("color","black")


            final_greeting_values = customization.get("final_greeting", {})

            final_greeting_values_en = customization.get("final_greeting_en", {})
            greeting_x=final_greeting_values.get("x",0)
            greeting_x_en=final_greeting_values_en.get("x",0)
            greeting_y=final_greeting_values.get("y",0)
            greeting_y_en=final_greeting_values_en.get("y",0)
            greeting_color_en=final_greeting_values_en.get("color","black")
            greeting_color=final_greeting_values.get("color","black")


            contact_info_values = customization.get("contact_info", {})
            contact_info_x=contact_info_values.get("x",0)
            contact_info_y=contact_info_values.get("y",0)
            contact_info_color=contact_info_values.get("color","black")
            Websit_value = contact_info_values.get("contact", {}).get("Web", {}).get("Websit", "")
            Websitlinke_value = contact_info_values.get("contact", {}).get("Web", {}).get("Websitlinke", "")
            x_value = contact_info_values.get("contact", {}).get("X", {}).get("X", "")
            xlink_value = contact_info_values.get("contact", {}).get("X", {}).get("Xlink", "")

            signature_1_values =customization.get("signature_1", {})
            signature_1_x = signature_1_values.get("x",0)
            signature_1_y = signature_1_values.get("y",0)
            signature_1_w = signature_1_values.get("w",0)
            signature_1_h = signature_1_values.get("h",0)
            signature_1_color = signature_1_values.get("color","black")

            signature_2_values =customization.get("signature_2", {})
            signature_2_x = signature_2_values.get("x",0)
            signature_2_y = signature_2_values.get("y",0)
            signature_2_w = signature_2_values.get("w",0)
            signature_2_h = signature_2_values.get("h",0)
            signature_2_color = signature_2_values.get("color","black")
    dpi = 300
    # img = mpimg.imread(template.template_image ,format='RGBA')
    pil_img = Image.open(template.template_image)# Convert float image to uint8

    # # Resize the image to fit A4 landscape dimensions
    resized_img = pil_img.resize(size=(1122,793))
    matplotlib.rcParams['pdf.fonttype'] = 42 
   
    # Create a figure with A4 landscape dimensions
    fig_width = 3.74
    fig_height = 2.64 
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), frameon=False)
    # Display the resized image without axes and stretching it to fill the entire figure
    ax.imshow(resized_img, aspect='auto')

    # Turn off axis
    ax.axis('off')

    # Specify the path to your custom Arabic font
    font_path = os.path.abspath('fonts/SakkalMajalla/majallab.ttf')
    font_path2 = os.path.abspath('fonts/Amiri/Amiri-Regular.ttf')
    font_size = 5 # Font size

    if (x_value and xlink_value ) and not (Websit_value and Websitlinke_value):
         contact_info = {
                1: ["img/x-logo.png", x_value, xlink_value],
                2: ["img/checkmark.png", "ggGBs2hu9j", None]
                }
    elif (Websit_value and Websitlinke_value) and not (x_value and xlink_value ) :
        contact_info = {
                    1: ["img/globe.png",Websit_value, Websitlinke_value],
                    2: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    elif (Websit_value and Websitlinke_value) and (x_value and xlink_value):
        contact_info = {
                    1: ["img/globe.png",Websit_value, Websitlinke_value],
                    2: ["img/x-logo.png", x_value, xlink_value],
                    3: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    else:
        contact_info = {
                    1: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    add=0
    a=0
    # Iterate over contact info
    for key, value in contact_info.items():
        # Add text annotation with URL as a tooltip
        img_path = value[0]
        img = plt.imread(img_path)
        # Calculate the scaling factor
        zoom = 4 / max(img.shape[:2])
        imagebox = OffsetImage(img, zoom=zoom)
        ab_image = AnnotationBbox(imagebox, xy=(contact_info_x, contact_info_y-add),xybox=(contact_info_x-0.07, contact_info_y-add),boxcoords='axes fraction', frameon=False)
        ax.add_artist(ab_image)

        ax.annotate(value[1], xy=(contact_info_x, contact_info_y-add), xytext=(contact_info_x,contact_info_y-add),
                                textcoords='axes fraction', ha='center', va='center',
                                fontsize=6, color=contact_info_color, fontproperties=FontProperties(fname=font_path),url=value[2])
        add = add+0.035
        a= a+20
    if (body_values.get("AltText")):
        certificate_body = body_values.get("AltText")

    body_lines = util.break_string_into_chunks(certificate_body, 58)
    y_position = body_y
    for line in body_lines:
        ax.text(body_x, y_position, get_display(reshape(line)), fontsize=font_size, color= body_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
        y_position -= 0.06

    if (body_values_en.get("AltText")):
        certificate_body_en = body_values_en.get("AltText")

    body_lines = util.break_string_into_chunks(certificate_body_en, 60)
    y_position = body_y_en
    for line in body_lines:
        ax.text(body_x_en, y_position, get_display(reshape(line)), fontsize=font_size, color= body_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
        y_position -= 0.05
    
    if (certificate_intro_values.get("AltText")):
        ax.text(intro_x,intro_y,get_display(reshape(certificate_intro_values.get("AltText"))), fontsize=font_size, color=intro_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(intro_x,intro_y,get_display(reshape(certificate_intro)), fontsize=font_size, color= intro_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (certificate_intro_en_values.get("AltText")):
        ax.text(intro_x_en,intro_y_en,get_display(reshape(certificate_intro_en_values.get("AltText"))), fontsize=font_size, color=intro_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(intro_x_en,intro_y_en,get_display(reshape(intro_en)), fontsize=font_size, color= intro_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    

    if (recipient_title_values.get("AltText")):
        ax.text(title_x, title_y ,get_display(reshape(recipient_title_values.get("AltText"))) ,fontsize=font_size, color=title_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(title_x, title_y ,get_display(reshape(recipient_title)) ,fontsize=font_size, color=title_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    if (recipient_title_values_en.get("AltText")):
        ax.text(title_x_en, title_y_en ,get_display(reshape(recipient_title_values_en.get("AltText"))) ,fontsize=font_size, color=title_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(title_x_en, title_y_en ,get_display(reshape(recipient_title_en)) ,fontsize=font_size, color=title_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    

    if (recipient_name_values.get("AltText")):
        ax.text(name_x, name_y ,get_display(reshape(recipient_name_values.get("AltText"))) ,fontsize=font_size, color=name_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(name_x, name_y ,get_display(reshape(" راكان عبدالصمد العبدالله")) ,fontsize=font_size, color=name_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    if (recipient_name_values_en.get("AltText")):
        ax.text(name_x_en, name_y_en ,get_display(reshape(recipient_name_values_en.get("AltText"))) ,fontsize=font_size, color=name_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(name_x_en, name_y_en ,get_display(reshape("Sumaiah Nassir Alnassir")) ,fontsize=font_size, color=name_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (final_greeting_values.get("AltText")):
        ax.text(greeting_x, greeting_y ,get_display(reshape(final_greeting_values.get("AltText"))), fontsize=6, color=greeting_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(greeting_x, greeting_y,get_display(reshape(greeting_txt)), fontsize=font_size, color=greeting_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    if (final_greeting_values_en.get("AltText")):
        ax.text(greeting_x_en, greeting_y_en ,get_display(reshape(final_greeting_values_en.get("AltText"))), fontsize=6, color=greeting_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(greeting_x_en, greeting_y_en,get_display(reshape(greeting_txt_en)), fontsize=font_size, color=greeting_color_en, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    # if (signature_1_x != 0.0 and signature_1_y != 0.0) and (signature_1_w != 0.0 and signature_1_h != 0.0):
    img = plt.imread(path_to_dean_signature)
            # Calculate the scaling factor
    zoom = 35 / max(img.shape[:2])
    imagebox = OffsetImage(img, zoom=zoom)
    ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(signature_1_x, signature_1_y+0.07),boxcoords='axes fraction', frameon=False)
    ax.add_artist(ab_image)
    # Define the coordinates for the line as axes fraction
    x1, y1 = signature_1_x-0.1, signature_1_y+0.05 # Starting point
    x2, y2 = signature_1_x+0.1, signature_1_y+0.05# Ending point

        # Draw the line
    ax.plot([x1, x2], [y1, y2], color='black', linewidth=0.3, transform=ax.transAxes)
    if (signature_1_values.get("AltText")):
        ax.text(signature_1_x,  signature_1_y-0.04,get_display(reshape(signature_1_values.get("AltText"))), fontsize=font_size, color=signature_1_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(signature_1_x,  signature_1_y,get_display(reshape(dean_position)) , fontsize=font_size, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(signature_1_x,  signature_1_y-0.04,get_display(reshape(dean_name)), fontsize=font_size, color=signature_1_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(signature_1_x,  signature_1_y,get_display(reshape(dean_position)) , fontsize=font_size, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        
    if (signature_2_x == 0.01 and signature_2_y == 0.01) and (signature_2_w == 0.01 and signature_2_h == 0.01):
        print("signature 2 hidden")
    else:
        img = plt.imread(path_to_csu_head_signature)
                # Calculate the scaling factor
        zoom = 35 / max(img.shape[:2])
        imagebox = OffsetImage(img, zoom=zoom)
        ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(signature_2_x,signature_2_y+0.07),boxcoords='axes fraction', frameon=False)
        ax.add_artist(ab_image)
        # Define the coordinates for the line as axes fraction
        x11, y11 = signature_2_x-0.1, signature_2_y+0.05 # Starting point
        x22, y22 = signature_2_x+0.1,signature_2_y+0.05  # Ending point

        # Draw the line
        ax.plot([x11, x22], [y11, y22], color='black', linewidth=0.3, transform=ax.transAxes)
        if (signature_2_values.get("AltText")):
            ax.text(signature_2_x,  signature_2_y-0.04,get_display(reshape(signature_2_values.get("AltText"))), fontsize=font_size, color=signature_2_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
            ax.text(signature_2_x,  signature_2_y,get_display(reshape(csu_position)) , fontsize=font_size, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        else:
            ax.text(signature_2_x,  signature_2_y-0.04,get_display(reshape(csu_director_name)), fontsize=font_size, color=signature_2_color, ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
            ax.text(signature_2_x,  signature_2_y,get_display(reshape(csu_position)) , fontsize=font_size, color="black", ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    static_folder = os.path.join(app.root_path, 'static')
    # Save the figure without any padding as PNG in the static folder
    output_filename = 'generated_image.png'
    output_path = os.path.join(static_folder, output_filename)
    fig.savefig(output_path, dpi=dpi, pad_inches=0, transparent=True)

    # # Close the figure to release resources
    plt.close(fig)
    return send_from_directory(os.path.join(app.root_path, 'static'), 'generated_image.png', as_attachment=True)