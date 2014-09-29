# coding=utf-8
from django.contrib.sites.models import Site

def site(request):
    return {
        'site' : Site.objects.get_current(),
    }