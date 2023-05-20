from django.forms import Form, CharField


class LoginForm(Form):
    username = CharField(required=True)
    password = CharField(required=True)

    def clean_username(self):
        username = self.cleaned_data['username']
        # hello
        return username.strip()

    def clean_password(self):
        password = self.cleaned_data['password'].strip()

        return password.strip()
