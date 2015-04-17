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
  pidm = models.CharField(max_length=100)
  cust_code = models.CharField(max_length=100)
  last_name = models.CharField(max_length=100)
  last_name_sdx = models.CharField(max_length=100)
  status_ind = models.CharField(max_length=100)
  start_date = models.CharField(max_length=100)
  activity_date = models.CharField(max_length=100)
  user_id = models.CharField(max_length=100)
  ten99_ind = models.CharField(max_length=100)
  first_name = models.CharField(max_length=100)
  first_name_sdx = models.CharField(max_length=100)
  middle_name = models.CharField(max_length=100)
  middle_name_sdx = models.CharField(max_length=100)
  ssn = models.CharField(max_length=100)
  drivers_license = models.CharField(max_length=100)
  ethn_code = models.CharField(max_length=100)
  credit_rating = models.CharField(max_length=100)
  employer = models.CharField(max_length=100)
  pay_by_check_ind = models.CharField(max_length=100)
  spouses_name = models.CharField(max_length=100)
  end_date = models.CharField(max_length=100)
  bmsg_code = models.CharField(max_length=100)
  ten99_id = models.CharField(max_length=100)
  ten99_wh_pct = models.CharField(max_length=100)
  ten99_state = models.CharField(max_length=100)
  natn_code_d_l = models.CharField(max_length=100)
  stat_code_d_l = models.CharField(max_length=100)
  spouses_ssn = models.CharField(max_length=100)
  ten99_primary_ind = models.CharField(max_length=100)
  title = models.CharField(max_length=100)
  mmbr_type_ind = models.CharField(max_length=100)
  last_name_upr = models.CharField(max_length=100)
  approval_code = models.CharField(max_length=100)
  lrg_prnt_ind = models.CharField(max_length=100)
  lang_code = models.CharField(max_length=100)
  letr_ind = models.CharField(max_length=100)
  birth_date = models.CharField(max_length=100)

