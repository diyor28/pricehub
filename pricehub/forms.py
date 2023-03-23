from django.forms import Form, CharField

users = {
    "ozod@gmail.com": {
        "firstName": "Ozod",
        "lastName": "Shukurov",
        "password": "1234"
    },
    "amir@gmail.com": {
        "firstName": "Amir",
        "lastName": "Akhtamov",
        "password": "qwerty123"
    },
    "ibrogim@gmail.com": {
        "firstName": "Ibrogim",
        "lastName": "Miraliev",
        "password": "pass123"
    }
}


class LoginForm(Form):
    email = CharField(required=True)
    password = CharField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.strip()

    def clean_password(self):
        password = self.cleaned_data['password'].strip()
        # if len(password) < 12:
        #     raise ValidationError("Password is too short")
        # if not any(char.isupper() for char in password):
        #     raise ValidationError("Should contain at least one upper case letter")
        # if not any(char.islower() for char in password):
        #     raise ValidationError("Should contain at least one lower case letter")
        # if not any(char.isdigit() for char in password):
        #     raise ValidationError("Should contain at least one digit")
        return password

