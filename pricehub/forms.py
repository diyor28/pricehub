from django.forms import Form, CharField


class LoginForm(Form):
    email = CharField(max_length=50, required=True)
    password = CharField(max_length=30, required=True)

    def cleaned_data(self):
        email = self.cleaned_data['email'].strip()
        password = self.cleaned_data['password'].strip()

        return {"email": email, "password": password}
