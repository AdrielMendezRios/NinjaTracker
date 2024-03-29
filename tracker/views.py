from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect, request
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.db.models import Q
from django import forms 
from django.core.paginator import Paginator
from django.contrib.auth import  authenticate, login, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
import time

from .models import Dojo, Ninja, Session, Employee
from .forms import SessionForm, NinjaForm, EmployeeCreationForm, BankWithdrawalForm, BankDepositForm
from .decorators import *
import logging
import csv

logger = logging.getLogger(__name__)

utc = pytz.UTC
et = pytz.timezone('US/Eastern')



class IndexView(generic.ListView):
    template_name = "tracker/index.html"
    context_object_name = "dojo_list"
    

    
    @method_decorator(login_required(login_url='tracker:login'))
    # @method_decorator(allowed_users(allowed_roles=['admin','lead','sensei']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Dojo.objects.all()
    
    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['ninja_list'] = Ninja.objects.all()
        user = get_user(self.request)
        context['user'] = user
        # ninjaUpload() # this uploads ninjas into database from scrubbed csv file DO NOT uncomment
        if user.is_director:
            context['sessions'] = Session.objects.filter(session_dojo=user.home_dojo)

        
        return context


@login_required(login_url='tracker:login')
def search(request):
    search_query = request.GET.get('search', '')

    context = {}
    result = ""
    print(search_query)
    if search_query:
        result = Ninja.objects.filter(Q(ninja_name__icontains=search_query))
    else:
        result = Ninja.objects.all()
    print(result)
    context['ninja_list'] = result
    context['user'] = get_user(request)
    pagination(result, request, context, 10)
    return  render(request, "tracker/ninjas.html", context)

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead'])
def registerPage(request):
    try:
        form = EmployeeCreationForm(initial={'username':'username'})
 
        if request.method == 'POST':
            form = EmployeeCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('tracker:login')
        context = {'form':form,  'user' : get_user(request)}
        return render(request, 'tracker/Register.html', context)
    except Exception as e:
        logger.info(e)
        logger.error(e)
        logger.debug(e)
        


