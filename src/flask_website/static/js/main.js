const translations = {
    en: {
        Event: "Event",
        Settings: "Settings",
        Contact: "Contact",
        Sign_out: "Sign out",
        Templates: "Templates",
        Dismiss: "Dismiss",
        english: "English",
        arabic: "Arabic",
        arabic_english: "Arabic & English",
        Your_Events: "Your Events",
        Latest_Event: "Latest Event",
        More_Info: "More Info",
        Load_More: "Load More",
        Add_Events: "Add Events",
        Admin_page: "Admin Page",
        Explanation_Message: "Please select the language for the event and the certificate:",
        Users: "Users",
        ID: "ID",
        First_Name: "First Name",
        Email: "Email",
        Role: "Role",
        Edit: "Edit",
        Delete: "Delete",
        Customizations_added_successfully: "Customizations added successfully!",
        Certificate_Appearance: "Certificate Appearance",
        Template_Name: "Template Name",
        bilingual: "bilingual",
        Certificate_items: "Certificate items (English)",
        Certificate_items_ar: "Certificate items (Arabic)",
        All_positions_note: "All positions in numbers between 0.00 to 1.00.",
        Hide_signature_note: "Note: if you want to hide the signature set all values to 'Zero'",
        X_Position: "X Position",
        Y_Position: "Y Position",
        Height: "Height",
        Width: "Width",
        Color: "Color",
        Text: "Text",
        Website: "Website",
        Twitter: "Twitter (X)",
        Website_URL: "Website URL",
        Website_Name: "Website Name",
        Twitter_Handle: "Twitter Handle",
        Twitter_Link: "Twitter Link",
        Preview: "Preview",
        Save: "Save",
    },
    ar: {
        Event: "الاحداث",
        Settings: "الاعدادات",
        Contact: "تواصل معنا",
        Sign_out: "تسجيل خروج",
        Templates: "القوالب",
        Dismiss: "إنهاء",
        english: "الانجليزية",
        arabic: "العربية",
        arabic_english: "العربية والإنجليزية",
        Your_Events: "الاحداث التي قمت بإنشائها",
        Latest_Event: "آخر الاحداث",
        More_Info: "المزيد من المعلومات",
        Load_More: "تحميل المزيد",
        Add_Events: "اضافة حدث",
        Admin_page: "صفحة المدير",
        Explanation_Message: "يرجى تحديد اللغة للحدث والشهادة:",
        Users: "المستخدمون",
        ID: "المعرف",
        First_Name: "الاسم الأول",
        Email: "البريد الإلكتروني",
        Role: "الدور",
        Edit: "تحرير",
        Delete: "حذف",
        Customizations_added_successfully: "تمت إضافة التخصيصات بنجاح!",
        Certificate_Appearance: "مظهر الشهادة",
        Template_Name: "اسم القالب",
        bilingual: "ثنائي اللغة",
        Certificate_items: "عناصر الشهادة (للإنجليزية)",
        Certificate_items_ar: "عناصر الشهادة (للعربية)",
        All_positions_note: "جميع المواضع في أرقام بين 0.00 إلى 1.00.",
        Hide_signature_note: "ملاحظة: إذا كنت تريد إخفاء التوقيع، قم بتعيين جميع القيم إلى 'صفر'",
        X_Position: "الموضع X",
        Y_Position: "الموضع Y",
        Height: "الارتفاع",
        Width: "العرض",
        Color: "اللون",
        Text: "النص",
        Website: "موقع الويب",
        Twitter: "تويتر (X)",
        Website_URL: "رابط موقع الويب",
        Website_Name: "اسم موقع الويب",
        Twitter_Handle: "حساب تويتر",
        Twitter_Link: "رابط تويتر",
        Preview: "معاينة",
        Save: "حفظ",
    }
};
const setLanguage = (language) => {
    console.log(`Setting language to: ${language}`);
    const elements = document.querySelectorAll("[data-i18n]");
    elements.forEach((element) => {
        const translationKey = element.getAttribute("data-i18n");
        console.log(`Translating element with key: ${translationKey}`);
        if (translations[language][translationKey]) {
            if (element.tagName.toLowerCase() === 'input' && element.type === 'submit') {
                element.value = translations[language][translationKey];
            } else {
                element.textContent = translations[language][translationKey];
            }
        }
    });

    document.dir = language === "ar" ? "rtl" : "ltr";

    // Adjust left padding dynamically
    const navbarItems = document.querySelectorAll("#navbar-user ul li a");
    if (language === "ar") {
        navbarItems.forEach((item) => {
            item.style.paddingLeft = "1rem";
        });
    } else {
        navbarItems.forEach((item) => {
            item.style.paddingLeft = ""; // Reset padding
        });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    const language = localStorage.getItem("lang") || "en"; // اذا لم تكن اللغة متوفرة استخدم الانجليزية
    console.log(`Language on DOMContentLoaded: ${language}`);
    setLanguage(language);

    var checkbox = document.getElementById('bilingualCheckbox');
    var bilingual = document.getElementById("ardropdownToggleButton");
    var customItem = document.getElementById("customizationform");
    var keyitem = document.getElementById("keyitem");
    var signature = document.getElementById("signature");

    // Check if the checkbox is in the checked state
    window.check = function () {
        if (checkbox.checked) {
            bilingual.style.display = "flex";
        } else {
            bilingual.style.display = "none";
        }
    };

    window.dismissFlashMessage = function () {
        var flashMessage = document.getElementById('flashMessage');
        flashMessage.style.display = 'none';
    };

    window.checkItems = function (value, isChecked) {
        if (isChecked) {
            customItem.style.display = "block";
            keyitem.value = value;
            if (keyitem.value == "signature_1" || keyitem.value == "signature_2") {
                signature.style.display = "block";
            } else {
                signature.style.display = "none";
            }
            if (keyitem.value == "contact_info") {
                document.getElementById('webcheck').style.display = "flex";
                document.getElementById('Xcheck').style.display = "flex";
                document.getElementById('alttextfield').style.display = "none";
                document.getElementById('alttextfield2').style.display = "block";
            } else {
                document.getElementById('webcheck').style.display = "none";
                document.getElementById('Xcheck').style.display = "none";
                document.getElementById('alttextfield').style.display = "block";
                document.getElementById('alttextfield2').style.display = "none";
            }
        } else {
            customItem.style.display = "none";
        }
    };

    document.getElementById('web-checkbox').addEventListener('change', () => {
        const websitfield = document.getElementById('websitfield');
        const websitfield2 = document.getElementById('websitfield2');
        if (document.getElementById('web-checkbox').checked) {
            websitfield.style.display = "block";
            websitfield2.style.display = "block";
        } else {
            websitfield.style.display = "none";
            websitfield2.style.display = "none";
        }
    });

    document.getElementById('twitter-checkbox').addEventListener('change', () => {
        const xfield = document.getElementById('xfield');
        const xfield2 = document.getElementById('xfield2');
        if (document.getElementById('twitter-checkbox').checked) {
            xfield.style.display = "block";
            xfield2.style.display = "block";
        } else {
            xfield.style.display = "none";
            xfield2.style.display = "none";
        }
    });

    window.arCheckItems = function (value, isChecked) {
        if (isChecked) {
            customItem.style.display = "block";
            keyitem.value = value;
        } else {
            customItem.style.display = "none";
        }
    };

    window.submitForm = function (event, temp_id) {
        event.preventDefault(); // Prevent the default form submission behavior
        fetch(`/Select_template/${temp_id}`, {
            method: 'POST',
            body: new FormData(document.getElementById('customizationform')),
        })
            .then(response => {
                document.getElementById('flashMessage').style.display = "block";
                document.getElementById('fMessage').innerHTML = translations[language].Customizations_added_successfully;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };

    window.previewCertificate = function (temp_id) {
        const url = `/img/${temp_id}?_=${new Date().getTime()}`;
        const imgFrame = document.getElementById('preview-image');
        const imgFrame2 = document.getElementById('generated-image');
        imgFrame.style.display = "block";
        imgFrame2.style.display = "none";
        imgFrame2.src = null;

        fetch(url, { method: 'POST' })
            .then(response => response.blob())
            .then(blob => {
                const urlCreator = window.URL || window.webkitURL;
                imgFrame2.src = urlCreator.createObjectURL(blob);
                imgFrame2.style.display = "block";
                imgFrame.style.display = "none";
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };
});

const languageSelector = document.querySelector("select");
if (languageSelector) {
    languageSelector.addEventListener("change", (event) => {
        setLanguage(event.target.value);
        localStorage.setItem("lang", event.target.value);
    });
}