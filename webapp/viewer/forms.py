from django import forms
from django_select2 import fields, widgets
 
from models import Group
 
class GroupChoices(fields.AutoModelSelect2TagField):
    queryset = Group.objects
    search_fields = ['name__icontains', ]
    def get_model_field_values(self, value):
        return {'tag': value}
 
class GroupFilterForm(forms.Form):
    groups = GroupChoices()

    class Meta:
        model = Group
