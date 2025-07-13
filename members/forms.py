from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.db.models.signals import post_save

from .models import ROLE_CHOICES, Instructor, Profile, Student
from .signals import user_signed_up


class SignUpForms(SignupForm,forms.ModelForm):
    class Meta:
        model   = Instructor
        fields = ['first_name', 'last_name','role','email', 'gender', 'birth_date','country' ]
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Your First Name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Your Last Name'}),
            'email':forms.EmailInput(attrs={'class':'form-control','placeholder':'Your Email'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
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
            Submit("submit", "Submit", css_class="btn btn-primary w-100")
        )

    def save(self, request):
        user = super(SignUpForms, self).save(request)

        data = self.cleaned_data
        signup_data = {
            'first_name':data['first_name'],
            'last_name':data['last_name'],
            'role':data['role'],
            'gender':data['gender'],
            'country':data['country'],
            'birth_date':data['birth_date'],
        }
        user_signed_up.send(
            sender=user.__class__,
            user=user,
            signup_data=signup_data
        )

        return user

# for the social account authticationss
class RoleSelectionForm(forms.Form):

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="Select your account type"
    )
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Column("role", css_class="form-group col-md-6 mb-3"),
            )


class UpdateUserProfile(forms.ModelForm):
    
    class Meta:
        model = Instructor
        fields  = ['first_name', 'last_name','profile_pic','bio','phone', 'gender', 'birth_date','country' ]
        
        widgets = {
                'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Your First Name'}),
                'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Your Last Name'}),
        
                'profile_pic' : forms.FileInput(attrs={'class':'d-none'}),
                'bio' : forms.TextInput(attrs={'class':'form-control','placeholder':'About You.'}),
                'phone' : forms.NumberInput(attrs={'class':'form-control','placeholder':'Your Phone Number.'}),
                'gender': forms.Select(attrs={'class': 'form-control'}),
                'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'country': forms.Select(attrs={'class': 'form-control'}),
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
            Submit("submit", "Submit", css_class="btn btn-primary w-100")
        )