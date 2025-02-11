from django.db import models
from django.utils.crypto import get_random_string

from apps.base.models import *

class LandingPage(LabUUID, Base):

    class Meta:
        verbose_name = 'Landing Page'

    def __str__(self):
        return self.nome

