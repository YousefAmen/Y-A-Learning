from django.urls import path

from .views import (
    About,
    AddLessonView,
    CourseDetail,
    CoursesList,
    CreateCourse,
    CreateLearningObjectives,
    CreateModule,
    DeleteCourse,
    DeleteLearningObjectives,
    DeleteLesson,
    DeleteModule,
    EditLearningObjectives,
    EditLesson,
    EditModule,
    Index,
    UpdateCourse,
    fetch_courses_by_category,
    fetch_courses_by_tag,
    search,
)

app_name = 'course'
urlpatterns = [
  path('',Index.as_view(),name = 'index'),
  path('about/',About.as_view(),name = 'about'),
  path('create-course/',CreateCourse.as_view(),name = 'create-course'),
  path('update-course/<slug:slug>/<str:token>/',UpdateCourse.as_view(),name = 'update-course'),
  path('delete-course/<slug:slug>/<str:token>/',DeleteCourse.as_view(),name = 'delete-course'),
  path('create-course/create-objectives/<slug:slug>/<str:token>/',CreateLearningObjectives.as_view(),name = 'create-learning-objectives'),
  path('create-course/edit-objective/<slug:slug>/',EditLearningObjectives.as_view(),name = 'edit-learning-objective'),
  path('create-course/delete-objective/<slug:slug>/',DeleteLearningObjectives.as_view(),name = 'delete-learning-objective'),

  path('create-course/create-module/<slug:slug>/<str:token>/',CreateModule.as_view(),name = 'create-module'),
  path('create-course/edit-module/<slug:slug>/',EditModule.as_view(),name = 'edit-module'),
  path('create-course/delete-module/<slug:slug>/',DeleteModule.as_view(),name = 'delete-module'),
  path('create-course/module/create-lesson/<slug:slug>/',AddLessonView.as_view(),name = 'create-lesson'),
  path('create-course/module/edit-lesson/<slug:slug>/<str:token>',EditLesson.as_view(),name = 'edit-lesson'),
  path('create-course/module/delete-lesson/<slug:slug>/<str:token>',DeleteLesson.as_view(),name = 'delete-lesson'),
  path('course-detail/<slug:slug>/<str:token>/',CourseDetail.as_view(),name = 'course-detail'),
  path('search/',search,name = 'search'),
  path('courses/',CoursesList.as_view(),name = 'courses-list'),
  path('categories/<str:cat>/',fetch_courses_by_category,name = 'fetch-courses-by-category'),
  path('tags/<str:tag>/',fetch_courses_by_tag,name = 'fetch-courses-by-tag'),
  
]