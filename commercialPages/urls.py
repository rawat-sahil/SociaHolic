from django.urls import include,path
from .views import create_view, list_view, viewPage,someRandomFunction
urlpatterns=[
    path('create/', create_view, name='createPage'),
    path('list/', list_view, name='list'),
    path('view/<page>/',viewPage),
    path('view/',someRandomFunction,name='view')
]