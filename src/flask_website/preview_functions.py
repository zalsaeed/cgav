import os
from flask import send_from_directory
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


app = db_connection.app
db = db_connection.db
bcrypt = db_connection.bcrypt





def load_default_data():
    with open(os.path.abspath('events/sample-event.yaml'), 'r') as file:
        default_data = yaml.safe_load(file)
    return default_data

def img(temp_id):
    customization = db_classes.CertificateCustomizations.query.filter_by(template_id=temp_id).first()
    default_data = load_default_data() #load sampl recepent information form yml file 
    template= Template.query.filter_by(template_id=temp_id).first()
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

    #assign each information in yml to varabile and make it as string 
    event_title = default_data.get('event_title', 'Default Title')
    event_intro = default_data.get('intro', 'Default Intro Text')
    male_recipient_title= default_data.get('male_recipient_title', 'Default male_recipient_titleText')
    male_certificate_body = default_data.get('male_certificate_body', 'Default male_certificate_body Text')
    dean_name = default_data.get('dean_name', 'Default dean_name Text')
    dean_position = default_data.get('dean_position', 'Default dean_position Text')
    path_to_dean_signature = default_data.get('path_to_dean_signature', 'Default path_to_dean_signature Text')
    csu_name = default_data.get('csu_director_name', 'Default csu_director_name Text')
    csu_position = default_data.get('csu_position', 'Default csu_position Text')
    path_to_csu_signature = default_data.get('path_to_csu_signature', 'Default path_to_csu_signature Text')
    male_final_greeting = default_data.get('male_final_greeting', 'Default male_final_greeting Text')
    event_intro_to_draw = f"{event_intro}"
    male_recipient_title_to_draw = f"{male_recipient_title}"
    male_certificate_body_to_draw = f"{male_certificate_body}"
    dean_name_to_draw = f"{dean_name}"
    dean_position_to_draw = f"{dean_position}"
    dean_signature_to_draw = f"{path_to_dean_signature}"
    csu_name_to_draw = f"{csu_name}"
    csu_position_to_draw = f"{csu_position}"
    csu_signature_to_draw = f"{path_to_csu_signature}"
    male_final_greeting_to_draw = f"{male_final_greeting}"
    if (customization.items_positions['contact_info']['contact']['X'].get("X") and customization.items_positions['contact_info']['contact']['X'].get("Xlink") ) and not (customization.items_positions['contact_info']['contact']['Web'].get("Websit") and customization.items_positions['contact_info']['contact']['Web'].get("Websitlinke")):
         contact_info = {
                1: ["img/x-logo.png", customization.items_positions['contact_info']['contact']['X'].get("X"), customization.items_positions['contact_info']['contact']['X'].get("Xlink")],
                2: ["img/checkmark.png", "ggGBs2hu9j", None]
                }
    elif (customization.items_positions['contact_info']['contact']['Web'].get("Websit") and customization.items_positions['contact_info']['contact']['Web'].get("Websitlinke")) and not (customization.items_positions['contact_info']['contact']['X'].get("X") and customization.items_positions['contact_info']['contact']['X'].get("Xlink") ) :
        contact_info = {
                    1: ["img/globe.png",customization.items_positions['contact_info']['contact']['Web'].get("Websit"), customization.items_positions['contact_info']['contact']['Web'].get("Websitlinke")],
                    2: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    elif (customization.items_positions['contact_info']['contact']['Web'].get("Websit") and customization.items_positions['contact_info']['contact']['Web'].get("Websitlinke")) and (customization.items_positions['contact_info']['contact']['X'].get("X") and customization.items_positions['contact_info']['contact']['X'].get("Xlink") ):
        contact_info = {
                    1: ["img/globe.png",customization.items_positions['contact_info']['contact']['Web'].get("Websit"), customization.items_positions['contact_info']['contact']['Web'].get("Websitlinke")],
                    2: ["img/x-logo.png", customization.items_positions['contact_info']['contact']['X'].get("X"), customization.items_positions['contact_info']['contact']['X'].get("Xlink")],
                    3: ["img/checkmark.png", "ggGBs2hu9j", None]
                    }
    else:
        # contact_info = {
        #             1: ["img/globe.png", "coc.qu.edu.sa", "https://coc.qu.edu.sa"],
        #             2: ["img/x-logo.png", "@coc_qu_sa", "https://twitter.com/coc_qu_sa"],
        #             3: ["img/checkmark.png", "ggGBs2hu9j", None]
        #             }
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
        ab_image = AnnotationBbox(imagebox, xy=(customization.items_positions["contact_info"].get("x",0), customization.items_positions["contact_info"].get("y",0)-add),xybox=(customization.items_positions["contact_info"].get("x",0)-0.07, customization.items_positions["contact_info"].get("y",0)-add),boxcoords='axes fraction', frameon=False)
        ax.add_artist(ab_image)

        ax.annotate(value[1], xy=(customization.items_positions["contact_info"].get("x",0), customization.items_positions["contact_info"].get("y",0)-add), xytext=(customization.items_positions["contact_info"].get("x",0), customization.items_positions["contact_info"].get("y",0)-add),
                                textcoords='axes fraction', ha='center', va='center',
                                fontsize=6, color=customization.items_positions["contact_info"].get("color"), fontproperties=FontProperties(fname=font_path),url=value[2])
        add = add+0.035
        a= a+20
    # # Use textwrap to break the text into multiple lines
    max_line_length = 58
    if (customization.items_positions["body"].get("AltText")):
        wrapped_text = textwrap.fill(customization.items_positions["body"].get("AltText"), width=max_line_length)
    else:
        wrapped_text = textwrap.fill(male_certificate_body_to_draw, width=max_line_length)

    # Split the wrapped text into individual lines
    body_lines = wrapped_text.split('\n')
    # # Draw each line of the wrapped text
    y_position = customization.items_positions["body"].get("y",0)
    for line in body_lines:
        ax.text(customization.items_positions["body"].get("x",0), y_position, get_display(reshape(line)), fontsize=font_size, color= customization.items_positions["body"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
        y_position -= 0.06 # Move to the next line
    
   

    # Add the text to the figure
    # ax.text(text_x, text_y, get_display(reshape(text)), fontsize=font_size, color='black', ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
        # write text inside image with x,y positions 
    if (customization.items_positions["Intro"].get("AltText")):
        ax.text(customization.items_positions["Intro"].get("x",0), customization.items_positions["Intro"].get("y",0),get_display(reshape(customization.items_positions["Intro"].get("AltText"))), fontsize=font_size, color= customization.items_positions["Intro"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(customization.items_positions["Intro"].get("x",0), customization.items_positions["Intro"].get("y",0),get_display(reshape(event_intro_to_draw)), fontsize=font_size, color= customization.items_positions["Intro"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (customization.items_positions["recipient_title"].get("AltText")):
        ax.text(customization.items_positions["recipient_title"].get("x",0), customization.items_positions["recipient_title"].get("y",0),get_display(reshape(customization.items_positions["recipient_title"].get("AltText"))) ,fontsize=font_size, color=customization.items_positions["recipient_title"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(customization.items_positions["recipient_title"].get("x",0), customization.items_positions["recipient_title"].get("y",0),get_display(reshape(male_recipient_title_to_draw)) ,fontsize=font_size, color=customization.items_positions["recipient_title"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    
    if (customization.items_positions["recipient_name"].get("AltText")):
        ax.text(customization.items_positions["recipient_name"].get("x",0), customization.items_positions["recipient_name"].get("y",0),get_display(reshape(customization.items_positions["recipient_name"].get("AltText"))) ,fontsize=font_size, color=customization.items_positions["recipient_name"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    else:
        ax.text(customization.items_positions["recipient_name"].get("x",0), customization.items_positions["recipient_name"].get("y",0),get_display(reshape(" راكان عبدالصمد العبدالله")) ,fontsize=font_size, color=customization.items_positions["recipient_name"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path))
    # ax.text((145, y_position),male_certificate_body_to_draw, fill='black', font=font)
    img = plt.imread(dean_signature_to_draw)
        # Calculate the scaling factor
    zoom = 35 / max(img.shape[:2])
    imagebox = OffsetImage(img, zoom=zoom)
    ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(customization.items_positions["signature_1"].get("x",0), customization.items_positions["signature_1"].get("y",0)+0.07),boxcoords='axes fraction', frameon=False)
    ax.add_artist(ab_image)
    # Define the coordinates for the line as axes fraction
    x1, y1 = customization.items_positions["signature_1"].get("x",0)-0.1, customization.items_positions["signature_1"].get("y",0)+0.05 # Starting point
    x2, y2 = customization.items_positions["signature_1"].get("x",0)+0.1, customization.items_positions["signature_1"].get("y",0)+0.05# Ending point

    # Draw the line
    ax.plot([x1, x2], [y1, y2], color='black', linewidth=0.3, transform=ax.transAxes)
    if (customization.items_positions["signature_1"].get("AltText")):
        ax.text(customization.items_positions["signature_1"].get("x",0),  customization.items_positions["signature_1"].get("y",0)-0.04,get_display(reshape(customization.items_positions["signature_1"].get("AltText"))), fontsize=6, color=customization.items_positions["signature_1"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(customization.items_positions["signature_1"].get("x",0),  customization.items_positions["signature_1"].get("y",0),get_display(reshape(dean_position_to_draw)) , fontsize=6, color=customization.items_positions["signature_1"].get("colorpostion"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(customization.items_positions["signature_1"].get("x",0),  customization.items_positions["signature_1"].get("y",0)-0.04,get_display(reshape(dean_name_to_draw)), fontsize=6, color=customization.items_positions["signature_1"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(customization.items_positions["signature_1"].get("x",0),  customization.items_positions["signature_1"].get("y",0),get_display(reshape(dean_position_to_draw)) , fontsize=6, color=customization.items_positions["signature_1"].get("colorpostion"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    
    img = plt.imread(csu_signature_to_draw)
            # Calculate the scaling factor
    zoom = 35 / max(img.shape[:2])
    imagebox = OffsetImage(img, zoom=zoom)
    ab_image = AnnotationBbox(imagebox, xy=(1,1),xybox=(customization.items_positions["signature_2"].get("x",0), customization.items_positions["signature_2"].get("y",0)+0.07),boxcoords='axes fraction', frameon=False)
    ax.add_artist(ab_image)
    # Define the coordinates for the line as axes fraction
    x11, y11 = customization.items_positions["signature_2"].get("x",0)-0.1, customization.items_positions["signature_2"].get("y",0)+0.05 # Starting point
    x22, y22 = customization.items_positions["signature_2"].get("x",0)+0.1,customization.items_positions["signature_2"].get("y",0)+0.05  # Ending point

    # Draw the line
    ax.plot([x11, x22], [y11, y22], color='black', linewidth=0.3, transform=ax.transAxes)
    if (customization.items_positions["signature_2"].get("AltText")):
        ax.text(customization.items_positions["signature_2"].get("x",0),  customization.items_positions["signature_2"].get("y",0)-0.04,get_display(reshape(customization.items_positions["signature_2"].get("AltText"))), fontsize=6, color=customization.items_positions["signature_2"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(customization.items_positions["signature_2"].get("x",0),  customization.items_positions["signature_2"].get("y",0),get_display(reshape(csu_position_to_draw)) , fontsize=6, color=customization.items_positions["signature_2"].get("colorpostion"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(customization.items_positions["signature_2"].get("x",0),  customization.items_positions["signature_2"].get("y",0)-0.04,get_display(reshape(csu_name_to_draw)), fontsize=6, color=customization.items_positions["signature_2"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
        ax.text(customization.items_positions["signature_2"].get("x",0),  customization.items_positions["signature_2"].get("y",0),get_display(reshape(csu_position_to_draw)) , fontsize=6, color=customization.items_positions["signature_2"].get("colorpostion"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    if (customization.items_positions["final_greeting"].get("AltText")):
        ax.text(customization.items_positions["final_greeting"].get("x",0),  customization.items_positions["final_greeting"].get("y",0),get_display(reshape(customization.items_positions["final_greeting"].get("AltText"))), fontsize=6, color=customization.items_positions["final_greeting"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    else:
        ax.text(customization.items_positions["final_greeting"].get("x",0),  customization.items_positions["final_greeting"].get("y",0),get_display(reshape(male_final_greeting_to_draw)), fontsize=6, color=customization.items_positions["final_greeting"].get("color"), ha='center', va='center', transform=ax.transAxes,fontproperties=FontProperties(fname=font_path2))
    # Adjust the position of the axes to fill the entire figure
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    static_folder = os.path.join(app.root_path, 'static')
    # Save the figure without any padding as PNG in the static folder
    output_filename = 'generated_image.png'
    output_path = os.path.join(static_folder, output_filename)
    fig.savefig(output_path, dpi=dpi, pad_inches=0, transparent=True)

    # # Save the figure as a PDF file in the static folder
    # output_pdf_filename = 'generated_image.pdf'
    # output_pdf_path = os.path.join(static_folder, output_pdf_filename)
    # fig.savefig(output_pdf_path, format='pdf', dpi=300, bbox_inches='tight', pad_inches=0, metadata={'Title': 'Arabic PDF'})
    # # Close the figure to release resources
    plt.close(fig)
    return send_from_directory(os.path.join(app.root_path, 'static'), 'generated_image.png', as_attachment=True)
    # return render_template('img.html')
