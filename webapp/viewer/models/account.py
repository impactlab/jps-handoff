from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import request_finished
from django.utils.safestring import mark_safe
import string, os, fnmatch, csv, datetime, pytz, json, math

class Account(models.Model):
  meter = models.ForeignKey('Meter', related_name='account')
  account = models.CharField('Account number', max_length=100, null=True)
  name = models.CharField('Name', max_length=250, null=True)
  cycle = models.CharField('Cycle', max_length=100, null=True)
  rate = models.CharField('Rate', max_length=100, null=True)
  tou = models.CharField('TOU', max_length=100, null=True)
  addr = models.CharField('Address', max_length=250, null=True)

