from django.db import models
from django.utils import timezone
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================
# Custom User Model
# ==========================
class CustomerUser(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
    )

    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    dob = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

# ==========================
# Application Categories
# ==========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# ==========================
# Applications
# ==========================
class Application(models.Model):
    name = models.CharField(max_length=150)
    link = models.URLField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="app_images/", blank=True, null=True)
    added_on = models.DateTimeField(default=timezone.now)
    rating = models.FloatField(default=5.0)     
    avg_sentiment_score = models.FloatField(default=0.0) # Average sentiment score
    is_fraud = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # Method to update avg_rating and avg_sentiment_score
    def update_metrics(self):
        reviews = self.review_set.all()
        self.avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        self.avg_sentiment_score = reviews.aggregate(avg=Avg('sentiment_score'))['avg'] or 0
        self.save()

# ==========================
# Reviews by Users
# ==========================
class Review(models.Model):
    SENTIMENT_CHOICES = (
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    )

    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(default=0)  # 1-5 scale
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)  # -1 to 1 score
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_fake = models.BooleanField(default=False)  # Fake review detection
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.app.name}"


# ==========================
# Update avg_rating & sentiment_score after each review
# ==========================
@receiver(post_save, sender=Review)
def update_app_metrics(sender, instance, **kwargs):
    instance.app.update_metrics()


# ==========================
# Feedback from Users
# ==========================
class Feedback(models.Model):
    user = models.ForeignKey(CustomerUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Feedback by {self.user.username}"

# ==========================
# Admin Logs for Monitoring
# ==========================
class AdminReviewLog(models.Model):
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    admin = models.ForeignKey(CustomerUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'status': 'active'})
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)  # e.g., "Marked Fraud", "Removed Review"
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.app.name} - {self.action}"
