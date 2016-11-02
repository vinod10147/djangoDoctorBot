from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
	url(r'^(?P<question_id>[0-9]+)', views.index, name='index'),
	url(r'^factorial1', views.factorial1, name='factorial1'),
	url(r'^new', views.new, name='new'),
	url(r'^home', TemplateView.as_view(template_name='Fact.html')),
]