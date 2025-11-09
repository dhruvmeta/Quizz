from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# -------------------------------
# User and User Manager
# -------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        user = self.create_user(email=email, name=name, tc=tc, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True)
    name = models.CharField(max_length=200)
    tc = models.BooleanField(verbose_name="Terms and Conditions Accepted")
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "tc"]

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


# -------------------------------
# Quiz
# -------------------------------
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# -------------------------------
# Question
# -------------------------------
class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short', 'Short Answer'),
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
# -------------------------------
# Answer
# -------------------------------
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'wrong'})"

# -------------------------------
# UserSubmission
# -------------------------------
class UserSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    user_name = models.CharField(max_length=150)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.quiz.title} ({self.score})"

# -------------------------------
# UserAnswer
# -------------------------------
class UserAnswer(models.Model):
    submission = models.ForeignKey(UserSubmission, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

# -------------------------------
# Event
# -------------------------------
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} @ {self.location}"

