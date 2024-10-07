from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, default='')
    otp_check = models.IntegerField(default=0)
    uid = models.CharField(max_length=500, default="", null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.email}'


class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    payment_date = models.DateField(auto_now_add=True)
    description = models.TextField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_map_id = models.IntegerField(null=True, blank=True)  # New field

    def save(self, *args, **kwargs):
        if self.subscription == 'free':
            self.amount = 0.00
        elif self.subscription == 'monthly':
            self.amount = 4.00
        elif self.subscription == 'yearly':
            self.amount = 29.99
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.name} - {self.subscription}'


class Emotion(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Scores(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='scores')
    image_value = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    general_emotion_value = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    revaluation_one = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    revaluation_two = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    selected_emotions = models.ManyToManyField(Emotion, related_name='current_scores')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_score_record()

    def create_score_record(self):
        score_record = ScoreRecord.objects.create(
            user=self.user,
            image_value=self.image_value,
            general_emotion_value=self.general_emotion_value,
            revaluation_one=self.revaluation_one,
            revaluation_two=self.revaluation_two,
        )
        score_record.selected_emotions.set(self.selected_emotions.all())
        score_record.save()


class ScoreRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='score_records')
    image_value = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    general_emotion_value = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    revaluation_one = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    revaluation_two = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    selected_emotions = models.ManyToManyField(Emotion, related_name='score_records')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        selected_emotions_names = ', '.join([e.name for e in self.selected_emotions.all()])
        return f"{self.user.name} - Image {self.image_value} - General Emotion: {self.general_emotion_value} - Revaluation One: {self.revaluation_one} - Revaluation Two: {self.revaluation_two} - Selected: {selected_emotions_names}"
