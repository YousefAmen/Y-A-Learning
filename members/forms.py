from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms

from .models import Instructor, Student, SocialLinks, User
from .signals import user_signed_up

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class SignUpForms(SignupForm):
    first_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your First Name"}
        ),
    )

    last_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Last Name"}
        ),
    )

    role = forms.ChoiceField(
        choices=User.Role.choices, widget=forms.Select(attrs={"class": "form-control"})
    )

    gender = forms.ChoiceField(
        choices=User.Gender.choices,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    country = CountryField(blank_label="Select Country").formfield(
        widget=CountrySelectWidget(
            attrs={"class": "form-control", "size": "5", "placeholder": "Country"}
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-3"),
                Column("last_name", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("email", css_class="form-group col-md-12 mb-3"),
            ),
            Row(
                Column("role", css_class="form-group col-md-6 mb-3"),
                Column("gender", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("birth_date", css_class="form-group col-md-6 mb-3"),
                Column("country", css_class="form-group col-md-6 mb-3"),
            ),
            Submit("submit", "Submit", css_class="btn btn-primary w-100"),
        )

    def save(self, request):
        user = super(SignUpForms, self).save(request)
        data = self.cleaned_data

        user.role = data["role"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.gender = data["gender"]
        user.birth_date = data["birth_date"]
        user.country = data["country"]
        user.save()
        signup_data = {
            "role": data["role"],
        }
        user_signed_up.send(sender=user.__class__, user=user, signup_data=signup_data)

        return user


# for the social account authticationss
class RoleSelectionForm(forms.Form):

    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.RadioSelect,
        label="Select your account type",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Column("role", css_class="form-group col-md-6 mb-3"),
        )


class UpdateUserProfile(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "profile_pic",
            "bio",
            "phone",
            "gender",
            "birth_date",
            "country",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your Last Name"}
            ),
            "profile_pic": forms.FileInput(attrs={"class": "d-none"}),
            "bio": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "About You.", "rows": 4}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your Phone Number."}
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "country": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="form-group col-md-6 mb-3"),
                Column("last_name", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("profile_pic", css_class="form-group col-md-12 mb-3"),
            ),
            Row(
                Column("bio", css_class="form-group col-md-12 mb-3"),
            ),
            Row(
                Column("gender", css_class="form-group col-md-6 mb-3"),
            ),
            Row(
                Column("birth_date", css_class="form-group col-md-6 mb-3"),
                Column("country", css_class="form-group col-md-6 mb-3"),
            ),
            Submit("submit", "Submit", css_class="btn btn-primary w-100"),
        )


class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = SocialLinks
        fields = ["link_name", "link"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("link_name", css_class="form-group col-md-6 mb-3"),
                Column("link", css_class="form-group col-md-6 mb-3"),
            ),
        )


class InstructorEditProfile(forms.ModelForm):

    class Meta:
        model = Instructor
        fields = ["about", "teaching_exe"]
        widgets = {
            "about": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "About yourself",
                    "rows": 4,
                }
            ),
            "teaching_exe": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("about", css_class="form-group col-md-12 mb-3"),
            ),
            Row(
                Column("teaching_exe", css_class="form-group col-md-6 mb-3"),
            ),
            Submit("submit", "Update Profile", css_class="btn btn-primary w-100"),
        )
