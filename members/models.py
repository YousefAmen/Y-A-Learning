import uuid
from datetime import date

from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from django.db.models import Count, Avg
from django.contrib.auth.models import Group
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

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


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = (
            "student",
            "STUDENT",
        )
        INSTRUCTOR = "instructor", "Instructor"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, choices=Role.choices, default=Role.STUDENT)
    bio = models.TextField(max_length=500, blank=True, null=True)
    gender = models.CharField(
        max_length=255, choices=Gender.choices, default=Gender.MALE
    )
    profile_pic = CloudinaryField("image", null=True, blank=True)
    phone = models.CharField(max_length=11, blank=True, null=True)
    country = CountryField()
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="")
    token = models.CharField(max_length=20, unique=True, blank=True)
    objects = UserManager()
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.first_name}-{self.last_name}")
        if not self.token:
            self.token = uuid.uuid4().hex[:16].upper()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("members:user_profile", args=[self.slug, self.token])


class Instructor(User):
    """
    - Instructor profile it will inherit form the profile model
    - it will have the his owen Fields
    """

    class TeachingExperience(models.TextChoices):
        ONE_YEAR = "1", "1 year"
        TWO_YEARS = "2", "2 years"
        THREE_YEARS = "3", "3 years"
        FOUR_YEARS = "4", "4 years"
        FIVE_PLUS = "5", "5+ years"

    about = models.TextField(max_length=500)

    teaching_exe = models.PositiveSmallIntegerField(
        choices=TeachingExperience.choices,
        default=TeachingExperience.ONE_YEAR,
        blank=True,
    )
    followers = models.ManyToManyField(User, blank=True, related_name="followers")

    class Meta:
        verbose_name_plural = "Instructors"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Instructor)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        instructor_group = Group.objects.get(name="Instructors")
        if not self.groups.filter(pk=instructor_group.pk).exists():
            self.groups.add(instructor_group)

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
        total_rate = self.instructor_courses.aggregate(
            total=Avg("course_reviews__rate")
        )["total"]
        return total_rate or 0


class SocialLinks(models.Model):
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instructor_links"
    )
    link_name = models.CharField(max_length=250)
    link = models.URLField(max_length=250)
    slug = models.SlugField(default="", max_length=1500)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.link_name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Social_Links"

    def __str__(self):
        return f"{self.link_name}"


class Student(User):
    """
    - Instructor profile it will inherit form the profile model
    - it will have the his owen Fields
    """

    enrollments = models.CharField(max_length=500, blank=True, null=True)
    courses_complete = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Student)"
