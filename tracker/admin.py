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


admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Dojo)
admin.site.register(Ninja)
admin.site.register(Session)