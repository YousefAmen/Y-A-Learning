from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from members.models import Instructor, Student

from .forms import (
    AddCourseForms,
    AddLessonForm,
    CreateLearningOutcomesForm,
    CreateModuleForm,
    SearchForm,
)
from .models import Category, Course, LearningOutcomes, Lesson, Module


class Index(TemplateView):
    template_name = 'course_pages/index.html'


class About(TemplateView):
    template_name = 'about.html'


class CreateCourse(PermissionRequiredMixin, CreateView):
  model         = Course
  form_class    = AddCourseForms 
  template_name = 'course_pages/add_course.html'
  permission_required = 'course.add_course'

  def form_valid(self, form):
    user = self.request.user

    form.instance.user = user
    form.instance.instructor = user.instructor
    messages.success(self.request, 'Your course has been uploaded successfully.')
    return super().form_valid(form)


  def get_success_url(self):
    return reverse_lazy('course:create-lerning-outcome',args = [
      self.object.slug,
      self.object.token,
    ])



class UpdateCourse(PermissionRequiredMixin, UpdateView):
  model         = Course
  form_class    = AddCourseForms 
  template_name = 'course_pages/update_course.html'
  success_url   = reverse_lazy('course:index')
  permission_required  = 'course.change_course'



class DeleteCourse(PermissionRequiredMixin, DeleteView):
  model = Course
  template_name = 'course_pages/delete_course.html'
  success_url   = reverse_lazy('course:index')
  permission_required  = 'course.delete_course'


class CreateLearningObjectives(CreateView):
  model = LearningOutcomes
  template_name = 'course_pages/create_learning_outcomes.html'
  form_class = CreateLearningOutcomesForm
  
  def get_course(self):
    return Course.objects.get(slug= self.kwargs['slug'],token = self.kwargs['token'])

  def form_valid(self,form):
    course = self.get_course()
    form.instance.course = course 
    messages.success(self.request,'Add Successfully.')
    return super().form_valid(form)

  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    course = self.get_course()
    course_outcomes = LearningOutcomes.objects.filter(course= course)
    context['course'] = course
    context['course_outcomes'] = course_outcomes
    return context

  def get_success_url(self):
    course = self.get_course()
    return reverse_lazy('course:create-learning-objectives',args = [course.slug,course.token,])


class EditLearningObjectives(UpdateView):
  model = LearningOutcomes
  template_name  = 'course_pages/edit_learning_outcomes.html'
  form_class = CreateLearningOutcomesForm
  context_object_name  = 'objective'

  def form_valid(self,form):
    outcome = self.get_object()
    if not self.request.user.instructor == outcome.course.instructor:
      messages.info(self.request,"You don't have premission to edit this objective")
    return super().form_valid(form)

  def get_success_url(self):
    objective = self.get_object()
    return reverse_lazy('course:create-learning-objectives',args = [
      objective.course.slug,
      objective.course.token,
    ])


class DeleteLearningObjectives(DeleteView):
  model = LearningOutcomes
  template_name  = 'course_pages/delete_learning_outcomes.html'
  context_object_name  = 'objective'

  def get_success_url(self):
    objective = self.get_object()
    return reverse_lazy('course:create-learning-objectives',args = [
      objective.course.slug,
      objective.course.token,
    ])


def most_viewed_courses(request):
  pass


class CreateModule(PermissionRequiredMixin,CreateView):
  model  = Module
  template_name = 'course_pages/create_module.html'
  form_class = CreateModuleForm
  permission_required = 'module.add_module'
  def get_course(self):
    return Course.objects.get(slug =self.kwargs['slug'],token=self.kwargs['token'])

  def form_valid(self,form):
    course = self.get_course()
    form.instance.course = course
    return super().form_valid(form)

  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    course = self.get_course()
    
    course_modules = Module.objects.filter(course  =course).order_by('-created_at')
    
    context['course_modules'] = course_modules
    context['course'] = course
    
    return context

  def get_success_url(self):
    course = self.get_course()
    messages.success(self.request,f'Your {self.object.title } module is created successfully.')
    return reverse_lazy('course:create-module',args = [
      course.slug,
      course.token,
    ])


class EditModule(PermissionRequiredMixin,UpdateView):
  model = Module
  template_name = 'course_pages/edit_module.html'
  form_class = CreateModuleForm
  permission_required = 'module.change_module'
  def get_success_url(self):
    course= self.object.course
    return reverse_lazy('course:create-module',args = [
    course.slug,
    course.token,
    ])


