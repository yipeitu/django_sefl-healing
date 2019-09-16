from django.urls import path

from . import views

# app_name="first"
urlpatterns = [
    path('', views.index, name='url_index'),
    path('<int:year>', views.first, name='url_first')
]