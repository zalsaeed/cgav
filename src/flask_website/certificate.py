import os
import logging
from typing import List, Dict

from PIL import Image
import fpdf  # TODO: why not use fpdf2? (fpdf2==2.7.5) It is the maintained version now!
from arabic_reshaper import reshape
from bidi.algorithm import get_display

import util
import configuration_loader

DEFAULT_FONT = ("SakkalMajalla", 24)

# set where fonts are stored
font_abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fonts'))
fpdf.set_global("SYSTEM_TTFONTS", font_abs_path)
logging.root.info(f"-----------------------------> Fonts dir: {font_abs_path}")


class Certificate:

    def __init__(self, recipient_name: str, recipient_title: str,
                 recipient_email: str, dean_name: str, dean_position: str, path_to_dean_signature: str,
                 csu_director_name: str, csu_position: str, path_to_csu_head_signature: str,
                 certificate_intro: str, certificate_body: str,
                 greeting_txt: str, certificate_template: str, certificate_event_id: int):
        self.log = logging.getLogger(__name__)
        self.recipient_name = recipient_name
        self.recipient_title = recipient_title
        self.recipient_email = recipient_email
        self.dean_name = dean_name
        self.dean_position = dean_position
        self.path_to_dean_signature = path_to_dean_signature
        self.csu_director_name = csu_director_name
        self.csu_position = csu_position
        self.path_to_csu_head_signature = path_to_csu_head_signature
        self.certificate_intro = certificate_intro
        self.certificate_body = certificate_body
        self.greeting_txt = greeting_txt
        self.certificate_template = certificate_template
        # Assign certificate_event_id to self
        self.certificate_event_id = certificate_event_id
        # self.certificate_hash = util.small_hash(self.recipient_email + self.recipient_name)
        self.certificate_hash = util.small_hash(self.recipient_email + self.recipient_name + str(certificate_event_id)) 

        
        # use and A4 in Landscape orientation.
        self.pdf = fpdf.FPDF(orientation='L', unit='mm', format='A4')
        
        # do not allow page breaks
        self.pdf.set_auto_page_break(auto=False)
        
        # add an empty page
        self.pdf.add_page()

        font_settings = configuration_loader.Settings()
        font_settings.read_yaml(open(os.path.abspath("flask_website/fonts-config.yaml")))

        self.log.debug(font_settings['fonts'])
        #src/flask_website/fonts-config.yaml
        # setup fonts, font size, and color
        self.pdf.add_font("NotoSans", style="", fname="fonts/NotoSans/NotoSansArabic-VariableFont_wdth,wght.ttf", uni=True)
        #src/fonts/NotoSans/NotoSansArabic-VariableFont_wdth,wght.ttf
        self.pdf.add_font("Amiri", style="", fname="fonts/Amiri/Amiri-Regular.ttf", uni=True)
        self.pdf.add_font("Amiri", style="I", fname="fonts/Amiri/Amiri-Italic.ttf", uni=True)
        self.pdf.add_font("Amiri", style="B", fname="fonts/Amiri/Amiri-Bold.ttf", uni=True)
        self.pdf.add_font("Amiri", style="BI", fname="fonts/Amiri/Amiri-BoldItalic.ttf", uni=True)

        self.pdf.add_font("SakkalMajalla", style="", fname="fonts/SakkalMajalla/majalla.ttf", uni=True)
        self.pdf.add_font("SakkalMajalla", style="B", fname="fonts/SakkalMajalla/majallab.ttf", uni=True)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])
        self.pdf.set_text_color(0, 0, 0)

        # place the image template over the white page
        # TODO: the template should have its own class where we define all the position for each template
        self.pdf.image(self.certificate_template, x=0, y=0, w=self.pdf.w, h=self.pdf.h)

        # ‘x’ and ‘y’ refer to the specified location on our page
        # ‘w’ and ‘h’ refer to the dimensions of our cell
        # ‘txt’ is the string or number that is to be displayed
        # ‘border’ indicates if a line must be drawn around the cell (0: no, 1: yes or L: left, T: top,
        #       R: right, B: bottom)
        # ‘align’ indicates the alignment of the text (L: left, C: center, R: right)
        # ‘fill’ indicates whether the cell background should be filled or not (True, False).

        """
        An A4 in Landscape orientation has width=297mm and height=210mm.
        The top left corner is the (0,0) point.

           (0,0)+-------------------------+
                |                         |
                |                         |
                |                         |
                |                         |
                |                         |
                |                         |
                +-------------------------+(297,210)

        """

    def certificate_info(self, intro_x: float, intro_y: float, intro_w: float, intro_h: float,
                     name_x: float, name_y: float, name_w: float, name_h: float,
                     title_x: float, title_y: float, title_w: float, title_h: float,
                     body_x: float, body_y: float, body_w: float, body_h: float):
        # intro
        self.pdf.set_xy(intro_x, intro_y)
        self.pdf.cell(intro_w, intro_h, get_display(reshape(self.certificate_intro)), border=0, align="C", fill=False)
        
        # recipient_name
        recipient_name_width = self.pdf.get_string_width(self.recipient_name)
        left_margin_name = (name_w - recipient_name_width) / 2
        self.pdf.set_xy(name_x + left_margin_name, name_y)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="B")
        self.pdf.cell(recipient_name_width, name_h, get_display(reshape(self.recipient_name)), border=0, align="C", fill=False)

        # recipient_title
        recipient_title_width = self.pdf.get_string_width(self.recipient_title)
        left_margin_title = (title_w - recipient_title_width) / 2
        self.pdf.set_xy(title_x + left_margin_title, title_y)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="")
        self.pdf.cell(recipient_title_width, title_h, get_display(reshape(self.recipient_title)), border=0, align="C", fill=False)
        # certificate_body

        body_lines = util.break_string_into_chunks(self.certificate_body, 58)
        for idx, line in enumerate(body_lines):
            self.pdf.set_xy(body_x, body_y + (body_h * idx))
            self.pdf.cell(body_w, body_h, get_display(reshape(line)), border=0, align="C", fill=False)

    def signature_filed(self, x: float, y: float, h: float, w: float, name: str, position: str, signature: str):
        # the dean signature line
        self.pdf.set_font("Amiri", size=10)
        self.pdf.set_xy(x, y)
        self.pdf.cell(w, h, get_display(reshape(position)), border="T", align="C", fill=False)
        self.pdf.set_text_color(5, 168, 172)  # name color (hex = #05a9ac)
        self.pdf.set_xy(x, y+h-5)
        self.pdf.cell(w, h, get_display(reshape(name)), border=0, align="C", fill=False)
        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])

        with Image.open(signature) as img:
            width, height = img.size
            width = width * 0.2645833333  # convert to mm
            height = height * 0.2645833333  # convert to mm
        self.log.debug(f"W:{width}, H:{height}")
        new_height = 15
        new_width = new_height * width / height
        self.pdf.image(signature, x+((w/2)-(new_width/2)), y-12, w=new_width, h=new_height)

    def greeting(self, greeting_txt: str, y: float):
        self.pdf.set_font("Amiri", size=12)
        self.pdf.set_text_color(5, 168, 172)  # text color
        
        greeting_width = self.pdf.get_string_width(self.greeting_txt)
        greeting_x = (self.pdf.w - greeting_width) / 2
        self.pdf.set_xy(greeting_x, y)
        self.pdf.cell(greeting_width, 10, get_display(reshape(self.greeting_txt)), border=0, align="C", fill=False)
        
        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])

    def contact_info(self, contact_info: Dict[int, List[str]], x: float, y: float):
        dim = 5
        self.pdf.set_font("Amiri", size=12)
        self.pdf.set_text_color(5, 168, 172)  # text color

        for key, value in contact_info.items():
            self.pdf.image(value[0], x+1, y+(dim*key)+1, w=dim-1, h=dim-1)
            text_width = self.pdf.get_string_width(value[1])
            self.pdf.set_xy(x+dim, y+(dim*key))
            self.pdf.cell(text_width, dim, value[1], border=0, align="L", fill=False, link=value[2])

        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])
    
    def generate_certificate(self, output_dir: str,get_certificate_customizations):
        customization = get_certificate_customizations
        if customization:
            # Extract values for Certificate_Title
            certificate_intro_values = customization.get("Intro", {})
            intro_x=certificate_intro_values.get("x",0)
            intro_y=certificate_intro_values.get("y",0)
            intro_w=certificate_intro_values.get("w",0)
            intro_h=certificate_intro_values.get("h",0)
            recipient_title_values = customization.get("recipient_title", {})
            title_x=recipient_title_values.get("x",0)
            title_y=recipient_title_values.get("y",0)
            title_w=recipient_title_values.get("w",0)
            title_h=recipient_title_values.get("h",0)
            recipient_name_values = customization.get("recipient_name", {})
            name_x=recipient_name_values.get("x",0)
            name_y=recipient_name_values.get("y",0) 
            name_w=recipient_name_values.get("w",0)
            name_h=recipient_name_values.get("h",0)
            body_values = customization.get("body", {})
            body_x=body_values.get("x",0)
            body_y=body_values.get("y",0)
            body_w=body_values.get("w",0)
            body_h=body_values.get("h",0)
            final_greeting_values = customization.get("final_greeting", {})
            greeting_y=final_greeting_values.get("y",0)
            contact_info_values = customization.get("contact_info", {})
            contact_info_x=contact_info_values.get("x",0)
            contact_info_y=contact_info_values.get("y",0)
            signature_1_values =customization.get("signature_1", {})
            signature_1_x = signature_1_values.get("x",0)
            signature_1_y = signature_1_values.get("y",0)
            signature_1_w = signature_1_values.get("w",0)
            signature_1_h = signature_1_values.get("h",0)
            signature_2_values =customization.get("signature_2", {})
            signature_2_x = signature_2_values.get("x",0)
            signature_2_y = signature_2_values.get("y",0)
            signature_2_w = signature_2_values.get("w",0)
            signature_2_h = signature_2_values.get("h",0)
            self.certificate_info(intro_x, intro_y, intro_w, intro_h,name_x, name_y, name_w, name_h,
                              title_x, title_y, title_w, title_h,
                              body_x, body_y, body_w, body_h)
            if (signature_1_x >0 and signature_1_y >0 and signature_1_w >0):
                self.signature_filed(signature_1_x, signature_1_y, signature_1_h, signature_1_w, self.dean_name, self.dean_position,
                             self.path_to_dean_signature)
            # Second signature - process only if the path is provided
            if (self.path_to_csu_head_signature is not None)and (signature_2_x >0 and signature_2_y>0 and signature_2_w >0):
                self.signature_filed(signature_2_x, signature_2_y,signature_2_h, signature_2_w, self.csu_director_name, self.csu_position,
                                self.path_to_csu_head_signature)
            
            self.greeting(self.greeting_txt, greeting_y)
            contact_info_dict = {
                1: ["img/globe.png", "coc.qu.edu.sa", "https://coc.qu.edu.sa"],
                2: ["img/x-logo.png", "@coc_qu_sa", "https://twitter.com/coc_qu_sa"],
                3: ["img/checkmark.png", self.certificate_hash, ""]
                }
            self.contact_info(contact_info_dict, contact_info_x, contact_info_y)
            
            self.log.debug(f"Hash: '{self.certificate_hash}'")
            util.make_sure_path_exists(output_dir)
            self.pdf.output(f"{output_dir}/{self.recipient_email}-{self.certificate_hash}.pdf")
            self.pdf.close()
        else:
             print("erorr")


