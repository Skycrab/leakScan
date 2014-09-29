from django.db import models
from django.contrib import admin

# Create your models here.

class Task(models.Model):
    """
    status: 0 create(wait) 1 running 2 stop 3 finish
    spider_flag: 0 create(wait) 1 running 2 stop 3 finish
    """
    class Meta:
        db_table = 'task'

    name = models.CharField(max_length=200)
    status = models.IntegerField()
    start_url = models.URLField()
    base = models.CharField(max_length=40)
    url_count = models.IntegerField()
    progress = models.TextField()
    spider_flag = models.IntegerField(1)
    robots_parsed = models.BooleanField(default=False)
    sitemap_parsed = models.BooleanField(default=False)
    reachable = models.BooleanField(default=True)
    start_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(blank=True, null=True)
   

class Url(models.Model):

    class Meta:
        db_table = 'url'

    task_id = models.IntegerField()
    url = models.URLField()
    method = models.CharField(max_length=10)
    params = models.CharField(max_length=200,blank=True)
    referer = models.CharField(max_length=200,blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

class Result(models.Model):

    class Meta:
        db_table = 'result'

    task_id = models.IntegerField()
    rule_id = models.IntegerField()
    risk = models.IntegerField(1) # 1 low 2 middle 3 high
    url = models.URLField()
    detail = models.TextField(blank=True)
    request = models.TextField(blank=True)
    response = models.TextField(blank=True)


class Rule(models.Model):

    class Meta:
        db_table = 'rule'

    rule_id = models.IntegerField()
    rule_name = models.CharField(max_length=128)
    run_type = models.IntegerField(1)
    risk = models.CharField(max_length=4)
    priority = models.IntegerField(1)
    file_name = models.CharField(max_length=128)
    category_id = models.IntegerField()
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)




admin.site.register(Task)