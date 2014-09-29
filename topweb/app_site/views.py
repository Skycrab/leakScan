#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import json
import copy
from datetime import datetime
import urlparse

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.utils.html import escape

from app_site.models import Task, Url, Result, Rule
from app_site.util import json_success, json_error, get_domain, send_request, enum

TASK = enum('WAIT', 'RUNNING', 'STOP', 'FINISH')
SPIDER = enum('WAIT', 'RUNNING', 'STOP', 'FINISH')
RISK =  enum('LOW', 'MIDDLE', 'HIGH', start=1)

def task_percent(tasks):
    for task in tasks:
        h_c = Result.objects.filter(task_id=task.id,risk=RISK.HIGH).count()
        m_c = Result.objects.filter(task_id=task.id,risk=RISK.MIDDLE).count()
        l_c = Result.objects.filter(task_id=task.id,risk=RISK.LOW).count()
        c = h_c + m_c + l_c
        if c == 0:
            s_c = 0
            s_p = 100 #无漏洞概率
            c = 1
        else:
            s_c = 0
            s_p = 0
                
        h_p = int(float(h_c)/c*100)
        m_p = int(float(m_c)/c*100)
        l_p = (100 - h_p - m_p) if l_c > 0 else 0
        sum_p = h_p + m_p + l_p
        if  sum_p != 100 and sum_p != 0: ##弥补可能和不是100%误差
            diff = 100 - sum_p
            if h_p != 0:
                h_p += diff
            elif m_p != 0:
                m_p += diff
            else:
                l_p += diff
                
        for attr in ('h_c','m_c','l_c','s_c','h_p','m_p','l_p','s_p'):
            setattr(task, attr, vars().get(attr,0))
    return tasks


def index(request):
    if request.user.is_authenticated():
        tasks = Task.objects.order_by('-id')
        tasks = task_percent(tasks)
        return render_to_response('home/home.html',{'tasks':tasks},RequestContext(request))
    else:
       return HttpResponseRedirect("/login/")

@login_required(login_url="/login/")
def task(request):
    action = request.POST.get('action','error')
    func = 'do_' + action
    f = getattr(DoTask,func,DoTask.do_error)
    return f(request)
    

