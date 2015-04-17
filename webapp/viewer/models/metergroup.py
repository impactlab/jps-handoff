from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import request_finished
from django.utils.safestring import mark_safe
import string, os, fnmatch, csv, datetime, pytz, json, math
import pandas as pd
import numpy as np
from datapoints import ProfileDataPoint, EventDataPoint, MeasurementDataPoint

class MeterGroup(models.Model):
  name = models.CharField(max_length=64)

  def __unicode__(self):
    return unicode(self.name) 
