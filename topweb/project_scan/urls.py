from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView
from app_site import views

admin.autodiscover()

#url(r'^$', TemplateView.as_view(template_name="base.html"), name='index'),

urlpatterns = patterns('',
    url(r'^$', views.index,name='index'),
    url(r'', include('django.contrib.auth.urls')),
    url(r'task$', views.task),
    url(r'detail$', views.detail),
    url(r'policy$', views.policy,name='policy'),
    url(r'^admin/', include(admin.site.urls)),
) #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