class BilingualCertificate:

    def __init__(self, recipient_name: str, recipient_name_en: str,recipient_title: str, recipient_title_en: str,
                 recipient_email: str, dean_name: str, dean_position: str, path_to_dean_signature: str,
                 csu_director_name: str, csu_position: str, path_to_csu_head_signature: str,
                 certificate_intro: str, intro_en: str, certificate_body: str,certificate_body_en: str,
                 greeting_txt: str,greeting_txt_en: str, certificate_template: str, certificate_event_id: int):
        
        self.log = logging.getLogger(__name__)
        self.recipient_name = recipient_name
        self.recipient_title = recipient_title
        self.recipient_email = recipient_email
        self.dean_name = dean_name
        self.dean_position = dean_position
        self.path_to_dean_signature = path_to_dean_signature
        self.csu_director_name = csu_director_name
        self.csu_position = csu_position
        self.path_to_csu_head_signature = path_to_csu_head_signature
        self.certificate_intro = certificate_intro
        self.certificate_body = certificate_body
        self.greeting_txt = greeting_txt
        self.certificate_template = certificate_template
        # Assign certificate_event_id to self
        self.certificate_event_id = certificate_event_id
        # self.certificate_hash = util.small_hash(self.recipient_email + self.recipient_name)
        self.certificate_hash = util.small_hash(self.recipient_email + self.recipient_name + str(certificate_event_id)) 

        # English 
        self.recipient_name_en = recipient_name_en
        self.recipient_title_en = recipient_title_en
        self.intro_en = intro_en
        self.certificate_body_en = certificate_body_en
        self.greeting_txt_en = greeting_txt_en
        
        # use and A4 in Landscape orientation.
        self.pdf = fpdf.FPDF(orientation='L', unit='mm', format='A4')
        
        # do not allow page breaks
        self.pdf.set_auto_page_break(auto=False)
        
        # add an empty page
        self.pdf.add_page()

        font_settings = configuration_loader.Settings()
        font_settings.read_yaml(open(os.path.abspath("flask_website/fonts-config.yaml")))

        self.log.debug(font_settings['fonts'])
        #src/flask_website/fonts-config.yaml
        # setup fonts, font size, and color
        self.pdf.add_font("NotoSans", style="", fname="fonts/NotoSans/NotoSansArabic-VariableFont_wdth,wght.ttf", uni=True)
        #src/fonts/NotoSans/NotoSansArabic-VariableFont_wdth,wght.ttf
        self.pdf.add_font("Amiri", style="", fname="fonts/Amiri/Amiri-Regular.ttf", uni=True)
        self.pdf.add_font("Amiri", style="I", fname="fonts/Amiri/Amiri-Italic.ttf", uni=True)
        self.pdf.add_font("Amiri", style="B", fname="fonts/Amiri/Amiri-Bold.ttf", uni=True)
        self.pdf.add_font("Amiri", style="BI", fname="fonts/Amiri/Amiri-BoldItalic.ttf", uni=True)

        self.pdf.add_font("SakkalMajalla", style="", fname="fonts/SakkalMajalla/majalla.ttf", uni=True)
        self.pdf.add_font("SakkalMajalla", style="B", fname="fonts/SakkalMajalla/majallab.ttf", uni=True)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])
        self.pdf.set_text_color(0, 0, 0)

        # place the image template over the white page
        # TODO: the template should have its own class where we define all the position for each template
        self.pdf.image(self.certificate_template, x=0, y=0, w=self.pdf.w, h=self.pdf.h)

        # ‘x’ and ‘y’ refer to the specified location on our page
        # ‘w’ and ‘h’ refer to the dimensions of our cell
        # ‘txt’ is the string or number that is to be displayed
        # ‘border’ indicates if a line must be drawn around the cell (0: no, 1: yes or L: left, T: top,
        #       R: right, B: bottom)
        # ‘align’ indicates the alignment of the text (L: left, C: center, R: right)
        # ‘fill’ indicates whether the cell background should be filled or not (True, False).

        """
        An A4 in Landscape orientation has width=297mm and height=210mm.
        The top left corner is the (0,0) point.

           (0,0)+-------------------------+
                |                         |
                |                         |
                |                         |
                |                         |
                |                         |
                |                         |
                +-------------------------+(297,210)

        """

    def certificate_info(self, 
                     intro_x: float, intro_y: float, intro_w: float, intro_h: float,
                     intro_x_en: float, intro_y_en: float, intro_w_en: float, intro_h_en: float,

                     name_x: float, name_y: float, name_w: float, name_h: float,
                     name_x_en: float, name_y_en: float, name_w_en: float, name_h_en: float,

                     title_x: float, title_y: float, title_w: float, title_h: float,
                     title_x_en: float, title_y_en: float, title_w_en: float, title_h_en: float,

                     body_x: float, body_y: float, body_w: float, body_h: float,
                     body_x_en: float, body_y_en: float, body_w_en: float, body_h_en: float
                     
                     ):
        # intro
        self.pdf.set_xy(intro_x, intro_y)
        self.pdf.cell(intro_w, intro_h, get_display(reshape(self.certificate_intro)), border=0, align="C", fill=False)
        
        # intro_en
        self.pdf.set_xy(intro_x_en, intro_y_en)
        self.pdf.cell(intro_w_en, intro_h_en, get_display(reshape(self.intro_en)), border=0, align="C", fill=False)
        

        # recipient_name
        recipient_name_width = self.pdf.get_string_width(self.recipient_name)
        left_margin_name = (name_w - recipient_name_width) / 2
        self.pdf.set_xy(name_x + left_margin_name, name_y)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="B")
        self.pdf.cell(recipient_name_width, name_h, get_display(reshape(self.recipient_name)), border=0, align="C", fill=False)

        # recipient_name_en
        recipient_name_width_en = self.pdf.get_string_width(self.recipient_name_en)
        left_margin_name_en = (name_w_en - recipient_name_width_en) / 2
        self.pdf.set_xy(name_x_en + left_margin_name_en, name_y_en)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="B")
        self.pdf.cell(recipient_name_width_en, name_h_en, get_display(reshape(self.recipient_name_en)), border=0, align="C", fill=False)


        # recipient_title
        recipient_title_width = self.pdf.get_string_width(self.recipient_title)
        left_margin_title = (title_w - recipient_title_width) / 2
        self.pdf.set_xy(title_x + left_margin_title, title_y)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="")
        self.pdf.cell(recipient_title_width, title_h, get_display(reshape(self.recipient_title)), border=0, align="C", fill=False)
       
        # recipient_title_en
        recipient_title_width_en = self.pdf.get_string_width(self.recipient_title_en)
        left_margin_title_en = (title_w_en - recipient_title_width_en) / 2
        self.pdf.set_xy(title_x_en + left_margin_title_en, title_y_en)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="")
        self.pdf.cell(recipient_title_width_en, title_h_en, get_display(reshape(self.recipient_title_en)), border=0, align="C", fill=False)
       
        # certificate_body
        body_lines = util.break_string_into_chunks(self.certificate_body, 58)
        for idx, line in enumerate(body_lines):
            self.pdf.set_xy(body_x, body_y + (body_h * idx))
            self.pdf.cell(body_w, body_h, get_display(reshape(line)), border=0, align="C", fill=False)
        
        # certificate_body_en
        body_lines_en = util.break_string_into_chunks(self.certificate_body_en, 58)
        for idx, line in enumerate(body_lines_en):
            self.pdf.set_xy(body_x_en, body_y_en + (body_h_en * idx))
            self.pdf.cell(body_w_en, body_h_en, get_display(reshape(line)), border=0, align="C", fill=False)


    def signature_filed(self, x: float, y: float, h: float, w: float, name: str, position: str, signature: str):
        # the dean signature line
        self.pdf.set_font("Amiri", size=10)
        self.pdf.set_xy(x, y)
        self.pdf.cell(w, h, get_display(reshape(position)), border="T", align="C", fill=False)
        self.pdf.set_text_color(5, 168, 172)  # name color (hex = #05a9ac)
        self.pdf.set_xy(x, y+h-5)
        self.pdf.cell(w, h, get_display(reshape(name)), border=0, align="C", fill=False)
        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])

        with Image.open(signature) as img:
            width, height = img.size
            width = width * 0.2645833333  # convert to mm
            height = height * 0.2645833333  # convert to mm
        self.log.debug(f"W:{width}, H:{height}")
        new_height = 15
        new_width = new_height * width / height
        self.pdf.image(signature, x+((w/2)-(new_width/2)), y-12, w=new_width, h=new_height)

    def greeting(self, greeting_txt: str, y: float):
        self.pdf.set_font("Amiri", size=12)
        self.pdf.set_text_color(5, 168, 172)  # text color
        
        greeting_width = self.pdf.get_string_width(self.greeting_txt)
        greeting_x = (self.pdf.w - greeting_width) / 2
        self.pdf.set_xy(greeting_x, y)
        self.pdf.cell(greeting_width, 10, get_display(reshape(self.greeting_txt)), border=0, align="C", fill=False)
        
        greeting_width_en = self.pdf.get_string_width(self.greeting_txt_en)
        greeting_x_en = (self.pdf.w - greeting_width_en) / 2
        self.pdf.set_xy(greeting_x_en, y)
        self.pdf.cell(greeting_width_en, 10, get_display(reshape(self.greeting_txt_en)), border=0, align="C", fill=False)
        
        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])

    def contact_info(self, contact_info: Dict[int, List[str]], x: float, y: float):
        dim = 5
        self.pdf.set_font("Amiri", size=12)
        self.pdf.set_text_color(5, 168, 172)  # text color

        for key, value in contact_info.items():
            self.pdf.image(value[0], x+1, y+(dim*key)+1, w=dim-1, h=dim-1)
            text_width = self.pdf.get_string_width(value[1])
            self.pdf.set_xy(x+dim, y+(dim*key))
            self.pdf.cell(text_width, dim, value[1], border=0, align="L", fill=False, link=value[2])

        self.pdf.set_text_color(0, 0, 0)  # set it back to black
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1])
    
    def generate_certificate(self, output_dir: str,get_certificate_customizations):
        customization = get_certificate_customizations
        if customization:
            # Extract values for Certificate_Title
            certificate_intro_values = customization.get("Intro", {})

            intro_x=certificate_intro_values.get("x",0)
            intro_y=certificate_intro_values.get("y",0)
            intro_w=certificate_intro_values.get("w",0)
            intro_h=certificate_intro_values.get("h",0)

            intro_x_en=certificate_intro_values.get("x",0)
            intro_y_en=certificate_intro_values.get("y",0)
            intro_w_en=certificate_intro_values.get("w",0)
            intro_h_en=certificate_intro_values.get("h",0)

            recipient_title_values = customization.get("recipient_title", {})
            title_x=recipient_title_values.get("x",0)
            title_y=recipient_title_values.get("y",0)
            title_w=recipient_title_values.get("w",0)
            title_h=recipient_title_values.get("h",0)


            recipient_title_values_en = customization.get("recipient_title_en", {})
            title_x_en=recipient_title_values_en.get("x",0)
            title_y_en=recipient_title_values_en.get("y",0)
            title_w_en=recipient_title_values_en.get("w",0)
            title_h_en=recipient_title_values_en.get("h",0)

            recipient_name_values = customization.get("recipient_name", {})
            name_x=recipient_name_values.get("x",0)
            name_y=recipient_name_values.get("y",0) 
            name_w=recipient_name_values.get("w",0)
            name_h=recipient_name_values.get("h",0)

            recipient_name_values_en = customization.get("recipient_name_en", {})
            name_x_en=recipient_name_values_en.get("x",0)
            name_y_en=recipient_name_values_en.get("y",0) 
            name_w_en=recipient_name_values_en.get("w",0)
            name_h_en=recipient_name_values_en.get("h",0)

            body_values = customization.get("body", {})
            body_x=body_values.get("x",0)
            body_y=body_values.get("y",0)
            body_w=body_values.get("w",0)
            body_h=body_values.get("h",0)

            body_values_en = customization.get("body", {})
            body_x_en=body_values_en.get("x",0)
            body_y_en=body_values_en.get("y",0)
            body_w_en=body_values_en.get("w",0)
            body_h_en=body_values_en.get("h",0)

            final_greeting_values = customization.get("final_greeting", {})

            final_greeting_values_en = customization.get("final_greeting_en", {})

            greeting_y=final_greeting_values.get("y",0)
            greeting_y_en=final_greeting_values.get("y",0)

            contact_info_values = customization.get("contact_info", {})
            contact_info_x=contact_info_values.get("x",0)
            contact_info_y=contact_info_values.get("y",0)

            signature_1_values =customization.get("signature_1", {})
            signature_1_x = signature_1_values.get("x",0)
            signature_1_y = signature_1_values.get("y",0)
            signature_1_w = signature_1_values.get("w",0)
            signature_1_h = signature_1_values.get("h",0)
            signature_2_values =customization.get("signature_2", {})
            signature_2_x = signature_2_values.get("x",0)
            signature_2_y = signature_2_values.get("y",0)
            signature_2_w = signature_2_values.get("w",0)
            signature_2_h = signature_2_values.get("h",0)

            self.certificate_info(intro_x, intro_y, intro_w, intro_h,
                              intro_x_en, intro_y_en, intro_w_en, intro_h_en,
                              name_x, name_y, name_w, name_h,
                              name_x_en, name_y_en, name_w_en, name_h_en,
                              title_x, title_y, title_w, title_h,
                              title_x_en, title_y_en, title_w_en, title_h_en,
                              body_x, body_y, body_w, body_h,
                              body_x_en, body_y_en, body_w_en, body_h_en)
            
            if (signature_1_x >0 and signature_1_y >0 and signature_1_w >0):
                self.signature_filed(signature_1_x, signature_1_y, signature_1_h, signature_1_w, self.dean_name, self.dean_position,
                             self.path_to_dean_signature)
                
            # Second signature - process only if the path is provided
            if (self.path_to_csu_head_signature is not None)and (signature_2_x >0 and signature_2_y>0 and signature_2_w >0):
                self.signature_filed(signature_2_x, signature_2_y,signature_2_h, signature_2_w, self.csu_director_name, self.csu_position,
                                self.path_to_csu_head_signature)
            
            self.greeting(self.greeting_txt, greeting_y)

            contact_info_dict = {
                1: ["img/globe.png", "coc.qu.edu.sa", "https://coc.qu.edu.sa"],
                2: ["img/x-logo.png", "@coc_qu_sa", "https://twitter.com/coc_qu_sa"],
                3: ["img/checkmark.png", self.certificate_hash, ""]
                }
            self.contact_info(contact_info_dict, contact_info_x, contact_info_y)
            
            self.log.debug(f"Hash: '{self.certificate_hash}'")
            util.make_sure_path_exists(output_dir)
            self.pdf.output(f"{output_dir}/{self.recipient_email}-{self.certificate_hash}.pdf")
            self.pdf.close()
        else:
             print("erorr")