class DoTask(object):
    MODULE_NAME = "SCAN_MODULE"

    @classmethod
    def do_create(cls,request):
        task_name = request.POST.get("task_name")
        task_starturl = request.POST.get("task_starturl")
        task_base = request.POST.get("task_base")
        task_urlcount = request.POST.get("task_urlcount")
        task_status = TASK.WAIT
        task = Task(name=task_name, status=task_status, start_url=task_starturl, base=task_base,
                url_count=task_urlcount, spider_flag=SPIDER.WAIT)
        task.save()
        task.s_c = 0
        task.s_p = 100
        #initnum = Task.objects.count() - 1
        #return render_to_response("home/task_template.html",{'tasks':[task],'initnum':initnum},RequestContext(request))
        return render_to_response("home/task_template.html",{'tasks':[task]},RequestContext(request))

    @classmethod
    def do_refresh(cls, request):
        tasks = Task.objects.order_by('-id')
        tasks = task_percent(tasks)
        return render_to_response("home/task_template.html",{'tasks':tasks},RequestContext(request))

    @classmethod
    def do_get(cls,request):
        task_id = request.POST.get("task_id")
        task = Task.objects.get(id=task_id)
        _ = copy.deepcopy(task.__dict__)
        _.pop('_state')
        _.pop('start_time')
        _.pop('end_time')
        return HttpResponse(json_success(_))
        #return HttpResponse(json.dumps(_))

    @classmethod
    def do_edit(cls,request):
        task_id = request.POST.get("task_id")
        task_name = request.POST.get("task_name")
        task_starturl = request.POST.get("task_starturl")
        task_base = request.POST.get("task_base")
        task_urlcount = request.POST.get("task_urlcount")
        Task.objects.filter(id=task_id).update(name=task_name, start_url=task_starturl,
                                base=task_base, url_count=task_urlcount)
        return HttpResponse(json_success(''))

    @classmethod
    def do_delete(cls, request, delete_task=True):
        task_ids = request.POST.get("task_id").split(',')
        if Task.objects.filter(id__in=task_ids).filter(status=TASK.RUNNING).count()>0:
            msg = json_error('任务正在运行，请重新选择！')
        else:
            if delete_task:
                Task.objects.filter(id__in=task_ids).delete()
            Result.objects.filter(task_id__in=task_ids).delete()
            Url.objects.filter(task_id__in=task_ids).delete()
            msg = json_success('success')
        return HttpResponse(msg)

    @classmethod
    def do_start(cls, request):
        task_id = request.POST.get("task_id")
        try:
            int(task_id)
        except ValueError:
            return HttpResponse(json_error('任务id格式有误'))
        try:
            task = Task.objects.get(id=task_id)
            if task.status == TASK.RUNNING:
                return HttpResponse(json_error('该任务正在运行，请先停止'))
        except Exception:
            return HttpResponse(json_error('该任务已不存在，请刷新重试'))
        else:
            cmd = {'action':'start','task_ids':task_id}
            res = send_request(cls.MODULE_NAME, cmd)
            if res['success']:
                task.status = TASK.RUNNING
                task.progress = ''
                task.spider_flag = TASK.WAIT
                task.start_time = datetime.now()
                task.end_time = None
                task.save()
                msg = json_success('start')
            else:
                msg = json_error('命令执行失败')

            return HttpResponse(msg)

    @classmethod
    def do_continue_start(cls, request):
        task_id = request.POST.get("task_id")
        try:
            int(task_id)
        except ValueError:
            return HttpResponse(json_error('任务id格式有误'))
        try:
            task = Task.objects.get(id=task_id)
            if task.status == TASK.RUNNING:
                return HttpResponse(json_error('该任务正在运行'))
        except Exception:
            return HttpResponse(json_error('该任务已不存在，请刷新重试'))
        else:
            cmd = {'action':'continue_start','task_ids':task_id}
            res = send_request(cls.MODULE_NAME, cmd)
            if res['success']:
                task.status = TASK.RUNNING
                task.save()
                msg = json_success('start')
            else:
                msg = json_error('命令执行失败')

            return HttpResponse(msg)
        

    @classmethod
    def do_restart(cls, request):
        http_response = cls.do_delete(request, delete_task=False)
        msg = json.loads(http_response.content)
        if not msg['success']:
            return http_response
        return cls.do_start(request)


    @classmethod
    def do_stop(cls, request):
        task_id = request.POST.get("task_id")
        try:
            int(task_id)
        except ValueError:
            return HttpResponse(json_error('任务id格式有误'))
        try:
            task = Task.objects.get(id=task_id)
            if task.status != TASK.RUNNING:
                return HttpResponse(json_error('该任务已经停止'))
        except Exception:
            return HttpResponse(json_error('该任务已不存在，请刷新重试'))
        else:
            cmd = {'action':'stop','task_ids':task_id}
            res = send_request(cls.MODULE_NAME, cmd)
            if res['success']:
                task.status = TASK.STOP
                task.save()
                msg = json_success('stop')
            else:
                msg = json_error('命令执行失败')

            return HttpResponse(msg)

    @classmethod
    def do_error(cls,request):
        return HttpResponse(json_error('非法操作'))



@login_required(login_url="/login/")
def policy(request):
    return HttpResponse("正在开发，敬请期待")



@login_required(login_url="/login/")
def detail(request):
    action = request.GET.get('action') or request.POST.get('action') or 'error'
    func = 'do_' + action
    f = getattr(DoDetail,func,DoDetail.do_error)
    return f(request)


