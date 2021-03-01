from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'tracker'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('q/', views.search, name='search'),
    path('register/', views.registerPage, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),

    path('<int:pk>/dojo/', views.DojoDetailView.as_view(), name='dojo'),
    path('dojos/', views.DojoListView.as_view(), name='dojos'),
    path('dojo/',views.DojoDetailView.as_view(), name='dojo-u'),

    path('<int:pk>/ninja/', views.NinjaDetailView.as_view(), name='ninja'),
    path('<int:pk>/ninja/info/', views.ninjaInfo, name='ninja-info'),
    path('ninja/<int:pk>/create/', views.ninja_create, name='ninja-create'),
    path('ninja/<int:pk>/update/', views.ninja_update, name='ninja-update'),
    path('ninja/<int:pk>/bank/', views.ninja_bank, name='ninja-bank'),

    path('ninjas/', views.NinjaListView.as_view(), name='ninjas'),

    path('session_create/<int:pk>/', views.session_create, name="session_create"),
    path('session_update/<int:pk>/', views.session_update, name="session_update"),
    path('session_delete/<int:pk>/', views.session_delete, name="session_delete"),
    path('session_approve/<int:pk>/', views.session_approve, name="session_approve"),
    path('approve_all_sessions/<int:pk>/', views.approve_all_dojo_sessions, name="approve_all_dojo_sessions"),


    # path('ninja/<dojo_name>/add/', views.NinjaCreateView.as_view(), name='ninja-add'),
    # path('session/add/<int:pk>/', views.SessionCreateView.as_view(), name='session-add'),
    # path('session/<int:pk>/', views.SessionUpdateView.as_view(), name='session-update'),
    # path('session/<int:pk/delete/', views.SessionDeleteView.as_view(), name='session-delete') 
]
