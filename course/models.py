import uuid
from datetime import timedelta
from django.db.models import Sum, Count, Avg

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from moviepy import VideoFileClip
from taggit.managers import TaggableManager
from members.models import Instructor, Student

CHOICES_LEVEL = [
    ("Beginner", "Beginner"),
    ("Intermediate", "Intermediate"),
    ("Advanced", "Advanced"),
]


class Category(models.Model):
    name = models.CharField(max_length=250)
    views = models.PositiveIntegerField()
    thumbnail = models.ImageField(
        upload_to="images/category_images/", blank=True, null=True
    )
    slug = models.SlugField(default="", unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "course:fetch-courses-by-category",
            args=[
                self.slug,
            ],
        )

    class Meta:
        verbose_name_plural = "Categories"


class Course(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="images/courses/courses_thumbnails/", null=True, blank=True
    )
    image = models.ImageField(upload_to="images/courses/images/")
    promo_video = models.FileField(
        upload_to="courses/promo_videos/", blank=True, null=True
    )
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    level = models.CharField(
        max_length=50, choices=CHOICES_LEVEL, default=CHOICES_LEVEL[0][0]
    )

    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(default="", unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = TaggableManager()
    token = models.CharField(max_length=20, unique=True, blank=True)

    is_puplished = models.BooleanField(default=False)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    loves = models.ManyToManyField(User, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.token:
            self.token = uuid.uuid4().hex[:16].upper()
        if self.discount_price > 0:
            self.price = self.price - self.discount_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Course:{self.title}"

    def get_absolute_url(self):
        return reverse(
            "course:course-detail",
            args=[
                self.slug,
                self.token,
            ],
        )

    @property
    def total_course_duration(self):
        total_duration = self.modules.aggregate(total_hours=Sum("lessons__duration"))
        return total_duration["total_hours"]

    @property
    def discount_percentage(self):
        if self.price and self.discount_price > 0:
            return round(self.discount_price / self.price * 100, 2)
        return 0

    @property
    def avg_rating(self):
        avg_course_rating = self.course_ratings.aggregate(avg_rating=Avg("rate"))[
            "avg_rating"
        ]
        return avg_course_rating or 0


class LearningOutcomes(models.Model):
    # user when he create course he need to create outcomes with
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_outcomes"
    )
    description = models.CharField(
        max_length=160,
        verbose_name="Outcome Description",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="", unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} outcome {self.description}"

    class Meta:
        verbose_name_plural = "Learning OutComes"


class Enrollment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="student_enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_enrollments"
    )

    token = models.UUIDField(default=uuid.uuid4, editable=False)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.student.first_name} {self.student.last_name} enroll {self.course}"
        )


class Rating(models.Model):
    RATING_CHOICES = (
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Vary Good"),
        (5, "5 - Excellent"),
    )

    rate = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, null=True, blank=True
    )
    user = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="user_ratings"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_ratings"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating by {self.user.first_name} {self.user.last_name} for {self.course} ({self.rate}/5)"


class Review(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_reviews"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_reviews"
    )
    body = models.TextField(max_length=300)
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.body[:16])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reviewing by {self.user.first_name} {self.user.last_name} for {self.course}"


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default="", unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def get_total_duration(self):
        total_lessons_duration = self.lessons.aggregate(total=Avg("duration"))
        return total_lessons_duration["total"]


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to="courses/videos/lesson_images/")
    video = models.FileField(upload_to="courses/videos/lesson_videos/")
    is_preview = models.BooleanField(default=False)
    duration = models.DurationField(blank=True, null=True)
    views = models.PositiveBigIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", unique=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        if self.video:
            video_path = self.video.path
            try:
                clip = VideoFileClip(video_path)
                duration_secounds = clip.duration
                clip.close()
                # convert the duration_secounds to timedelta to assign it ot the field
                self.duration = timedelta(seconds=duration_secounds)
                super().save(update_fields=["duration"])
            except Exception as e:
                raise ValueError(f"Error reading video duration: {e}")

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"{self.name} {self.email}"