class DoDetail(object):
    @classmethod
    def do_home(cls, request):
        return render_to_response("home/detail.html",{},RequestContext(request))

    @staticmethod
    def get_node(task_id, node):
        childrens = []
        temp = []
        for u in Url.objects.filter(task_id=task_id):
            _ = urlparse.urlsplit(u.url)
            if not _.path.startswith(node) or node == _.path:
                continue
            path = _.path.split(node,1)[-1]
            left = path.split('/',1)
            icon, children = ('folder',True) if len(left)>1 else ('file file-%s' % path[path.find('.')+1:], False)
            text = left[0]
            cid = "%s%s/" %(node, text) if children else "%s%s" %(node, text)
            if text not in temp:
                temp.append(text)
                childrens.append({'text':text, 'children': children, 'id': cid, 'icon':icon})
        return childrens



    @classmethod
    def do_node(cls, request):
        task_id = request.GET.get('task_id')
        node = request.GET.get('id','#')
        if node == '#': #root
            records = []
            node = '/'
            # task = Task.objects.get(id=task_id)
            # _ = urlparse.urlsplit(task.start_url)
            # domain = "%s://%s%s" % ( _.scheme, _.netloc, task.base)
            domain = get_domain(task_id)
            root = {'text':domain, 'id':'/', 'icon':'folder','state':{'opened':True,'disabled':False}}
            root['children'] = cls.get_node(task_id, node)
            records.append(root)
        else:
            records = cls.get_node(task_id, node)

            
        response = HttpResponse(json.dumps(records))
        response['Content-Type'] ='application/json; charset=utf8'
        return response

    @classmethod
    def do_detail(cls, request):
        task_id = request.GET.get('task_id')
        rule_id = request.GET.get('id','#')
        records = []
        template = '\t<span class="badge">%s</span>'
        if rule_id == '#':
            domain = get_domain(task_id)
            domain = "%s%s" %(domain,template % Result.objects.filter(task_id=task_id).count())
            root = {'text':domain, 'id':'/', 'icon':'domain','state':{'opened':True,'disabled':False}}         
            rule_ids = Result.objects.filter(task_id=task_id).order_by('-risk').values('rule_id').distinct()
            childrens = []
            for rd in rule_ids:
                r = Rule.objects.get(rule_id=rd['rule_id'])
                name = "%s%s" % (r.rule_name, template % Result.objects.filter(task_id=task_id, rule_id=rd['rule_id']).count())
                childrens.append({'text':name, 'id':rd['rule_id'], 'icon':r.risk,'children':True})
            root['children'] = childrens
            records.append(root)
        else:
            results = Result.objects.filter(task_id=task_id,rule_id=rule_id)
            for r in results:
                rid = "%s^%s" %(r.id, rule_id)
                url = r.url
                index = url.find('?')
                if index != -1:
                    url = url[:index]
                records.append({'text':url, 'id':rid, 'icon':'url','children':False})
            
        response = HttpResponse(json.dumps(records))
        response['Content-Type'] ='application/json; charset=utf8'
        return response

    @classmethod
    def do_vul(cls, request):
        task_id = request.GET.get('task_id')
        result_id = request.GET.get('id')
        result = Result.objects.get(task_id=task_id, id=result_id)
        record = {'url':result.url, 'detail':result.detail, 'request':result.request, 'response':result.response}
        rule = Rule.objects.get(rule_id=result.rule_id)
        for k, v in record.iteritems():
            record[k] = escape(v).replace('\r\n','<br />')
        return HttpResponse(json_success(record))

    @classmethod
    def do_desc(cls, request):
        rule_id = request.GET.get('id')
        rule = Rule.objects.get(rule_id=rule_id)
        record= {'name':rule.rule_name, 'description':rule.description, 'solution':rule.solution }
        for k, v in record.iteritems():
            record[k] = escape(v).replace('\r\n','<br />')
        return HttpResponse(json_success(record))


    @classmethod
    def do_basic(cls, request):
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        pro = task.progress.split('|')
        if pro[-1] == '':
            progress = '0%'
            if task.reachable:
                rule_name = '扫描引擎初始化'
            else:
                rule_name = '请确认目标网站是否可以访问'
        elif pro[-1] != 'END':
            rules_count = Rule.objects.count()
            progress = "%d%%" % (float(len(pro))/(rules_count+2)*100)
            rule = Rule.objects.get(rule_id=pro[-1])
            rule_name = rule.rule_name
        else:
            progress = '100%'
            rule_name = ''
        result = {'progress':progress, 'rule_name':rule_name, 'spider_flag':task.spider_flag,
                'task_status':task.status
            }
        return HttpResponse(json_success(result))



    @classmethod
    def do_error(cls,request):
        return HttpResponse(json_error('非法操作'))