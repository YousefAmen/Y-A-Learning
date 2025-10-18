import uuid
from datetime import timedelta
from django.db.models import Sum, Count, Avg

from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from moviepy import VideoFileClip
from taggit.managers import TaggableManager
from members.models import Instructor, Student
from cloudinary.models import CloudinaryField
import cloudinary.api
from main import settings

CHOICES_CATEGORIES = [
    ("Development & Programming", "Development & Programming"),
    ("Business & Management", "Business & Management"),
    ("Finance & Accounting", "Finance & Accounting"),
    ("IT & Software", "IT & Software"),
    ("Design", "Design"),
    ("Marketing", "Marketing"),
    ("Personal Development", "Personal Development"),
    ("Photography & Video", "Photography & Video"),
    ("Music & Audio", "Music & Audio"),
    ("Health & Fitness", "Health & Fitness"),
    ("Teaching & Academics", "Teaching & Academics"),
    ("Language Learning", "Language Learning"),
    ("Data Science & Analytics", "Data Science & Analytics"),
    (
        "Artificial Intelligence & Machine Learning",
        "Artificial Intelligence & Machine Learning",
    ),
    ("Cloud Computing & DevOps", "Cloud Computing & DevOps"),
    ("Cybersecurity", "Cybersecurity"),
    ("Engineering", "Engineering"),
    ("Science & Mathematics", "Science & Mathematics"),
    ("Social Sciences", "Social Sciences"),
    ("Humanities", "Humanities"),
    ("Lifestyle", "Lifestyle"),
    ("Cooking & Culinary Arts", "Cooking & Culinary Arts"),
    ("Arts & Crafts", "Arts & Crafts"),
    ("Beauty & Makeup", "Beauty & Makeup"),
    ("Sports", "Sports"),
    ("Travel & Adventure", "Travel & Adventure"),
    ("Test Preparation", "Test Preparation"),
    ("Career Development", "Career Development"),
    ("Parenting & Relationships", "Parenting & Relationships"),
]

CHOICES_LEVEL = [
    ("Beginner", "Beginner"),
    ("Intermediate", "Intermediate"),
    ("Advanced", "Advanced"),
]


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        choices=CHOICES_CATEGORIES,
        default="Development & Programming",
    )

    slug = models.SlugField(default="", unique=True, max_length=500)

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

    image = CloudinaryField(
        "image",
        resource_type="image",
    )
    promo_video = CloudinaryField("video", resource_type="video")
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
    slug = models.SlugField(default="", unique=True, max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = TaggableManager()
    token = models.CharField(max_length=20, unique=True, blank=True)

    is_puplished = models.BooleanField(default=False)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="instructor_courses"
    )
    loves = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if not self.token:
            self.token = uuid.uuid4().hex[:16].upper()

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
    def discount(self):
        if self.discount_price and self.discount_price > 0:
            return max(0, self.price - self.discount_price)

    @property
    def total_course_duration(self):
        total_duration = self.modules.aggregate(total_hours=Sum("lessons__duration"))
        return total_duration["total_hours"]

    @property
    def discount_percentage(self):
        if self.price and self.discount_price and self.discount_price > 0:
            return round(self.discount_price / self.price * 100, 2)
        return 0

    @property
    def avg_rating(self):
        avg_course_rating = self.course_reviews.aggregate(avg_rating=Avg("rate"))[
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
    slug = models.SlugField(default="", unique=True, max_length=500)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.description)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} outcome {self.description}"

    class Meta:
        verbose_name_plural = "Learning OutComes"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_enrollments",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_enrollments"
    )

    token = models.UUIDField(default=uuid.uuid4, editable=False)
    enrollment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} enroll {self.course}"


class Review(models.Model):
    RATING_CHOICES = (
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Vary Good"),
        (5, "5 - Excellent"),
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="course_reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_reviews"
    )

    rate = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, null=True, blank=True
    )
    body = models.TextField(max_length=300)
    slug = models.SlugField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        self.slug = slugify(self.body)
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
    slug = models.SlugField(default="", max_length=500)

    def save(self, *args, **kwargs):
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
    video = CloudinaryField("video", resource_type="video")
    is_preview = models.BooleanField(default=False)
    duration = models.DurationField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default="", max_length=500)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        if self.video:
            try:
                public_id = self.video.public_id
                resource = cloudinary.api.resource(
                    public_id,
                    resource_type="video",
                    media_metadata=True,
                )

                seconds = int(resource.get("duration", 0))
                if seconds > 0:
                    self.duration = timedelta(seconds=seconds)

                    super().save(update_fields=["duration"])

            except Exception as e:
                print("Error fetching video duration:", e)

    def __str__(self):
        return self.title


class Contact(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    subject = models.CharField(max_length=250)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"{self.name} {self.email}"