class DeleteModule(PermissionRequiredMixin,DeleteView):
  model = Module 
  template_name = 'course_pages/delete_module.html'
  permission_required = 'module.delete_module'

  def get_success_url(self):
    course = self.object.course
    return reverse_lazy('course:create-module',args = [course.slug,course.token])


class AddLessonView(CreateView):
  model = Lesson
  template_name = 'course_pages/add_lesson.html'
  form_class  = AddLessonForm

  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    module = Module.objects.get(slug = self.kwargs['slug'])
    context['module'] = module
    return context

  def form_valid(self,form):
    module = Module.objects.get(slug = self.kwargs['slug'])
    form.instance.module = module
    messages.success(self.request,f'The lesson is created successfully and is add in {module.title}')
    return super().form_valid(form)

  def get_success_url(self):
    lesson= self.object
    return reverse_lazy('course:create-module',args = [lesson.module.course.slug,lesson.module.course.token,])


class EditLesson(PermissionRequiredMixin,UpdateView):
  model = Lesson
  template_name = 'course_pages/edit_lesson.html'
  form_class = AddLessonForm
  permission_required  = 'lesson.add_lesson'
  def get_success_url(self):
    lesson = self.object
    return reverse_lazy('course:create-module',args = [
      lesson.module.course.slug,
      lesson.module.course.token,
      
    ])


class DeleteLesson(PermissionRequiredMixin,DeleteView):
  model = Lesson
  template_name = 'course_pages/delete_lesson.html'
  permission_required  = 'lesson.delete_lesson'
  def get_success_url(self):
    lesson = self.object
    return reverse_lazy('course:create-module',args = [
      lesson.module.course.slug,
      lesson.module.course.token,
    ])


class CoursesList(ListView):
  model = Course
  template_name = 'course_pages/courses.html'
  ordering  = ['-created_at']
  context_object_name = 'courses'
  def get_queryset(self):
    return Course.objects.filter(is_puplished=True)
  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    categories = Category.objects.all()
    context['categories']  = categories
    return context 


class CourseDetail(DetailView):
  model = Course
  template_name = 'course_pages/course_detail.html'
  context_object_name = 'course'
  def get_context_data(self,**kwargs):
    course = self.get_object()
    context = super().get_context_data(**kwargs)
    total_duration = Course.objects.filter(slug = course.slug,token = course.token).aggregate(total_hours = Sum('modules__lessons__duration'))
    
    context['total_hours'] = total_duration['total_hours']
    return context

# check if user is login or not 
# check if this course is pay this course or not 
# check if not pay check if the lesson is preview true so can user see as introducation 
# check if user is instructor or student


class LessonDetail(DeleteView):
  
  pass


def fetch_courses_by_tag(request,tag):
  
  courses = Course.objects.filter(tags__name = tag).order_by('-created_at')
  context = {'courses':courses,'tag':tag}
  return render(request,'course_pages/fetch_courses_by_tag.html',context)


def fetch_courses_by_category(request,cat):
  
  courses = Course.objects.filter(category__name = cat).order_by('-created_at')
  category = Category.objects.get(name = cat) 
  if 'category_views' not in request.session:
    request.session['category_views'] = []
  if request.user.id not in request.session['category_views']:
    category.views+=1
    category.save()
    request.session['category_views'].append(request.user.id)
    request.session.modified = True
  popular_categories = Category.objects.all().order_by('-views')[:5]
  context = {'courses':courses,'category':category,'popular_categories':popular_categories}
  return render(request,'course_pages/fetch_courses_by_category.html',context)


def search(request):
  results = {'instructors':None,'courses':None}
  query= None
  form = SearchForm(request.GET or None)
  if "search"  in request.GET:
    if form.is_valid():
      query = form.cleaned_data['search']
      courses = Course.objects.filter(Q(title__icontains = query)|Q(description__icontains = query),is_puplished=True).order_by('-created_at').distinct()
      instructors = Instructor.objects.filter(Q(first_name__icontains = query)|Q(last_name__icontains = query)).distinct()
      if courses.exists():
        results['courses'] = courses
      if instructors.exists():
        results['instructors'] = instructors
  context = {'form':form,'query':query,'results':results}
  return render(request,'course_pages/search.html',context)