@unauthenticated_user
def loginPage(request):
    context = {}

    users = Employee.objects.all()
    print(users)
    if request.method == "POST":
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('tracker:index')

    return render(request, 'tracker/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('tracker:login')

"""               DOJO                     """

class DojoListView(generic.ListView):
    model = Dojo
    context_object_name = "dojo_list"
    template_name = "tracker/dojos.html"

    @method_decorator(login_required(login_url='tracker:login'))
    @method_decorator(allowed_users(allowed_roles=['admin','lead','sensei']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DojoListView, self).get_context_data(*args, **kwargs)
        ninjas_in_dojos = {}
        for dojo in context['dojo_list']:
            ninjas = Ninja.objects.filter(dojo=dojo.id)
            ninjas_in_dojos[dojo] = len(ninjas)
        context['ninjas_in_dojo'] = ninjas_in_dojos
        context['user'] = get_user(self.request)

        return context

class DojoDetailView(generic.DetailView):
    model = Dojo
    template_name = "tracker/dojo.html"

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    @method_decorator(login_required(login_url='tracker:login'))
    @method_decorator(allowed_users(allowed_roles=['admin','lead','sensei']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    """ TODO: change the look up of all sessions using session_dojo instead of ninjas in dojo"""
    def get_context_data(self, *args, **kwargs):
        context = super(DojoDetailView, self).get_context_data(*args, **kwargs)
        ninjas = Ninja.objects.filter(dojo=self.object.id).order_by('-id')
        context['form'] = SessionForm()
        collect_todays_sessions(ninjas, context) # adds relavent sessions into context['in_dojo']
        collect_unapproved_sessions(self.object.id, context) # adds unapproved session into context['unapproved_sessions']
        context['ninjas'] = ninjas
        pagination(ninjas, self.request, context, pg_amount=10)
        context['user'] = get_user(self.request)

        return context

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead'])  
def approve_all_dojo_sessions(request, pk):
    unpproved_sessions_queryset = Session.objects.filter(session_dojo=pk, session_is_approved=False)
    for session in unpproved_sessions_queryset:
        session.session_is_approved = True
        session.save()
    return redirect(reverse('tracker:dojo', args=[pk]))

    
"""               end of DOJO                     """

"""               NINJA                     """


class NinjaListView(generic.ListView):
    model = Ninja
    template_name = "tracker/ninjas.html"

    @method_decorator(login_required(login_url='tracker:login'))
    @method_decorator(allowed_users(allowed_roles=['admin','lead','sensei']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(NinjaListView, self).get_context_data(*args, **kwargs)
        ninjas = Ninja.objects.all().order_by('-id')
        context['ninjas'] = ninjas
        pagination(ninjas, self.request, context, pg_amount=10)
        context['user'] = get_user(self.request)

        return context

class NinjaDetailView(generic.DetailView):
    model = Ninja
    template_name = "tracker/ninja.html"

    current_month = datetime.now().month
    current_year = datetime.now().year

    @method_decorator(login_required(login_url='tracker:login'))
    @method_decorator(allowed_users(allowed_roles=['admin','lead','sensei']))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(NinjaDetailView, self).get_context_data(*args, **kwargs)
        sessions =  Session.objects.filter(ninja=self.object.id).order_by('-id')
        latest_session = Session.objects.filter(ninja=self.object.id).latest() if len(sessions) > 0 else False
        if sessions.count() > 0:
            latestSession = Session.objects.filter(ninja=self.object.id).latest()
            context['workingOn'] = latestSession.session_assignment
            sessionsThisMonth = list(Session.objects.filter(ninja=self.object.id, session_date__month__gte=self.current_month-1, session_date__year=self.current_year))
            # print(sessionsThisMonth)
            context['hrsThisMonth'] = calc_hours_in_month(self.object.date_registered, sessionsThisMonth)
        else:
            context['hrsThisMonth'] = 0
            context['workingOn'] = "Get them started on their first project!"
        context['firstName'] = self.object.ninja_name.split(' ')[0]
        context['number_of_sessions'] = len(sessions)
        context['latest_session'] = latest_session
        context['user'] = get_user(self.request)

        pagination(sessions, self.request, context, pg_amount=5)
        
        return context

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead'])
def ninjaInfo(request, pk):
    context = {}
    ninja = Ninja.objects.get(id=pk)
    # dojo = Dojo.objects.get(id=ninja.dojo.id)
    sessions = Session.objects.filter(ninja=pk).order_by('-id')
    periods = sessions_grouped_by_period(sessions, ninja.date_registered)
    # print(dojo)
    context['ninja'] = ninja
    # context['dojo'] = dojo
    context['periods'] = periods
    context['user'] = get_user(request)
    context['ninja_data'] = get_fields(ninja)
    pagination(periods, request, context, 5)
    return render(request, 'tracker/ninja_info.html', context)


@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead'])
def ninja_create(request, pk):
    dojo = Dojo.objects.get(id=pk)
    form = NinjaForm(initial={'dojo':dojo})
    context = {'form': form, 'dojo': dojo, 'user': get_user(request)}
    if request.method == 'POST':
        form = NinjaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('tracker:dojo', args=[dojo.id]))
    
    return render(request, 'tracker/ninja_create.html', context)

def ninjaUpload():
    """
        only call this function if you have a lot of kids to add to the system 
        and have a csv file with the right information.
    """
    # result = Ninja.objects.filter(Q(ninja_name__icontains=search_query))
    dojo = Dojo.objects.filter(id=1)
    ninjas = []
    with open('ninjas.csv','r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        ninja = {}
        cont = 0
        for row in csv_reader:
            if cont == 0:
                cont += 1
            elif row[2] != '':
                ninja['ninja_name'] = row[0]
                unformatDate = row[1].split('-')
                date = '-'.join([unformatDate[2],unformatDate[0], unformatDate[1]])
                ninja['date_registered'] = date

                pack = float(row[2][1:])
                if pack < 150:
                    ninja['ninja_package'] = 'Create Lite'
                else:
                    ninja['ninja_package'] = 'Create Standard'
                ninja['parent_email'] = row[3]
                ninjas.append(ninja)
                print(ninja)
                ninja = {}
    for ninja in ninjas:
        if len(Ninja.objects.filter(ninja_name__icontains=ninja['ninja_name'])) > 0:    
             ninja = Ninja(dojo=dojo[0], ninja_name=ninja['ninja_name'], date_registered=ninja['date_registered'], ninja_package=ninja['ninja_package'],parent_email=ninja['parent_email'] )
             ninja.save()

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead', 'sensei'])
def ninja_update(request, pk):
    ninja = Ninja.objects.get(id=pk)
    form = NinjaForm( initial={'dojo': ninja.dojo, 'current_belt': ninja.current_belt, 'ninja_package':ninja.ninja_package, 'date_registered':ninja.date_registered}, instance=ninja)
    # form.fields['date_registered'].widget = forms.HiddenInput()
    if request.method == 'POST':
        # print("printing request:", request.POST)
        form = NinjaForm(request.POST, instance=ninja)
        if form.is_valid():
            form.save()
            return redirect(reverse('tracker:ninja', args=[ninja.id]))
    
    context = {'form': form, 'ninja': ninja, 'user': get_user(request)}
    return render(request, 'tracker/ninja_update.html', context)

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead', 'sensei'])
def ninja_bank(request, pk):
    context = {}
    ninja = Ninja.objects.get(id=pk)
    user = get_user(request)
    withdrawalForm = BankWithdrawalForm()
    depositForm = BankDepositForm()
    if request.method == 'POST':
        form = BankWithdrawalForm(request.POST)
        widthdrawl_amount = abs(int(form['withdrawal_amount'].value()))
        if widthdrawl_amount <= ninja.ninja_bank:
            ninja.ninja_bank -= widthdrawl_amount
            ninja.save()
            return redirect(reverse( 'tracker:ninja-bank', args=[ninja.id]))
    if request.method == 'GET':
        form = BankDepositForm(request.GET)
        if form['deposit_amount'].value():
            deposit_amount = int(form['deposit_amount'].value())
            if deposit_amount > 0:
                ninja.ninja_bank += deposit_amount
                ninja.save()
                return redirect(reverse('tracker:ninja-bank', args=[ninja.id]))

    context = {'ninja': ninja, 'user' : user, 'withdrawalForm' : withdrawalForm, 'depositeForm': depositForm }
    return render(request, 'tracker/bank.html', context)

"""               end of NINJA                     """



"""               SESSION                     """
@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead', 'sensei'])
def session_create(request, pk):
    ninja = Ninja.objects.get(id=pk)
    user = get_user(request)
    form = SessionForm(initial={'ninja':ninja, 'session_notes':'add notes here', 'session_sensei': user.first_name, 'session_dojo': user.home_dojo})

    context = {'form': form, 'ninja': ninja,  'user': user}
    
    if request.method == 'POST':
        # print("printing request:", request.POST)
        form = SessionForm(request.POST)
        if form.is_valid():
            # print('its valid!')
            form.save()
            this_session = Session.objects.filter(ninja=ninja.id).order_by("-id")[0]
            return redirect(reverse('tracker:dojo', args=[this_session.session_dojo.id]))

    return render(request, 'tracker/session_create.html', context)



@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead','sensei'])
def session_update(request, pk):
    session = Session.objects.get(id=pk)
    form = SessionForm(instance=session)

    user = get_user(request)
    if request.method == 'POST':
        # print("printing request:", request.POST)
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            print(request.POST)
            if 'approve session' in request.POST:
                session.session_is_approved = True
                session.save()
            form.save()
            ninja = Ninja.objects.get(ninja_name=session.ninja.ninja_name)
            return redirect(reverse('tracker:dojo', args=[session.session_dojo.id]))
    
    context = {'form': form, 'session':session,  'user': user}
    return render(request, 'tracker/session_update.html', context)

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead','sensei'])
def session_delete(request, pk):
    if Session.objects.filter(id=pk):
        context ={}
        session = Session.objects.get(id=pk)
        ninja = session.ninja

        if request.method == 'POST':
            # print('in here!!')
            session.delete()
            return redirect(reverse('tracker:ninja', args=[ninja.id]))

        context = {'session': session, 'user': get_user(request)}
        return render(request,'tracker/session_delete.html', context)
    return redirect("../../")

@login_required(login_url='tracker:login')
@allowed_users(allowed_roles=['admin','lead'])
def session_approve(request, pk):
    session = Session.objects.get(id=pk)
    user = get_user(request)
    if user.is_director or user.is_lead:
        session.session_is_approved = True
        session.save()
    dojo = session.session_dojo
    return redirect(reverse('tracker:dojo', args=[dojo.id]))

""" End Of SESSION"""





""" Helper Functions"""


def calc_hours_in_month(reg_date,sessions_this_month):
    hrs_this_month = 0
    print(sessions_this_month)
    if reg_date.day > date.today().day:
        reg_date_in_month = date(datetime.today().year,datetime.today().month,reg_date.day) - relativedelta(month=1)
        first_of_month = reg_date_in_month #date(datetime.today().year,datetime.today().month-1,reg_date.day)
    else:
        first_of_month = date(datetime.today().year,datetime.today().month,reg_date.day)
    last_of_month = first_of_month + relativedelta(months=+1)
    # print("first of the month",first_of_month)
    # print("last of the month",last_of_month)
    for session in sessions_this_month:
        # print(session.session_date.date())
        if first_of_month <= session.session_date.date() <= last_of_month:
            if session.session_duration >= 2:
                hrs_this_month += 2
            else:
                hrs_this_month += 1
    # print(hrs_this_month)
    return hrs_this_month


def all_pay_days(sessions, reg_date):
    pay_days = [reg_date.date()]
    cont = True
    last_payed = reg_date
    while cont:
        next_payDay = last_payed + relativedelta(months=+1)
        if next_payDay.date() > date.today():
            pay_days.append(next_payDay.date())
            cont = False
        else:
            pay_days.append(next_payDay.date())
        last_payed = next_payDay
    return pay_days


def sessions_grouped_by_period(sessions, reg_date):
    periods = []
    pay_days = all_pay_days(sessions, reg_date)
    for i in range(len(pay_days)):
        if len(pay_days) > i+1:
            periods.append(sessions.filter(session_date__gte=pay_days[i], session_date__lt=pay_days[i+1]))
    data = group_session_dict(periods, reg_date)
    return data

def group_session_dict(grouped_sessions, reg_date):
    grouped_sessions_and_hours_in_month = []
    hrs = 0
    for group in grouped_sessions:
        if len(group) > 0:
            print(group)
            for session in group: 
                hrs += session.session_duration
            sessions_and_hrs = {'hours':hrs, 'sessions':group}
            grouped_sessions_and_hours_in_month.append(sessions_and_hrs)
            hrs=0
    grouped_sessions_and_hours_in_month.reverse()
            
        
    return grouped_sessions_and_hours_in_month


def pagination(obj, req, context, pg_amount):
    paginator = Paginator(obj, pg_amount)
    page_number = req.GET.get('page', 1)
    page = paginator.get_page(page_number)

    if page.has_next():
        next_url = f'?page={page.next_page_number()}'
    else:
        next_url = ''
    
    if page.has_previous():
        previous_url = f'?page={page.previous_page_number()}'
    else:
        previous_url = ''

    context['next_page_url'] = next_url
    context['previous_page_url'] = previous_url
    context['page'] = page


def session_countdown(obj):
    session_start = obj.session_date
    session_end = session_start + timedelta(hours=obj.session_duration)
    # print(obj.ninja.ninja_name)
    # print(datetime.now())
    # print(session_end)
    # print()
    now = datetime.now().astimezone(et)
    # end = session_end
    return now < session_end



def get_user(request):
    if request.user:
        user = Employee.objects.get(pk=request.user.id)
        # print(user.is_director)
        return user
    return None


def get_fields(obj):
    if obj:
        fields = [[field.name.replace("_", " "), field.value_to_string(obj)] for field in obj._meta.fields]
        # print("*!*!*!*!*!*!*!",fields)
        fields[6][1] = fields[6][1].split("T")[0]
        fields[1][1] = Dojo.objects.get(id=int(fields[1][1]))
        fields.pop(0)
        for field in fields[8:11]:
            if "ninja" in field[0]:
                field[0] = field[0].split(" ")[1]

       
        return fields

def collect_todays_sessions(ninjas, context):
    in_dojo = []
    for ninja in ninjas:
        if Session.objects.filter(ninja=ninja.id):
            todays_session = Session.objects.filter(ninja=ninja.id).latest('session_date')
            todays_session.session_date = todays_session.session_date.astimezone(et)
            if todays_session.session_date.date() == datetime.now().date():
                if session_countdown(todays_session):
                    in_dojo.append(todays_session)
    context['in_dojo'] = in_dojo

def collect_unapproved_sessions(dojo, context):
    context['unapproved_sessions'] = Session.objects.filter(session_dojo=dojo, session_is_approved=False)

""" Helper Functions end """