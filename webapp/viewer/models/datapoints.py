from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.signals import request_finished
import string, os, fnmatch, csv, datetime, pytz, json, math
import pandas as pd
import numpy as np

class EventDataPoint(models.Model):
  meter = models.ForeignKey('Meter', related_name='events')
  ts = models.DateTimeField()
  event = models.CharField(max_length=200)

class ProfileDataPoint(models.Model):
  meter = models.ForeignKey('Meter', related_name='profile_points')
  ts = models.DateTimeField()
  kw = models.FloatField()
  kva = models.FloatField() 

class MeasurementDataPoint(models.Model):
  meter = models.ForeignKey('Meter', related_name='measurement_points')
  ts = models.DateTimeField()
  time_of_last_interrogation = models.DateTimeField(null=True)
  time_of_last_outage = models.DateTimeField(null=True)

  phase_a_voltage = models.FloatField()
  phase_a_current = models.FloatField()
  phase_a_current_angle = models.FloatField()
  phase_a_dc_detect = models.FloatField()
  phase_b_voltage = models.FloatField()
  phase_b_voltage_angle = models.FloatField()
  phase_b_current = models.FloatField()
  phase_b_current_angle = models.FloatField()
  phase_b_dc_detect = models.FloatField()
  phase_c_voltage = models.FloatField()
  phase_c_voltage_angle = models.FloatField()
  phase_c_current = models.FloatField()
  phase_c_current_angle = models.FloatField()
  phase_c_dc_detect = models.FloatField()

  abc_phase_rotation = models.IntegerField()

  daylight_savings_time_configured = models.NullBooleanField()
  low_battery_error = models.NullBooleanField()
  metrology_communications_fatal_error = models.NullBooleanField()
  inactive_phase = models.NullBooleanField()
  file_system_fatal_error = models.NullBooleanField()
  voltage_deviation = models.NullBooleanField()
  phase_angle_displacement = models.NullBooleanField()
  slc_error = models.NullBooleanField()
  tou_schedule_error = models.NullBooleanField()
  reverse_power_flow_error = models.NullBooleanField()
  register_full_scale_exceeded_error = models.NullBooleanField()
  epf_data_fatal_error = models.NullBooleanField()
  demand_threshold_exceeded_error = models.NullBooleanField()
  metrology_communications_error = models.NullBooleanField()
  ram_fatal_error = models.NullBooleanField()
  phase_loss_error = models.NullBooleanField()
  mass_memory_error = models.NullBooleanField()
  cross_phase_flow = models.NullBooleanField()
  current_waveform_distorsion = models.NullBooleanField()
  mcu_flash_fatal_error = models.NullBooleanField()
  data_flash_fatal_error = models.NullBooleanField()
  clock_sync_error = models.NullBooleanField()
  site_scan_error = models.NullBooleanField()

  diag_count_2 = models.IntegerField()
  diag_count_3 = models.IntegerField()
  diag_count_4 = models.IntegerField()
  diag_5_phase_b_count = models.IntegerField()
  diag_5_phase_a_count = models.IntegerField()
  diag_5_phase_c_count = models.IntegerField()
  times_programmed_count = models.IntegerField()
  early_power_fail_count = models.IntegerField()
  power_outage_count = models.IntegerField()
  good_battery_reading = models.IntegerField()
  demand_reset_count = models.IntegerField()
  demand_interval_length = models.IntegerField()
  current_battery_reading = models.IntegerField()
  current_season = models.IntegerField()
  days_since_demand_reset = models.IntegerField()
  days_since_last_test = models.IntegerField()
  days_on_battery = models.IntegerField()
  service_type_detected = models.IntegerField()
  diag_count_1 = models.IntegerField()
  diag_count_5 = models.IntegerField()
