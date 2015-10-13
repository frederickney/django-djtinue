from django.db import models

from djtools.fields import BINARY_CHOICES
from djforms.processors.models import Contact


class Registration(Contact):

    phone_home = models.CharField(
        verbose_name='Home phone',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX"
    )
    phone_work = models.CharField(
        verbose_name='Work phone',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX",
        null=True, blank=True
    )
    email_work = models.EmailField(
        "Work email",
        max_length=128,
        null=True, blank=True
    )
    date_of_birth = models.DateField(
        "Date of birth",
        help_text="Format: mm/dd/yyyy"
    )
    social_security_number = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    social_security_four = models.CharField(
        max_length=4,
        null=True, blank=True
    )
    attended_before = models.CharField(
        "Have you attended Carthage in the past?", max_length=3,
        choices=BINARY_CHOICES
    )
    collegeid = models.CharField(
        "College ID number",
        max_length=8,
        null=True, blank=True
    )
    verify = models.BooleanField(
        """
            I understand that courses offered and/or taken through Carthage's
            Enrichment program cannot be applied toward any undergraduate or
            graduate degree at Carthage.
        """,
        default=False
    )

    class Meta:
        db_table = 'djtinue_enrichment_registration'

class Course(models.Model):

    title = models.CharField(
        max_length=255
    )
    course_number = models.CharField(
        max_length=128
    )
    abstract = models.TextField()
    credits = models.IntegerField(
        max_length=2
    )
    audience = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    instructors = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    dates = models.CharField(
        max_length=255,
        null=True, blank=True
    )
    room = models.CharField(
        max_length=128,
        null=True, blank=True
    )

    class Meta:
        db_table = 'djtinue_enrichment_course'
