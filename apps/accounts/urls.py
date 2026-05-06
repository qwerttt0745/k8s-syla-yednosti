from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("volunteers/", views.volunteer_list, name="volunteer_list"),
    path("volunteers/add/", views.volunteer_create, name="volunteer_create"),
    path("volunteers/<int:pk>/toggle/", views.volunteer_toggle, name="volunteer_toggle"),
]
