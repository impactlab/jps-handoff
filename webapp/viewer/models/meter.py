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
from metergroup import MeterGroup
from account import Account

class Meter(models.Model):
  meter_id = models.CharField(max_length=32)
  overall_score = models.FloatField(default=0.0)
  on_auditlist = models.BooleanField(default=False)
  total_usage = models.FloatField(default=0.0)
  metergroups = models.ManyToManyField(MeterGroup, verbose_name='Groups')

  def update_total_usage(self, start_date=None):
    if self.profile_points.count() == 0: 
      self.total_usage = 0
      return
    if start_date is None:
      tslast = self.profile_points.order_by('-ts')[0].ts
      start_date = tslast - datetime.timedelta(days=30)
    raw = [i for i in reversed(self.profile_points.\
           filter(ts__gte=start_date).order_by('-ts'))]
    s = pd.Series([i.kw for i in raw], index=[i.ts for i in raw])
    s = s.resample('60T').dropna()
    self.total_usage = int(s.sum())

  def __unicode__(self):
    return unicode(self.meter_id)

  def get_absolute_url(self):
    return reverse('detail', kwargs={'id': self.id})

  def _load_data(self, dir='/data/extract', turbo=False):
    tz = pytz.timezone('America/Jamaica')
    for f in os.listdir(dir):
      if fnmatch.fnmatch(f, self.meter_id+'__*'):
        with open(dir+'/'+f, 'r') as myf:
          fcsv = csv.reader(myf)
          linecount = 0
          for line in fcsv:
            ts = datetime.datetime.strptime(line[1], '%Y/%m/%d %H:%M')
            ts = ts.replace(tzinfo=tz)
            if not turbo:
              try: 
                dp = ProfileDataPoint.objects.get(\
                  meter=self, ts=ts, \
                  kw=float(line[2]), kva=float(line[3]))
              except:
                ProfileDataPoint.objects.create(\
                  meter=self, ts=ts, \
                  kw=float(line[2]), kva=float(line[3]))
            else:
              ProfileDataPoint.objects.create(\
                meter=self, ts=ts, \
                kw=float(line[2]), kva=float(line[3]))
            linecount = linecount + 1
    return True if linecount > 0 else False


  def _load_event_data(self, dir='/data/extract', turbo=False):
    tz = pytz.timezone('America/Jamaica')
    for f in os.listdir(dir):
      if fnmatch.fnmatch(f, 'evt__'+self.meter_id+'__*'):
        with open(dir+'/'+f, 'r') as myf:
          fcsv = csv.reader(myf)
          h = fcsv.next()
          for line in fcsv:
            if len(line) <= 1: continue
            ts = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S')
            ts = ts.replace(tzinfo=tz)
            if not turbo:
              try: 
                dp = EventDataPoint.objects.get(\
                  meter=self, ts=ts, \
                  event=line[2])
              except:
                EventDataPoint.objects.create(\
                  meter=self, ts=ts, \
                  event=line[2])
            else:
              EventDataPoint.objects.create(\
                meter=self, ts=ts, \
                event=line[2])
    return True

  def _load_account_data(self, filename):
    with open(filename, 'r') as myf:
      fcsv = csv.reader(myf)
      header = fcsv.next()
      for line in fcsv:
        if line[0] == self.meter_id:
          try: 
            a = Account.objects.get(meter=self)
          except:
            a = Account(meter=self)
          a.pidm = line[1]
          a.cust_code = line[2]
          a.last_name = line[3]
          a.last_name_sdx = line[4]
          a.status_ind = line[5]
          a.start_date = line[6]
          a.activity_date = line[7]
          a.user_id = line[8]
          a.ten99_ind = line[9]
          a.first_name = line[10]
          a.first_name_sdx = line[11]
          a.middle_name = line[12]
          a.middle_name_sdx = line[13]
          a.ssn = line[14]
          a.drivers_license = line[15]
          a.ethn_code = line[16]
          a.credit_rating = line[17]
          a.employer = line[18]
          a.pay_by_check_ind = line[19]
          a.spouses_name = line[20]
          a.end_date = line[21]
          a.bmsg_code = line[22]
          a.ten99_id = line[23]
          a.ten99_wh_pct = line[24]
          a.ten99_state = line[25]
          a.natn_code_d_l = line[26]
          a.stat_code_d_l = line[27]
          a.spouses_ssn = line[28]
          a.ten99_primary_ind = line[29]
          a.title = line[30]
          a.mmbr_type_ind = line[31]
          a.last_name_upr = line[32]
          a.approval_code = line[33]
          a.lrg_prnt_ind = line[34]
          a.lang_code = line[35]
          a.letr_ind = line[36]
          a.birth_date = line[37]
          a.save()
          return True
      return False

  def _load_measurement_data(self, filename):
    with open(filename, 'r') as myf:
      fcsv = csv.reader(myf)
      header = fcsv.next()
      for line in fcsv:
        if line[0] == self.meter_id:
          try:
            ts = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S')
          except:
            continue
          tz = pytz.timezone('America/Jamaica')
          ts = ts.replace(tzinfo=tz)
          try: 
            dp = MeasurementDataPoint.objects.get(\
              meter=self, ts=ts)
          except:
            dp = MeasurementDataPoint(\
              meter=self, ts=ts)
          for h,d in zip(header, line):
            if h=='DeviceId' or h=='Code': pass
            elif h=="Time Of Last Interrogation": 
              if d=='': continue
              ts = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
              ts = ts.replace(tzinfo=tz)
              dp.time_of_last_interrogation = ts
            elif h=="Time Of Last Outage": 
              if d=='': continue
              ts = datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
              ts = ts.replace(tzinfo=tz)
              dp.time_of_last_outage = ts
            elif h=="Phase B Current angle": dp.phase_b_current_angle = float(d)
            elif h=="Daylight Savings Time Configured": dp.daylight_savings_time_configured = True if d=='True' else False
            elif h=="Low Battery Error": dp.low_battery_error = True if d=='True' else False
            elif h=="Metrology Communications Fatal Error": dp.metrology_communications_fatal_error = True if d=='True' else False
            elif h=="Diagnostic Error (Inactive Phase)": dp.inactive_phase = True if d=='True' else False
            elif h=="Diag Count 3": dp.diag_count_3 = int(d)
            elif h=="Diag Count 4": dp.diag_count_4 = int(d)
            elif h=="Times Programmed Count": dp.times_programmed_count = int(d)
            elif h=="Early Power Fail Count": dp.early_power_fail_count = int(d)
            elif h=="Good Battery Reading": dp.good_battery_reading = int(d)
            elif h=="File System Fatal Error": dp.file_system_fatal_error = True if d=='True' else False
            elif h=="Diag Count 2": dp.diag_count_2 = int(d)
            elif h=="Phase A Current": dp.phase_a_current = float(d)
            elif h=="Phase A Current angle": dp.phase_a_current_angle = float(d)
            elif h=="ABC PHASE Rotation": dp.abc_phase_rotation = int(d)
            elif h=="Diagnostic Error (Voltage Deviation)": dp.voltage_deviation = True if d=='True' else False
            elif h=="Diagnostic Error (Phase Angle Displacement)": dp.phase_angle_displacement = True if d=='True' else False
            elif h=="Power Outage Count": dp.power_outage_count = int(d)
            elif h=="SLC Error": dp.slc_error = True if d=='True' else False
            elif h=="Phase B Voltage": dp.phase_b_voltage = float(d)
            elif h=="Phase B Voltage angle": dp.phase_b_voltage_angle = float(d)
            elif h=="Phase C Voltage angle": dp.phase_c_voltage_angle = float(d)
            elif h=="Phase C Current angle": dp.phase_c_current_angle = float(d)
            elif h=="Phase A DC Detect": dp.phase_a_dc_detect = float(d)
            elif h=="Demand Reset Count": dp.demand_reset_count = int(d)
            elif h=="TOU Schedule Error": dp.tou_schedule_error = True if d=='True' else False
            elif h=="Reverse Power Flow Error": dp.reverse_power_flow_error = True if d=='True' else False
            elif h=="Diag 5 Phase B Count": dp.diag_5_phase_b_count = int(d)
            elif h=="Demand Interval Length": dp.demand_interval_length = int(d)
            elif h=="Phase B DC Detect": dp.phase_b_dc_detect = float(d)
            elif h=="Register Full Scale Exceeded Error": dp.register_full_scale_exceeded_error = True if d=='True' else False
            elif h=="EPF Data Fatal Error": dp.epf_data_fatal_error = True if d=='True' else False
            elif h=="Phase A Voltage": dp.phase_a_voltage = float(d)
            elif h=="Phase B Current": dp.phase_b_current = float(d)
            elif h=="Phase C Current": dp.phase_c_current = float(d)
            elif h=="Current Battery Reading": dp.current_battery_reading = int(d)
            elif h=="Demand Threshold Exceeded Error": dp.demand_threshold_exceeded_error = True if d=='True' else False
            elif h=="Metrology Communications Error": dp.metrology_communications_error = True if d=='True' else False
            elif h=="RAM Fatal Error": dp.ram_fatal_error = True if d=='True' else False
            elif h=="Diag 5 Phase A Count": dp.diag_5_phase_a_count = int(d)
            elif h=="Diag 5 Phase C Count": dp.diag_5_phase_c_count = int(d)
            elif h=="Current Season": dp.current_season = int(d)
            elif h=="Phase C DC Detect": dp.phase_c_dc_detect = float(d)
            elif h=="Days Since Demand Reset": dp.days_since_demand_reset = int(d)
            elif h=="Days Since Last Test": dp.days_since_last_test = int(d)
            elif h=="Days On Battery": dp.days_on_battery = int(d)
            elif h=="Phase Loss Error": dp.phase_loss_error = True if d=='True' else False
            elif h=="Mass Memory Error": dp.mass_memory_error = True if d=='True' else False
            elif h=="Diagnostic Error (Cross Phase Flow)": dp.cross_phase_flow = True if d=='True' else False
            elif h=="Diagnostic Error (Current Waveform Distorsion)": dp.current_waveform_distorsion = True if d=='True' else False
            elif h=="Phase C Voltage": dp.phase_c_voltage = float(d)
            elif h=="Service Type Detected": dp.service_type_detected = int(d)
            elif h=="MCU Flash Fatal Error": dp.mcu_flash_fatal_error = True if d=='True' else False
            elif h=="Data Flash Fatal Error": dp.data_flash_fatal_error = True if d=='True' else False
            elif h=="Diag Count 1": dp.diag_count_1 = int(d)
            elif h=="Diag Count 5": dp.diag_count_5 = int(d)
            elif h=="Clock Sync Error": dp.clock_sync_error = True if d=='True' else False
            elif h=="Site Scan Error": dp.site_scan_error = True if d=='True' else False
            else: print 'XXX '+h+' unrecognized'
          dp.save()
    return True

  def meas_diag_data(self, date=None):
    if self.measurement_points.count()==0:
      return {}
    if date is None:
      ts = self.measurement_points.order_by('-ts')[0].ts
    else:  
      ts = self.measurement_points.filter(ts__lt=date).order_by('-ts')[0].ts
    mp = self.measurement_points.get(ts=ts)
    return { 'phase_a_voltage': mp.phase_a_voltage,
             'phase_a_current': mp.phase_a_current,
             'phase_a_current_angle': mp.phase_a_current_angle,
             'phase_b_voltage': mp.phase_b_voltage,
             'phase_b_voltage_angle': mp.phase_b_voltage_angle,
             'phase_b_current': mp.phase_b_current,
             'phase_b_current_angle': mp.phase_b_current_angle,
             'phase_c_voltage': mp.phase_c_voltage,
             'phase_c_voltage_angle': mp.phase_c_voltage_angle,
             'phase_c_current': mp.phase_c_current,
             'phase_c_current_angle': mp.phase_c_current_angle,
             'max_voltage': max([mp.phase_a_voltage, mp.phase_b_voltage,\
                                 mp.phase_c_voltage, 0]),
             'max_current': max([mp.phase_a_current, mp.phase_b_current,\
                                 mp.phase_c_current, 0]),
             'pf_a': math.cos(mp.phase_a_current_angle*math.pi/180.0),
             'pf_b': math.cos((mp.phase_b_voltage_angle-
                               mp.phase_b_current_angle)*math.pi/180.0),
             'pf_c': math.cos((mp.phase_c_voltage_angle-
                               mp.phase_c_current_angle)*math.pi/180.0),
             'cross_phase_flow': str(mp.cross_phase_flow),
             'voltage_deviation': str(mp.voltage_deviation),
             'inactive_phase': str(mp.inactive_phase),
             'phase_angle_displacement': str(mp.phase_angle_displacement),
             'current_waveform_distorsion': str(mp.current_waveform_distorsion),
             'low_battery_error': str(mp.low_battery_error),
             'mass_memory_error': str(mp.mass_memory_error),
             'phase_loss_error': str(mp.phase_loss_error),
             'reverse_power_flow_error': str(mp.reverse_power_flow_error),
             'site_scan_error': str(mp.site_scan_error),
             'tou_schedule_error': str(mp.tou_schedule_error),
    }
    

  def events_data(self, start_date=None):
    if self.profile_points.count()==0: return None
    if start_date is None:
      tslast = self.profile_points.order_by('-ts')[0].ts
      start_date = tslast - datetime.timedelta(days=30)
    data = [{'date': i.ts.strftime('%Y-%m-%d %H:%M:%S'), 'text': i.event}
              for i in reversed(\
                self.events.filter(ts__gte=start_date).\
                order_by('-ts'))] 
    return json.dumps(data)
           

  def format_ami_data(self, start_date=None, fmt='json'):
    if self.profile_points.count() == 0: return None
    if start_date is None:
      tslast = self.profile_points.order_by('-ts')[0].ts
      start_date = tslast - datetime.timedelta(days=30)
    if fmt=='json':
      data = [{'date': i.ts.strftime('%Y-%m-%d %H:%M'), 'reading': i.kw}
              for i in reversed(\
                self.profile_points.filter(ts__gte=start_date).\
                order_by('-ts'))] 
      return json.dumps(data)
    elif fmt=='json-grid':
      raw = [i for i in reversed(self.profile_points.\
             filter(ts__gte=start_date).order_by('-ts'))]
      s = pd.Series([i.kw for i in raw], index=[i.ts for i in raw])
      data = [{'date': d.strftime('%Y-%m-%d'), 
               'time': d.strftime('%H:%M'),
               'reading': v} for d,v in \
               s.resample('15T').dropna().iteritems()]
      return json.dumps(data)
    elif fmt=='csv':
      data = [[i.ts.strftime('%Y-%m-%d %H:%M'), i.kw, i.kva] \
              for i in reversed(\
                self.profile_points.filter(ts__gte=start_date).\
                order_by('-ts'))] 
      return data


  def format_event_data(self, start_date=None, fmt='json'):
    if start_date is None:
      tslast = self.profile_points.order_by('-ts')[0].ts
      start_date = tslast - datetime.timedelta(days=30)
    if fmt=='json':
      data = [{'date': i.ts.strftime('%Y-%m-%d %H:%M'), 'event': i.event}
              for i in reversed(\
                self.events.filter(ts__gte=start_date).\
                order_by('-ts'))] 
      return json.dumps(data)
    if fmt=='json-grid':
      raw = [i for i in reversed(self.profile_points.\
             filter(ts__gte=start_date).order_by('-ts'))]
      s = pd.Series([1 for i in raw], index=[i.ts for i in raw])
      s = s.resample('15T', how='sum')
      s[np.isnan(s)] = 0
      data = [{'date': d.strftime('%Y-%m-%d'), 
               'time': d.strftime('%H:%M'),
               'reading': v} for d,v in \
               s.iteritems()]
      return json.dumps(data)
    if fmt=='csv':
      data = [[i.ts.strftime('%Y-%m-%d %H:%M'), i.event]
              for i in reversed(\
                self.events.filter(ts__gte=start_date).\
                order_by('-ts'))] 
      return data


