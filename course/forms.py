from django import forms
from django.core.exceptions import ValidationError

from .models import Course, LearningOutcomes, Lesson, Module


class AddCourseForms(forms.ModelForm):
  class Meta:
    model   = Course
    fields  =  ['title', 'description', 'requirements', 'image','promo_video', 'price', 'discount_price', 'is_free','is_puplished' ,'category','tags','level']

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


    self.fields['title'].widget.attrs.update({
      'class': 'form-control form-control-lg',
      'placeholder': 'Course Title'
    })

    self.fields['description'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Course Description',
      'rows': 4
    })

    self.fields['requirements'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Course Requirements',
      'rows': 3
        })

    self.fields['image'].widget.attrs.update({
      'class': 'form-control-file d-none'
    })

    self.fields['promo_video'].widget.attrs.update({
      'class': 'form-control-file d-none'
    })


    self.fields['price'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Course Price',
      'step': '0.01'
    })

    self.fields['discount_price'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Discount Price',
      'step': '0.01'
    })

    self.fields['is_free'].widget.attrs.update({
      'class': 'form-check-input'
    })
  
    self.fields['is_puplished'].widget.attrs.update({
      'class': 'form-check-input'
    })


    self.fields['category'].widget.attrs.update({
      'class': 'form-select'
    })

    self.fields['level'].widget.attrs.update({
      'class': 'form-select'
    })

    self.fields['tags'].widget.attrs.update({
      'class': 'form-control form-control-lg',
      'placeholder': 'Course Tags'
    })

  
  def clean(self):
    cd = self.cleaned_data
    if cd['price'] and cd['discount_price']:
      if cd['discount_price'] >= cd['price']:
        raise forms.ValidationError('Discount cannot be greater than or equal to the price.')
      cd['price'] = cd['price'] - cd['discount_price']

    if cd['price'] and cd['price'] <= 0 :
      raise forms.ValidationError('Discount cannot be less than or equal Zero.')
    
    if cd['price'] and cd['is_free']:
      raise forms.ValidationError('Cannot add a price when "is_free" is True. That means the course should be free.')
    return cd


class CreateModuleForm(forms.ModelForm):
  class Meta:
    model   = Module
    fields  = ['title','description','is_published']

  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.fields['title'].widget.attrs.update({
      'class': 'form-control form-control-lg',
      'placeholder': 'Course Title'
    })

    self.fields['description'].widget.attrs.update({
      'class': 'form-control',
      'placeholder': 'Course Description',
      'rows': 4
    })

    self.fields['is_published'].widget.attrs.update({
      'class': 'form-check-input',
      
    })





class AddLessonForm(forms.ModelForm):
  class Meta:
    model = Lesson
    fields = ['title','thumbnail','video']
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self.fields['title'].widget.attrs.update({
      'class': 'form-control form-control-lg',
      'placeholder': 'Course Title'
    })

    
    self.fields['video'].widget.attrs.update({
      'class': 'form-control-file d-none'
    })
    
    self.fields['thumbnail'].widget.attrs.update({
      'class': 'form-control-file d-none'
    })



class CreateLearningOutcomesForm(forms.ModelForm):

  class Meta:
    model = LearningOutcomes
    fields = ['description']
    widgets = {
      'description': forms.TextInput(attrs={
      'class': 'form-control',
      'placeholder': 'What students will learn (260)',
      
    })
  }

class SearchForm(forms.Form):
  search = forms.CharField(widget = forms.TextInput(attrs = {'class':'form-control','placeholder':'Searching...'}))

