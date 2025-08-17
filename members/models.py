import uuid
from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from django.db.models import Count, Avg

GENDER_CHOICES = (
    ("male", "Male"),
    ("female", "Female"),
)


ROLE_CHOICES = (
    ("student", "Student"),
    ("instructor", "Instructor"),
)


TEACHING_EXPERIENCE_CHOICES = (
    (1, "1 year"),
    (2, "2 years"),
    (3, "3 years"),
    (4, "4 years"),
    (5, "5+ years"),
)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    bio = models.TextField(max_length=500, blank=True, null=True)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES)
    profile_pic = models.ImageField(
        upload_to="users/profile_images/%Y/%m/%d/",
        blank=True,
        null=True,
        verbose_name="profile_picture",
    )
    phone = models.CharField(max_length=11, blank=True, null=True)
    country = CountryField()
    birth_date = models.DateField()
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="", unique=True)
    token = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.first_name}-{self.last_name}")
        if not self.token:
            self.token = uuid.uuid4().hex[:16].upper()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("members:user_profile", args=[self.slug, self.token])


class Instructor(Profile):
    """
    - Instructor profile it will inherit form the profile model
    - it will have the his owen Fields
    """

    about = models.TextField(max_length=500, blank=True, null=True)

    teaching_exe = models.PositiveSmallIntegerField(
        choices=TEACHING_EXPERIENCE_CHOICES,
        default=TEACHING_EXPERIENCE_CHOICES[0][0],
        blank=True,
    )
    followers = models.ManyToManyField(User, blank=True, related_name="followers")

    class Meta:
        permissions = [
            ("add_course", "Can add course"),
            ("change_course", "Can change course"),
            ("delete_course", "Can delete course"),
            ("add_module", "Can add module"),
            ("change_module", "Can update module"),
            ("delete_module", "Can delete course"),
            ("add_lesson", "Can add lesson"),
            ("change_lesson", "Can update lesson"),
            ("delete_lesson", "Can delete lesson"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Instructor)"

    @property
    def get_students_count(self):
        instructor_students = self.instructor_courses.aggregate(
            total_students=Count("course_enrollments")
        )["total_students"]
        return instructor_students or 0

    @property
    def get_total_reviews(self):
        total_reviews = self.instructor_courses.aggregate(
            total=Count("course_reviews")
        )["total"]
        return total_reviews or 0

    @property
    def get_avg_instructor_rating(self):
        total_rate = self.instructor_courses.aggregate(total=Avg("course_ratings"))[
            "total"
        ]
        return total_rate or 0


class SocialLinks(models.Model):
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instructor_links"
    )
    link_name = models.CharField(max_length=250)
    link = models.URLField(max_length=250)

    def __str__(self):
        return f"{self.link_name}"


class Student(Profile):
    """
    - Instructor profile it will inherit form the profile model
    - it will have the his owen Fields
    """

    enrollments = models.CharField(max_length=500, blank=True, null=True)
    courses_complete = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Student)"
