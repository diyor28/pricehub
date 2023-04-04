from django.forms import Form, CharField


class LoginForm(Form):
    username = CharField(required=True)
    password = CharField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.strip()

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

