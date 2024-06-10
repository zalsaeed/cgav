
import os
import unittest

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base


HOSTNAME = os.environ.get('HOSTNAME')
DB_PORT = os.environ.get('DB_PORT')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_ROOT_PASSWORD = os.environ.get('MYSQL_ROOT_PASSWORD')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
SCHEMA = os.environ.get("SCHEMA")

class TestUsingFlaskSQLAlchemy(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] =\
            f'mysql+pymysql://{MYSQL_DATABASE}:{MYSQL_ROOT_PASSWORD}@{HOSTNAME}/{SCHEMA}'
        self.db = SQLAlchemy(self.app)
        self.bcrypt = Bcrypt(self.app)

        # we map the tables we already have in the database
        # to an object named base
        self.base = automap_base()
        self.base.prepare(autoload_with=self.db.engine)

    def test_insert_row_in_users_table(self):

        info = {
            "Fname": "عمر",
            "Lname": "خالد",
            "email": "test2@test.com",
            "password": "12345678",
            "user_role": 1
        }

        hashed_password = self.bcrypt.generate_password_hash(info["password"])

        # sanity check, show the tables names!
        users_table = self.base.classes.users
        session = self.db.session

        session.add(users_table(
                                Fname=info['Fname'],
                                Lname=info['Lname'],
                                email=info["email"],
                                password=hashed_password,
                                user_role=info["user_role"]))
        session.commit()

    def test_insert_row_in_template_table(self):
        template_data = {
            "id": 1,
            "template_name": "دورة",
            "template_image": "/root/src/flask_website/certificate-templates/template.png"
        }

        template_table = self.base.classes.template
        session = self.db.session

        session.add(template_table(
            id=template_data['id'],
            template_name=template_data['template_name'],
            template_image=template_data['template_image']
        ))
        session.commit()

    def test_insert_row_in_Event_type_table(self):
        event_type_data = {
            "event_type_name": "دورة",
            "is_active": True
        }

        event_type_table = self.base.classes.Event_type
        
        session = self.db.session
        session.add(event_type_table(
            event_type_name=event_type_data['event_type_name'],
            is_active=event_type_data['is_active']
        ))
        session.commit()

    def test_insert_row_in_instructor_table(self):
        instructor_data = {
            "instructor_id": "1",
            "first_name": "Bob",
            "last_name": "Johnson",
            "gender": "male",
            "email": "bob@example.com",
            "phone_number": "9876543210"
        }

        instructor_table = self.base.classes.instructor
        session = self.db.session

        # Check if instructor with the given ID already exists
        existing_instructor = session.query(instructor_table).filter_by(instructor_id=instructor_data['instructor_id']).first()
        if existing_instructor is None:
            session.add(instructor_table(
                instructor_id=instructor_data['instructor_id'],
                first_name=instructor_data['first_name'],
                last_name=instructor_data['last_name'],
                gender=instructor_data['gender'],
                email=instructor_data['email'],
                phone_number=instructor_data['phone_number']
            ))
            session.commit()

    def test_insert_row_in_recipient_table(self):
        recipient_data = {
            "recipient_id": "1",
            "first_name": "Alice",
            "last_name": "Smith",
            "gender": "female", 
            "email": "alice@example.com",
            "phone_number": "1234567890"
        }

        recipient_table = self.base.classes.recipient
        session = self.db.session

        # Check if recipient with the given ID already exists
        existing_recipient = session.query(recipient_table).filter_by(recipient_id=recipient_data['recipient_id']).first()
        if existing_recipient is None:
            session.add(recipient_table(
                recipient_id=recipient_data['recipient_id'],
                first_name=recipient_data['first_name'],
                last_name=recipient_data['last_name'],
                gender=recipient_data['gender'],
                email=recipient_data['email'],
                phone_number=recipient_data['phone_number']
            ))
            session.commit()


    def test_insert_row_in_CertificateCustomizations_table(self):
        customization_data = {
            "customization_id": 1,
            "template_id": 1, 
            "id": 1,
            "items_positions": "{}"
        }
        customization_table = self.base.classes.CertificateCustomizations
        session = self.db.session
        session.add(customization_table(
            customization_id=customization_data['customization_id'],
            template_id=customization_data['template_id'],
            id=customization_data['id'],
            items_positions=customization_data['items_positions']
        ))
        session.commit()

       
    def test_insert_row_in_addCertificate_table(self):
        certificate_data = [
            {
                "created_by": 1,
                "certificate_title": "شهادة شكر",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
                "intro": "تشهد كلية الحاسب بجامعة القصيم ممثلة بوحدة خدمة المجتمع أن",
                "female_recipient_title": "المتدربة:",
                "male_recipient_title": "المتدرب:",
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "مها حسن الحمد",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2024-02-22",
                "certificate_description_female": "قد حضرت البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "certificate_description_male": "قد حضر البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "file_path": "/root/src/data/Arabic-data.csv",
                "first_Signatory_Name": "محمد بن فهد التميمي",
                "first_Signatory_Position": "عميد كلية الهندسة",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "خالد بن صالح الصالح",
                "second_Signatory_Position": "عميد عمادة خدمة المجتمع",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",
                "greeting_female": "مع تمنياتنا لها بالتوفيق والسداد",
                "greeting_male": "مع تمنياتنا له بالتوفيق والسداد",
                "form_type" : "Arabic"
            },
            {
                "created_by": 1,
                "certificate_title": "2",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
                "intro": "تشهد كلية الحاسب بجامعة القصيم ممثلة بوحدة خدمة المجتمع أن",
                "female_recipient_title": "المتدربة:",
                "male_recipient_title": "المتدرب:",
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "ساره ناصر",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2024-02-22",
                "certificate_description_female": "قد حضرت البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "certificate_description_male": "قد حضر البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "file_path": "/root/src/data/Arabic-data.csv",
                "first_Signatory_Name": "محمد بن فهد التميمي",
                "first_Signatory_Position": "عميد كلية الهندسة",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "خالد بن صالح الصالح",
                "second_Signatory_Position": "عميد عمادة خدمة المجتمع",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",
                "greeting_female": "مع تمنياتنا لها بالتوفيق والسداد",
                "greeting_male": "مع تمنياتنا له بالتوفيق والسداد",
                "form_type" : "Arabic"
            },
            {
                "created_by": 1,
                "certificate_title": "3",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
              
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "فهد العبدالرحيم ",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2024-02-22",

                "file_path": "/root/src/data/Arabic-data.csv",
                "first_Signatory_Name": "محمد بن فهد التميمي",
                "first_Signatory_Position": "عميد كلية الهندسة",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "خالد بن صالح الصالح",
                "second_Signatory_Position": "عميد عمادة خدمة المجتمع",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",

                "intro": "تشهد كلية الحاسب بجامعة القصيم ممثلة بوحدة خدمة المجتمع أن",
                "female_recipient_title": "المتدربة:",
                "male_recipient_title": "المتدرب:",
                "certificate_description_female": "قد حضرت البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "certificate_description_male": "قد حضر البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "greeting_female": "مع تمنياتنا لها بالتوفيق والسداد",
                "greeting_male": "مع تمنياتنا له بالتوفيق والسداد",

                "form_type" : "Arabic"
            },
            {
                "created_by": 1,
                "certificate_title": "4",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
                "intro": "تشهد كلية الحاسب بجامعة القصيم ممثلة بوحدة خدمة المجتمع أن",
                "female_recipient_title": "المتدربة:",
                "male_recipient_title": "المتدرب:",
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "حمدان العيد",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2024-02-22",
                "certificate_description_female": "قد حضرت البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "certificate_description_male": "قد حضر البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "file_path": "/root/src/data/Arabic-data.csv",
                "first_Signatory_Name": "محمد بن فهد التميمي",
                "first_Signatory_Position": "عميد كلية الهندسة",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "خالد بن صالح الصالح",
                "second_Signatory_Position": "عميد عمادة خدمة المجتمع",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",
                "greeting_female": "مع تمنياتنا لها بالتوفيق والسداد",
                "greeting_male": "مع تمنياتنا له بالتوفيق والسداد",
                "form_type" : "Arabic"
            }
        ]

        English_certificate_data = [
            {
                "created_by": 1,
                "certificate_title": "5",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
                "intro": "Computer of Collage in Qassim University statify that",
                "female_recipient_title": "Student:",
                "male_recipient_title": "Student:",
                
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "Maha Alhamad",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2025-02-22",

                "certificate_description_female": "She attended the training program: the name of the course, which conduct online through Zoom with the name of the association on 5/30/2025",
                "certificate_description_male":"He attended the training program: the name of the course, which conduct online through Zoom with the name of the association on 5/30/2025",
                "file_path": "/root/src/data/English-data.csv",

                "first_Signatory_Name": "Mohamad Fahad Altimimi",
                "first_Signatory_Position": "Head of Collage",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "Khaled Hassan AlHassn",
                "second_Signatory_Position": "Dean of Admission and Regestration",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",

                "greeting_female": "Best of luck for her",
                "greeting_male": "Best of luck for him",

                "form_type" : "English"
            },
        ]

        Arabic_and_English_certificate_data = [
            {
                "created_by": 1,
                "certificate_title": "6",
                "event_type_id": 1,
                "template_path": "/root/src/flask_website/certificate-templates/template.png",
                "customization_id": None,
                "template_id": None,
                "instructor_id": None,
                "presenter_name": "Maha Alhamad",
                "secret_phrase": "ggGBs2hu9j",
                "event_date": "2025-02-22",
                "file_path": "/root/src/data/Arabic_and_English-data.csv",

                # Arabic
                "intro": "تشهد كلية الحاسب بجامعة القصيم ممثلة بوحدة خدمة المجتمع أن",
                "female_recipient_title": "المتدربة:",
                "male_recipient_title": "المتدرب:",
                "certificate_description_female": "قد حضرت البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "certificate_description_male": "قد حضر البرنامج التدريبي: اسم الدورة والذي أقيم عن بعد بالتعاون مع الجمعية اسم الجمعية بتاريخ ٢٠٢٣/٥/٣٠م",
                "greeting_female": "مع تمنياتنا لها بالتوفيق والسداد",
                "greeting_male": "مع تمنياتنا له بالتوفيق والسداد",

                # English
                "intro_en": "Computer of Collage in Qassim University statify that",
                "female_recipient_title_en": "Student:",
                "male_recipient_title_en": "Student:",
                "certificate_description_female_en": "She attended the training program: the name of the course, which conduct online through Zoom with the name of the association on 5/30/2025",
                "certificate_description_male_en":"He attended the training program: the name of the course, which conduct online through Zoom with the name of the association on 5/30/2025",
                "greeting_female_en": "Best of luck for her",
                "greeting_male_en": "Best of luck for him",

                "first_Signatory_Name": "Mohamad Fahad Altimimi",
                "first_Signatory_Position": "Head of Collage",
                "first_Signatory_Path": "/root/src/signatures/sample-sig-1.png",
                "second_Signatory_Name": "Khaled Hassan AlHassn",
                "second_Signatory_Position": "Dean of Admission and Regestration",
                "second_Signatory_Path": "/root/src/signatures/sample-sig-2.png",

                "form_type" : "Arabic_English"
            },
        ]

        certificate_table = self.base.classes.addCertificate
        session = self.db.session

        for data in certificate_data:
            session.add(certificate_table(
                created_by=data['created_by'],
                certificate_title=data['certificate_title'],
                event_type_id=data['event_type_id'],
                template_path=data['template_path'],
                customization_id=data['customization_id'],
                template_id=data['template_id'],
                instructor_id=data['instructor_id'],
                presenter_name=data['presenter_name'],
                secret_phrase=data['secret_phrase'],
                event_date=data['event_date'],
                file_path=data['file_path'],

                first_Signatory_Name=data['first_Signatory_Name'],
                first_Signatory_Position=data['first_Signatory_Position'],
                first_Signatory_Path=data['first_Signatory_Path'],
                second_Signatory_Name=data['second_Signatory_Name'],
                second_Signatory_Position=data['second_Signatory_Position'],
                second_Signatory_Path=data['second_Signatory_Path'],
            
                intro=data['intro'],
                female_recipient_title=data['female_recipient_title'],
                male_recipient_title=data['male_recipient_title'],
                certificate_description_female=data['certificate_description_female'],
                certificate_description_male=data['certificate_description_male'],
                greeting_female=data['greeting_female'],
                greeting_male=data['greeting_male'],

                form_type = data['form_type']
            ))

        for data in English_certificate_data:
                session.add(certificate_table(
                    created_by=data['created_by'],
                    certificate_title=data['certificate_title'],
                    event_type_id=data['event_type_id'],
                    template_path=data['template_path'],
                    customization_id=data['customization_id'],
                    template_id=data['template_id'],
                    instructor_id=data['instructor_id'],
                    presenter_name=data['presenter_name'],
                    secret_phrase=data['secret_phrase'],
                    event_date=data['event_date'],

                    
                    file_path=data['file_path'],
                    first_Signatory_Name=data['first_Signatory_Name'],
                    first_Signatory_Position=data['first_Signatory_Position'],
                    first_Signatory_Path=data['first_Signatory_Path'],
                    second_Signatory_Name=data['second_Signatory_Name'],
                    second_Signatory_Position=data['second_Signatory_Position'],
                    second_Signatory_Path=data['second_Signatory_Path'],

                    greeting_female_en=data['greeting_female'],
                    greeting_male_en=data['greeting_male'],
                    intro_en=data['intro'],
                    female_recipient_title_en=data['female_recipient_title'],
                    male_recipient_title_en=data['male_recipient_title'],
                    certificate_description_female_en=data['certificate_description_female'],
                    certificate_description_male_en=data['certificate_description_male'],

                    form_type = data['form_type']
                ))

        for data in Arabic_and_English_certificate_data:
                session.add(certificate_table(
                    created_by=data['created_by'],
                    certificate_title=data['certificate_title'],
                    event_type_id=data['event_type_id'],
                    template_path=data['template_path'],
                    customization_id=data['customization_id'],
                    template_id=data['template_id'],
                    instructor_id=data['instructor_id'],
                    presenter_name=data['presenter_name'],
                    secret_phrase=data['secret_phrase'],
                    event_date=data['event_date'],

                    
                    file_path=data['file_path'],
                    first_Signatory_Name=data['first_Signatory_Name'],
                    first_Signatory_Position=data['first_Signatory_Position'],
                    first_Signatory_Path=data['first_Signatory_Path'],
                    second_Signatory_Name=data['second_Signatory_Name'],
                    second_Signatory_Position=data['second_Signatory_Position'],
                    second_Signatory_Path=data['second_Signatory_Path'],

                    # Arabic
                    intro=data['intro'],
                    female_recipient_title=data['female_recipient_title'],
                    male_recipient_title=data['male_recipient_title'],
                    certificate_description_female=data['certificate_description_female'],
                    certificate_description_male=data['certificate_description_male'],
                    greeting_female=data['greeting_female'],
                    greeting_male=data['greeting_male'],

                    # English
                    greeting_female_en=data['greeting_female_en'],
                    greeting_male_en=data['greeting_male_en'],
                    intro_en=data['intro_en'],
                    female_recipient_title_en=data['female_recipient_title_en'],
                    male_recipient_title_en=data['male_recipient_title_en'],
                    certificate_description_female_en=data['certificate_description_female_en'],
                    certificate_description_male_en=data['certificate_description_male_en'],

                    form_type = data['form_type']
                ))


        session.commit()

    
    # def test_insert_row_in_Certificate_table(self):
    #     certificate_data = {
    #         "certificate_hash": "unique_hash_value",
    #         "recipient_id": "1",
    #         "certificate_event_id": 1
    #     }
        
    #     certificate_table = self.base.classes.Certificate_table
    #     session = self.db.session

    #     # Check if a record with the same hash already exists
    #     existing_certificate = session.query(certificate_table).filter_by(
    #         certificate_hash=certificate_data['certificate_hash']
    #     ).first()
        
    #     if existing_certificate is None:
    #         session.add(certificate_table(
    #             certificate_hash=certificate_data['certificate_hash'],
    #             recipient_id=certificate_data['recipient_id'],
    #             certificate_event_id=certificate_data['certificate_event_id']
    #         ))
    #         session.commit()
    #     else:
    #         print("Certificate record already exists. Skipping insertion.")


    def test_insert_row_in_demo_table(self):
        demo_data = {
            "ID": 1,
            "Name": "Demo",
            "Hint": "This is a demo"
        }
        demo_table = self.base.classes.demo
        session = self.db.session
        
        # Check if a record with the same ID already exists
        existing_demo = session.query(demo_table).filter_by(
            ID=demo_data['ID']
        ).first()
        
        if existing_demo is None:
            session.add(demo_table(
                ID=demo_data['ID'],
                Name=demo_data['Name'],
                Hint=demo_data['Hint']
            ))
            session.commit()
        else:
            print("Demo record already exists. Skipping insertion.")



if __name__ == '__main__':
    # Create a test suite and add the test cases in the desired order
    suite = unittest.TestSuite()
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_users_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_template_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_Event_type_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_instructor_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_recipient_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_CertificateCustomizations_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_addCertificate_table'))
    # suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_Certificate_table'))
    suite.addTest(TestUsingFlaskSQLAlchemy('test_insert_row_in_demo_table'))
    
    # Run the test suite
    unittest.TextTestRunner().run(suite)
