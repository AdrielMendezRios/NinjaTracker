from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Dojo, Ninja, Session, Employee
from .forms import EmployeeCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class EmployeeAdmin(UserAdmin):
    model = Employee
    # add_form = EmployeeCreationForm
    fieldsets = ()
    readonly_fields = ('date_joined','last_login')

class NinjaAdmin(admin.ModelAdmin):
    model = Ninja
    list_display = ('ninja_name', 'dojo', 'date_registered')

class SessionAdmin(admin.ModelAdmin):
    model = Session
    list_display = ('ninja', 'session_dojo', 'session_date', 'session_sensei', 'session_is_approved' )

admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Dojo)
admin.site.register(Ninja, NinjaAdmin)
admin.site.register(Session, SessionAdmin)