import django_tables2 as tables
from django_tables2.utils import A

class MeterTable(tables.Table):
  meter_id = tables.LinkColumn('meter_detail', args=[A('pk')])
  overall_score = tables.Column()
  total_usage = tables.Column()
  groups = tables.Column(empty_values=(), orderable=False)
  audit = tables.CheckBoxColumn(accessor="pk", orderable=True,
                                order_by=('-on_auditlist','overall_score'),
    attrs={'th__input': {'type':"text", 'value':"Audit list", 
                         'readonly':None, 'style': 'border: none'},
           'td': {'width':'50px'}})

  class Meta:
    model = Meter
    fields = ( 'meter_id', 'overall_score', 'total_usage', 'audit', 'groups' )

  def render_audit(self, record):
    if record.on_auditlist:
      return mark_safe('<input class="auditCheckBox" name="audit" value="'+str(record.pk)+'" type="checkbox" checked/> <input type="hidden" value="'+str(record.pk)+'"" name="auditVisible"/>')
    else:   
      return mark_safe('<input class="auditCheckBox" name="audit" value="'+str(record.pk)+'" type="checkbox"/> <input type="hidden" value="'+str(record.pk)+'"" name="auditVisible"/>')

  def render_overall_score(self, record):
    return '%5.2f' % (record.overall_score,)

  def render_total_usage(self, record):
    return '{:,.0f} kWh'.format(record.total_usage)

  def render_groups(self, record):
    retval = ''
    for i in record.metergroups.all():
      retval = retval + i.name + ', '
    if retval == '': return retval
    return retval[:-2]
