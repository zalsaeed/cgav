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
                 greeting_txt: str, certificate_template: str):
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
        self.certificate_hash = util.small_hash(self.recipient_email + self.recipient_name)
        
        # use and A4 in Landscape orientation.
        self.pdf = fpdf.FPDF(orientation='L', unit='mm', format='A4')
        
        # do not allow page breaks
        self.pdf.set_auto_page_break(auto=False)
        
        # add an empty page
        self.pdf.add_page()

        font_settings = configuration_loader.Settings()
        font_settings.read_yaml(open(os.path.abspath("fonts-config.yaml")))

        self.log.debug(font_settings['fonts'])
        
        # setup fonts, font size, and color
        self.pdf.add_font("NotoSans", style="", fname="NotoSans/NotoSansArabic-VariableFont_wdth,wght.ttf", uni=True)
        
        self.pdf.add_font("Amiri", style="", fname="Amiri/Amiri-Regular.ttf", uni=True)
        self.pdf.add_font("Amiri", style="I", fname="Amiri/Amiri-Italic.ttf", uni=True)
        self.pdf.add_font("Amiri", style="B", fname="Amiri/Amiri-Bold.ttf", uni=True)
        self.pdf.add_font("Amiri", style="BI", fname="Amiri/Amiri-BoldItalic.ttf", uni=True)

        self.pdf.add_font("SakkalMajalla", style="", fname="SakkalMajalla/majalla.ttf", uni=True)
        self.pdf.add_font("SakkalMajalla", style="B", fname="SakkalMajalla/majallab.ttf", uni=True)
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

    def certificate_info(self, x: float, y: float, h: float, w: float):
        # intro: str, recipient_name: str, recipient_title:str, certificate_details: str
        intro_width = self.pdf.get_string_width(self.certificate_intro)
        intro_x = (self.pdf.w - intro_width) / 2
        self.pdf.set_xy(intro_x, y)
        self.pdf.cell(intro_width, h, get_display(reshape(self.certificate_intro)), border=0, align="C", fill=False)
        
        recipient_title_width = self.pdf.get_string_width(self.recipient_title)
        recipient_name_width = self.pdf.get_string_width(self.recipient_name)
        left_margin = (self.pdf.w - (recipient_name_width + recipient_title_width)) / 2
        
        self.pdf.set_xy(left_margin, y+h)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="B")
        self.pdf.cell(recipient_name_width, h, get_display(reshape(self.recipient_name)), border=0, align="C",
                      fill=False)
        
        self.pdf.set_xy(left_margin+recipient_name_width, y+h)
        self.pdf.set_font(DEFAULT_FONT[0], size=DEFAULT_FONT[1], style="")
        self.pdf.cell(recipient_title_width, h, get_display(reshape(self.recipient_title)), border=0, align="C",
                      fill=False)

        body_lines = util.break_string_into_chunks(self.certificate_body, len(self.certificate_intro))
        for idx, line in enumerate(body_lines):

            self.pdf.set_xy(intro_x, y+(h*(idx+2)))
            self.pdf.cell(intro_width, h, get_display(reshape(line)), border=0, align="C", fill=False)

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

    def generate_certificate(self, output_dir: str):

        x = 140
        y = 100
        w = 17
        h = 13

        self.certificate_info(x, y, h, w)

        self.signature_filed(10, 190, 10, 50, self.dean_name, self.dean_position,
                             self.path_to_dean_signature)
        self.signature_filed(123.5, 190, 10, 50, self.csu_director_name, self.csu_position,
                             self.path_to_csu_head_signature)

        self.greeting(self.greeting_txt, 165)

        contact_info_dict = {
            1: ["img/globe.png", "coc.qu.edu.sa", "https://coc.qu.edu.sa"],
            2: ["img/x-logo.png", "@coc_qu_sa", "https://twitter.com/coc_qu_sa"],
            3: ["img/checkmark.png", self.certificate_hash, ""]
        }

        self.contact_info(contact_info_dict, 250, 180)

        self.log.debug(f"Hash: '{self.certificate_hash}'")
        util.make_sure_path_exists(output_dir)
        self.pdf.output(f"{output_dir}/{self.recipient_email}-{self.certificate_hash}.pdf")
        self.pdf.close()
