from django.urls import path, include
from course.APIs import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("contacts", views.ContactViewSet, basename="contact")
urlpatterns = [
    # course endpoint urls
    # path("", views.courses_list, name="courses-list"),
    # path("create/",views.create_course, name="course-create"),
    # path("<slug:slug>/<str:token>/", views.course_detail, name="course-detail"),
    # path("<slug:slug>/<str:token>/update/", views.update_course, name="course-update"),
    # path("<slug:slug>/<str:token>/delete/", views.delete_course, name="course-delete"),
    # # Module urls
    # path("<slug:slug>/<str:token>/modules/", views.modules_list, name="modules-list"),
    # path("<slug:slug>/<str:token>/modules/draft/", views.draft_modules, name="modules-draft"),
    # path(
    #     "<slug:slug>/<str:token>/modules/create/", views.create_modules, name="module-create"
    # ),
    # path("modules/module/<slug:slug>/update/", views.update_modules, name="module-update"),
    # path("modules/module/<slug:slug>/delete/", views.delete_modules, name="module-delete"),
    # # Learning outcomes urls
    # path(
    #     "<slug:slug>/<str:token>/learning-outcomes/",
    #     views.course_learning_outcome,
    #     name="learning-outcomes-list",
    # ),
    # path(
    #     "<slug:slug>/<str:token>/learning-outcomes/create/",
    #     views.create_learning_outcome,
    #     name="learning-outcome-create",
    # ),
    # path(
    #     "learning-outcomes/outcome/<slug:slug>/update/",
    #     views.update_learning_outcomes,
    #     name="learning-outcome-update",
    # ),
    # path(
    #     "learning-outcomes/outcome/<slug:slug>/delete/",
    #     views.delete_learning_outcomes,
    #     name="learning-outcome-delete",
    # ),
    # path("<slug:slug>/lesson/adding/", views.adding_lessons, name="adding-lessons"),
    # path("lesson/update/<str:lesson_token>/", views.update_lesson, name="update-lesson"),
    # path("lesson/delete/<str:lesson_token>/", views.delete_lesson, name="delete-lesson"),
    # path(
    #     "review/create/<slug:course_slug>/<slug:course_token>/",
    #     views.create_review,
    #     name="create-review",
    # ),
    # path("review/update/<slug:review_slug>/", views.update_review, name="update-review"),
    # path("review/delete/<slug:review_slug>/", views.delete_review, name="delete-review"),
    # end function enddpoint
    # --------------------------------
    # start generics endpoints pattern
    # --------------------------------
    # Course generics endpoints
    path("", views.CoursesList.as_view(), name="courses-list"),
    path(
        "<slug:slug>/<str:token>/update/",
        views.UpdateCourseView.as_view(),
        name="update-course",
    ),
    path(
        "instructor-courses/",
        views.InstructorCourseView.as_view(),
        name="update-course",
    ),
    path("create-course/", views.CreateCourseView.as_view(), name="create-course"),
    # module generics endpoints
    path(
        "<slug:slug>/<str:token>/all/course/modules/",
        views.AllCourseModules.as_view(),
        name="all-course-modules",
    ),
    path(
        "<slug:slug>/<str:token>/create/module/",
        views.CreateModuleView.as_view(),
        name="create-module",
    ),
    path(
        "<slug:slug>/update/module/",
        views.UpdateModuleView.as_view(),
        name="update-module",
    ),
    path(
        "<slug:slug>/delete/module/",
        views.DeleteModuleView.as_view(),
        name="delete-module",
    ),
    # learing outcomes generices endpoints
    path(
        "<slug:course_slug>/<str:course_token>/all/course/lessons/",
        views.AllCourseLessons.as_view(),
        name="all-course-lessons",
    ),
    # lessons generics endpoints
    path(
        "<slug:module_slug>/add/lesson/",
        views.AddingLessonView.as_view(),
        name="add-lesson",
    ),
    path(
        "<str:token>/update/lesson/",
        views.UpdateLessonView.as_view(),
        name="update-lesson",
    ),
    path(
        "<str:token>/delete/lesson/",
        views.DeleteLessonView.as_view(),
        name="delete-lesson",
    ),
    path(
        "learning-outcomes/<slug:slug>/create/outcome/",
        views.CreateLearningOutcome.as_view(),
        name="create-learning-outcome",
    ),
    path(
        "learning-outcomes/update/outcome/<slug:slug>/",
        views.UpdateLearningOutcome.as_view(),
        name="update-learning-outcome",
    ),
    path(
        "learning-outcomes/delete/outcome/<slug:slug>/",
        views.DeleteLearningOutcome.as_view(),
        name="delete-learning-outcome",
    ),
    # Review generics endpoints
    path(
        "<slug:slug>/<str:token>/add/review/",
        views.CreateReviewApiView.as_view(),
        name="add-review",
    ),
    path(
        "<slug:slug>/update/review/",
        views.UpateReviewApiView.as_view(),
        name="update-review",
    ),
    path(
        "<slug:slug>/delete/review/",
        views.DeleteReviewApiView.as_view(),
        name="update-review",
    ),
    # # only admins can used
    # path(
    #     "create/category/", views.CreateCategoryView.as_view(), name="create-category"
    # ),
    # path(
    #     "<slug:slug>/update/category/",
    #     views.UpdateCategoryView.as_view(),
    #     name="update-category",
    # ),
    # path(
    #     "<slug:slug>/delete/category/",
    #     views.DeleteCourseView.as_view(),
    #     name="delete-category",
    # ),
    # # contacts generics endpoints
    # path("user/contacts/", views.UserContactsView.as_view(), name="user-contacts"),
    # path("create/contact/", views.CreateContactView.as_view(), name="create-contact"),
    # path(
    #     "<str:token>/update/contact/",
    #     views.UpdateContactView.as_view(),
    #     name="update-contact",
    # ),
    # path("create/contact/", views.DeleteContactView.as_view(), name="delete-contact"),
    # start viewset endpoints pattern
    # path("", CoursesList.as_view(), name="courses"),
    # path("", include(router.urls)),
    # viewsets endpoints
]

urlpatterns += router.urls
