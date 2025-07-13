import uuid
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils.text import slugify
from moviepy import VideoFileClip
from taggit.managers import TaggableManager

from members.models import Instructor, Student

CHOICES_LEVEL =[
  ('Beginner','Beginner'),
  ('Intermediate','Intermediate'),
  ('Advanced','Advanced'),
]

class Category(models.Model):
  name  = models.CharField(max_length=250)
  views = models.PositiveIntegerField()
  slug  = models.SlugField(default = '',unique=True)

  def __str__(self):
    return self.name  

  def save(self,*args,**kwargs):
    if not self.slug:
      self.slug = slugify(self.name)
    super().save(*args,**kwargs)


class Course(models.Model):
  title           = models.CharField(max_length=250)
  description     = models.TextField()
  requirements    = models.TextField(blank=True,null=True)
  image           = models.ImageField(upload_to = 'images/courses/images/')
  promo_video     = models.FileField(upload_to = 'courses/promo_videos/',blank=True,null=True)
  price           = models.DecimalField(max_digits =8,decimal_places=2 ,blank=True,null=True)
  discount_price  = models.DecimalField(max_digits =8,decimal_places=2 ,blank=True,null=True)
  level           = models.CharField(max_length=50,choices=CHOICES_LEVEL,default=CHOICES_LEVEL[0][0])

  is_free         = models.BooleanField(default=False) 
  created_at      = models.DateTimeField(auto_now_add=True)
  updated_at      = models.DateTimeField(auto_now = True)
  published_at    = models.DateTimeField(blank=True, null=True)
  slug            = models.SlugField(default = '',unique=True)
  category        = models.ForeignKey(Category,on_delete = models.CASCADE)
  tags            = TaggableManager() 
  token           = models.CharField(max_length=20,unique=True,blank=True)

  is_puplished    = models.BooleanField(default=False)
  instructor      = models.ForeignKey(Instructor,on_delete=models.CASCADE)
  loves           = models.ManyToManyField(User,blank = True)
  

  def save(self,*args,**kwargs):
    if not self.slug :
      self.slug  = slugify(self.title)
    if not self.token:
      self.token  = uuid.uuid4().hex[:16].upper()
    super().save(*args,**kwargs)
  def __str__(self):
    return f'Course:{self.title}'

  # def get_absolute_url (self):
  #   return reverse('course:course_detail',args=[
  #     self.slug,
  #     self.token,
  #   ])

class LearningOutcomes(models.Model):
  # user when he create course he need to create outcomes with 
  course      = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_outcomes')
  description = models.CharField(max_length=160,verbose_name="Outcome Description",) 
  created_at  = models.DateTimeField(auto_now_add=True)
  updated_at  = models.DateTimeField(auto_now=True)
  slug        = models.SlugField(default='',unique=True)
  def save(self,*args,**kwargs):
    if not self.slug:
      self.slug = slugify(self.description)
    super().save(*args,**kwargs)
  def __str__(self):
    return f'{self.course.title} outcome {self.description}'


class Enrollment(models.Model):
  student         = models.ForeignKey(Student,on_delete=models.CASCADE)
  course          = models.ForeignKey(Course,on_delete=models.CASCADE)
  token           = models.UUIDField(default=uuid.uuid4,editable=False)
  enrollment_date = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"{self.student.first_name} {self.student.last_name} enroll {self.course}"



class Review(models.Model):
  RATING_CHOICES = (
    (1,'1 - Poor'),
    (2,'2 - Fair'),
    (3,'3 - Good'),
    (4,'4 - Vary Good'),
    (5,'5 - Excellent'),
  )

  rating      = models.PositiveSmallIntegerField(choices=RATING_CHOICES,null=True,blank=True)
  user        = models.ForeignKey(Student,on_delete=models.CASCADE)
  course      = models.ForeignKey(Course,on_delete=models.CASCADE)
  created_at  = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Review by {self.user.first_name} {self.user.last_name} for {self.course} ({self.rating}/5)"


class Comment(models.Model):
  course      = models.ForeignKey(Course,on_delete=models.CASCADE)
  user        = models.ForeignKey(User,on_delete=models.CASCADE)
  body        = models.TextField(max_length=300)
  slug        = models.SlugField(default='',unique=True)
  created_at  = models.DateTimeField(auto_now_add=True)
  updated_at  = models.DateTimeField(auto_now=True)

  def save(self,*args,**kwargs):
    if not self.slug :
      self.slug = slugify(self.body[:16])
    super().save(*args,**kwargs)
  
  def __str__(self):
    return f"Comment by {self.user.first_name} {self.user.last_name} for {self.course}"


class Module(models.Model):
  course       = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='modules')

  title        = models.CharField(max_length=255)
  description  = models.TextField(blank=True,null=True)
  is_published = models.BooleanField(default=True)
  created_at   = models.DateTimeField(auto_now_add=True)
  updated_at   = models.DateTimeField(auto_now=True)
  slug         = models.SlugField(default='',unique=True)

  def save(self,*args,**kwargs):
    if not self.slug :
      self.slug = slugify(self.title)
    super().save(*args,**kwargs)

  def __str__(self):
    return self.title


class Lesson (models.Model):
  module          = models.ForeignKey(Module,on_delete=models.CASCADE,related_name='lessons')
  title           = models.CharField(max_length=255)
  thumbnail       = models.ImageField(upload_to = 'courses/videos/lesson_images/')
  video           = models.FileField(upload_to='courses/videos/lesson_videos/') 
  preview         = models.BooleanField(default=False)
  duration        = models.DurationField(blank=True,null=True)
  added_at        = models.DateTimeField(auto_now_add=True)
  slug            = models.SlugField(default='',unique=True)
  token           = models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
  def save(self,*args,**kwargs):
    if not self.slug :
      self.slug = slugify(self.title)
    super().save(*args,**kwargs)
    
    if self.video:
      video_path = self.video.path
      try:
        clip = VideoFileClip(video_path)
        duration_secounds = clip.duration
        clip.close()
        # convert the duration_secounds to timedelta to assign it ot the field
        self.duration = timedelta(seconds=duration_secounds)
        super().save(update_fields=['duration'])
      except Exception as e:
        raise ValueError(f"Error reading video duration: {e}")
  
  def __str__(self):
    return self.title
  

class Contact(models.Model):
  name        = models.CharField(max_length=255)
  email       = models.EmailField(unique=True)
  message     = models.TextField(max_length=500)
  created_at  = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return f"{self.name} {self.email}"