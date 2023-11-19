from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/',
         views.АboutPage.as_view(),
         name='about'),
    path('rules/',
         views.RulesPage.as_view(),
         name='rules'),
]
