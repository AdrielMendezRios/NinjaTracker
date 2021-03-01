from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import CASCADE, PROTECT
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User, UserManager






class Dojo(models.Model):
    dojo_name = models.CharField(max_length=50)
    dojo_address = models.CharField(max_length=150, default="N/A")
    

    def __str__(self):
        return self.dojo_name
    
class Ninja(models.Model):
    dojo = models.ForeignKey(Dojo, on_delete=CASCADE, default=0)
    ninja_name = models.CharField(max_length=50)
    ninja_age = models.IntegerField(default=0)
    scratch_username = models.CharField("Scratch username", max_length=50, default="Request info")
    scratch_password = models.CharField("Scratch password", max_length=50, default="Request info")
    ninja_bank = models.IntegerField(default=5)
    # ninja_is_active = models.BooleanField(default=True)


    date_registered = models.DateTimeField("Date Registered", auto_now=False)

    parent_name = models.CharField(max_length=50, default="Request info")
    parent_email = models.EmailField(default="Request@Info.com")


    ninja_allergies = models.CharField(_("Ninja Allergies, if none enter NONE"), max_length=50, default="Request info")
    ninja_disposition = models.CharField(max_length=100, default="Request info")
    ninja_likes = models.CharField(max_length=100, default="Request info")
    ninja_dislikes = models.CharField(max_length=100, default="Request info")
    

    class NinjaBelt(models.TextChoices):
        WHITE = 'White', _('White Belt')
        YELLOW = 'Yellow', _('Yellow Belt')
        ORANGE = 'Orange', _('Orange Belt')
        GREEN = 'Green', _('Green Belt')
        BLUE = 'Blue', _('Blue Belt')
        PURPLE = 'Purple', _('Purple Belt')
        BROWN = 'Brown', _('Brown Belt')
        RED = 'Red', _('Red Belt')
        BLACK = 'Black', _('Black Belt')

    
    class HomeDojo(models.TextChoices):
        WAKEFOREST = 'Wake Forest', _('Wake Forest')
        HOLLYSPRING = 'Holly Springs', _('Holly Springs')
        RALEIGH = 'Raleigh', _('Raleigh')
    
    class NinjaPackage(models.TextChoices):
        CREATE_EIGHT = 'Create Standard', _('Create 8 hrs per month')
        CREATE_FOUR = 'Create Lite', _('Create 4 hrs per month')

    current_belt = models.CharField(
        max_length=20,
        choices=NinjaBelt.choices,
        default=NinjaBelt.WHITE
    )

    home_dojo = models.CharField(
        max_length=20,
        choices=HomeDojo.choices,
        default=HomeDojo.WAKEFOREST
    )

    ninja_package = models.CharField(
        max_length=50,
        choices=NinjaPackage.choices,
        default=NinjaPackage.CREATE_FOUR
    )

    def get_id(self):
        return str(self.id)
    
    def __str__(self):
        return self.ninja_name #f"Ninja_ID:{self.id}, Name: {self.ninja_name}, Age: {self.ninja_age}, Belt: {self.current_belt}, Home Dojo: {self.dojo} "


class Session(models.Model):
    ninja = models.ForeignKey(Ninja, on_delete=CASCADE, default=0)
    session_date = models.DateTimeField(auto_now_add=True)
    session_duration = models.IntegerField()
    session_assignment = models.CharField(max_length=100, blank=True)
    session_notes = models.CharField(max_length=500, blank=True, null=True)
    session_sensei = models.CharField(max_length=50)
    session_dojo = models.ForeignKey(Dojo, on_delete=PROTECT, default=0)
    session_is_approved = models.BooleanField(default=False, blank=True)
    

    # def get_absolute_url(self):
    #     return reverse("tracker:ninja", kwargs={"pk": self.ninja.pk})

    class Meta():
        get_latest_by = "session_date"
    

    def __str__(self):
        return self.ninja.ninja_name #f"Ninja: {self.ninja.ninja_name}, Session Location: {self.session_dojo}, Session Date: {self.session_date}, Duration: {str(self.session_duration)}, Worked on: {self.session_assignment}, Sensei Notes: {self.session_notes}, Sensei: {self.session_sensei}"

class EmployeeManager(UserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have a email")
        if not username:
            raise ValueError("User must have a username")
        


        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.is_admin = True
        user.has_perms = True
        user.is_staff = True
        user.is_superuser = True
        user.is_director = False
        user.is_lead = False
        user.is_sensei = True
        user.home_dojo = 1
        user.save(using=self._db)
        return user




class Employee(User):


    # email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    # username =  models.CharField(max_length=30, unique=True)
    # date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    # # last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    # is_admin = models.BooleanField(default=False)
    # is_active =  models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # # is_superuser = models.BooleanField(default=False)


    is_director = models.BooleanField(default=False)
    is_lead = models.BooleanField(default=False)
    is_sensei = models.BooleanField(default=True)

    home_dojo = models.ForeignKey(Dojo, on_delete=CASCADE, default=1)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = EmployeeManager()


    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

