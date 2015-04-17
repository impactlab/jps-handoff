from django.shortcuts import render
from django.contrib.auth.views import login
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404, render, render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.template import RequestContext
from django.forms.models import modelform_factory
from django_tables2 import RequestConfig
from django import forms
import json, re
from django.db.models import Q
from models import *

from viewer import models

def home(request):
  context = {}

  queryset = Meter.objects.filter(total_usage__gt=0)
  if ('q' in request.GET) and request.GET['q'].strip():
    query_string = request.GET['q']
    q = Q(**{"meter_id__icontains": query_string})
    queryset = queryset.filter(q)

  if ('g' in request.GET) and request.GET['g'].strip():
    query_string = request.GET['g']
    q = Q(**{"metergroups__name__icontains": query_string})
    queryset = queryset.filter(q)

  table = MeterTable(queryset)
  RequestConfig(request, paginate={'per_page': 100}).configure(table)
  context['table'] = table

  t = loader.get_template('viewer/home.html')
  c = RequestContext(request,context)
  return HttpResponse(t.render(c))

def profile(request):
  return render(request, template_name='viewer/profile.html')

def meter_detail(request, id):
  meter = Meter.objects.get(id=id)

  if ('rmgroup' in request.GET) and request.GET['rmgroup'].strip():
    try:
      group = MeterGroup.objects.get(name=request.GET['rmgroup'])
      meter.metergroups.remove(group)
      if group.meter_set.count() == 0:
        group.delete()
    except:
      pass

  if ('addgroup' in request.GET) and request.GET['addgroup'].strip():
    group = None
    try:
      group = MeterGroup.objects.get(name=request.GET['addgroup'])
    except:
      group = MeterGroup.objects.create(name=request.GET['addgroup'])
    meter.metergroups.add(group)

  context = {'meter': meter, 'groups': MeterGroup.objects,
             'ami_heatmap_data': meter.format_ami_data(fmt='json-grid'),
             'recent_preview_data': meter.format_ami_data(fmt='json'),
             'events_data': meter.events_data(),
             'meas_diag_data': meter.meas_diag_data()}
  return render(request, 'viewer/meter_detail.html', context)

def auditlist(request):
  if request.method == 'POST':
    pks = [int(i) for i in request.POST.getlist('auditVisible')]
    queryset = Meter.objects.filter(pk__in=pks)
    pks = [int(i) for i in request.POST.getlist('audit')]
    queryset.filter(pk__in=pks).update(on_auditlist=True)
    queryset.exclude(pk__in=pks).update(on_auditlist=False)
  return HttpResponseRedirect(reverse('home'))

def clear_auditlist(request):
  Meter.objects.all().update(on_auditlist=False)
  return HttpResponseRedirect(reverse('home'))

def download_auditlist(request):
  meters = Meter.objects.filter(on_auditlist=True)
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="AuditList.csv"'
  f = csv.writer(response)
  for m in meters:
    f.writerow([m.meter_id, m.overall_score, m.total_usage])
  return response

def download_summary(request):
  meters = Meter.objects.all()
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="AuditList.csv"'
  f = csv.writer(response)
  for m in meters:
    f.writerow([m.meter_id, m.overall_score, m.total_usage, m.on_auditlist])
  return response

def download_meter(request, id):
  m = Meter.objects.get(id=id)
  response = HttpResponse(content_type='text/csv')
  response['Content-Disposition'] = 'attachment; filename="'+m.meter_id+'.csv"'
  f = csv.writer(response)
  f.writerow(['Profile'])
  f.writerow(['time','kw','kva'])
  for row in m.format_ami_data(fmt='csv'):
    f.writerow(row)
  f.writerow([''])
  f.writerow(['Event'])
  f.writerow(['time','event'])
  for row in m.format_event_data(fmt='csv'):
    f.writerow(row)
  f.writerow([''])
  f.writerow(['Measurement and Diagnostic'])
  for k,v in m.meas_diag_data().iteritems():
    f.writerow([k,v])
  return response

def get_groups(request):
  q = request.GET.get('term', '')
  groups = MeterGroup.objects.filter(name__icontains = q )[:20]
  results = []
  for group in groups:
    group_json = {}
    group_json['id'] = group.id
    group_json['label'] = group.name
    group_json['value'] = group.name
    results.append(group_json)
  data = json.dumps(results)
  mimetype = 'application/json'
  return HttpResponse(data, mimetype)

