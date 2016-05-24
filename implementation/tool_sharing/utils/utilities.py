import uuid, hashlib
import re
from django.template.loader import render_to_string
from django.core.mail import send_mail
from tool_sharing.settings import DEFAULT_FROM_EMAIL


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


class USStates:
    states_list = (
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AS", "American Samoa"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("DC", "District Of Columbia"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("GU", "Guam"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("MP", "Northern Mariana Islands"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("PR", "Puerto Rico"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UM", "United States Minor Outlying Islands"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VI", "Virgin Islands"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming")
    )

    def get_long_name(self, abbreviation):
        return dict(self.states_list).get(abbreviation)


def is_user_logged_in(session):
    return "cool_user" in session and session["cool_user"] is not None


def is_number(expression):
    pattern = re.compile("^([0-9]+)$")
    if pattern.match(expression) is None:
        return False
    return True


def contains_number(expression):
    pattern = re.compile(".*[0-9].*")
    if pattern.match(expression) is None:
        return False
    return True


def is_empty(text):
    return text.strip(' \t\n\r') == ""


def contains_space(expression):
    pattern = re.compile("\\s+$")
    if pattern.match(expression) is None:
        return False
    return True


def send_email(template_txt, template_html, params, title, to_email):
    msg_plain = render_to_string(template_txt, params)
    msg_html = render_to_string(template_html, params)

    send_mail(title, msg_plain, DEFAULT_FROM_EMAIL, [to_email], html_message=msg_html, fail_silently=True)
