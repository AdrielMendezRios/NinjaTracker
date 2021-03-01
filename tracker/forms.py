from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from django import forms 
from .models import Session, Ninja
from django.forms.widgets import HiddenInput
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField, Textarea, CharField, TextInput, EmailField, DateTimeField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Select, CheckboxInput, DateInput, NumberInput
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelChoiceField
from .models import Dojo, Ninja, Employee
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker




DURATION_CHOICES = [('1',_('One Hour')), ('2',_('two Hours'))]
BELT_CHOICES = [('WHT', 'white'), ('YLW', 'Yellow'), ('ORG', 'Orange'), ('GRN', 'Green'), ('BLU', 'Blue'), ('PRP', 'Purple'), ('BRW', 'Brown'), ('RED', 'Red'), ('BLK', 'Black')]
PACKAGE_CHOICES = [('Create Standard', 'Create Standard (8 hrs/m)'), ('Create Lite', 'Create Lite (4 hrs/m)')]

class DateInput(forms.DateInput):
    input_type = 'date'



class BankWithdrawalForm(forms.Form):
    withdrawal_amount = forms.IntegerField(label='Withdrawal Amount')

class BankDepositForm(forms.Form):
    deposit_amount = forms.IntegerField(label='Deposit Amount')

class SessionForm(ModelForm):
    session_notes = CharField(widget=Textarea)
    # session_duration = ChoiceField(widget=RadioSelect(attrs={'class':'form-check form-check-radio form-check-inline', 'type':'radio', 'name':'inlineRadioOption'}), choices=DURATION_CHOICES)
    session_dojo = ModelChoiceField(queryset=Dojo.objects.all(), widget=Select())
    # session_date = DateTimeField(widget=HiddenInput)
    class Meta:
        model = Session
        exclude = ['session_date', 'session_is_approved']
        # fields = '__all__'
        widgets = {
            'session_date': HiddenInput(),
            'ninja': HiddenInput(),
            'session_sensei': TextInput(attrs={'class':'form-control'}),
            'session_duration': Select(attrs={'class':'form-control'},choices=DURATION_CHOICES),
            'session_assignment': TextInput(attrs={'class':'form-control'}),
            'session_notes': Textarea(attrs={'class': 'form-control', 'rows':3, 'placeholder':_('add notes here')}),
            'session_dojo': Select(attrs={'class': 'form-control'})
        }
    def clean_date(self, *args, **kwargs):
        print(self.session_date)
        session_date = self.cleaned_data.get("session_date")

class NinjaForm(ModelForm):
    dojo = ModelChoiceField(queryset=Dojo.objects.all(), widget=Select)
    # current_belt =  ChoiceField(widget=RadioSelect(attrs={'class':'form-control col-5'}), choices=BELT_CHOICES)
    ninja_package = ChoiceField(widget=Select, choices=PACKAGE_CHOICES)
    # date_registered = DateField(widget=DateInput(attrs={'class':'form-control col-2'}))
    class Meta:
        model = Ninja
        fields = ['date_registered','ninja_name', 'ninja_age', 'scratch_username', 'scratch_password','current_belt','dojo', 'ninja_package', 'parent_name', 'parent_email', 'ninja_allergies', 'ninja_disposition','ninja_likes', 'ninja_dislikes']
        # fields = '__all__'
        widgets = { 
            'date_registered' : DateInput(attrs={'class':'form-control'}),
            'ninja_name': TextInput(attrs={'class':'form-control'}),
            'ninja_age':TextInput(attrs={'class':'form-control'}),
            'current_belt': Select(attrs={'class':'form-control'}),
            'dojo': Select(attrs={'class': 'form-control'}),
            'parent_name': TextInput(attrs={'class': 'form-control'}),
            'parent_email': TextInput(attrs={'class': 'form-control', 'type': 'email'}),
            'ninja_allergies': TextInput(attrs={'class': 'form-control'}),
            'ninja_disposition': TextInput(attrs={'class': 'form-control'}),
            'ninja_likes': TextInput(attrs={'class': 'form-control', 'placeholder':_('i.e - video games, movies, etc')}),
            'ninja_dislikes': TextInput(attrs={'class': 'form-control', 'placeholder':_('i.e - loud noises, bright lights, etc')}),
        }

class EmployeeCreationForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = ['username','password1','password2']