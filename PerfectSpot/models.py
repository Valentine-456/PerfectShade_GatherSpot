from django.contrib.auth.models import AbstractUser
from django.db import models

# general custom user to avoid using django one for future implementations with no problems
# users are distinguished through types of users, is_org_verified, etc
# this way the db will contain everything and the admin will be able to filter what they need

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('organization', 'Organization'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_email_verified = models.BooleanField(default=False)

    # Organization-specific
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    verification_document = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    is_org_verified = models.BooleanField(
        default=False,
        help_text="Admin-approved verification of organization documents"
    )

    friends = models.ManyToManyField('self', blank=True, symmetrical=True)

    def __str__(self):
        return self.username

# event model roughly
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events')
    is_promoted = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    attendees = models.ManyToManyField('CustomUser', blank=True, related_name='attending_events')

    def __str__(self):
        return self.title

# review model roughly
class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.event.title}"



# not sure if it should be separate thing or just an additional criteria of the user
# for now let's separate it through for better ui

# proxy for org
class OrganizationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type='organization')

class OrganizationProxy(CustomUser):
    objects = OrganizationManager()

    class Meta:
        proxy = True
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'


# proxy for individual
class IndividualUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user_type='individual')

class IndividualUserProxy(CustomUser):
    objects = IndividualUserManager()

    class Meta:
        proxy = True
        verbose_name = 'Individual User'
        verbose_name_plural = 'Individual Users'

