
/*********analyse response***********/
function analyse(data){
    var d = jQuery.parseJSON(data);
    if(!d.success){
        bootbox.alert(d.msg);
        return false;
    }else{
        return d.msg;
    }
}

// 单个任务绑定双击 --修改记录
function task_bind_dblclick(){
    $('.task_record').bind('dblclick',function(){
        var task_id = $(this).children(".hide").html();
        $.post("/task",
            {
                'action': 'get',
                'task_id': task_id
            },
            function(data){
                var d = analyse(data);
                if(d !== false){
                    $('#task_title').html("修改扫描任务");
                    $('#hidden_id').val(task_id);
                    $('#task_name').val(d.name);
                    $('#task_starturl').val(d.start_url);
                    $('#task_base').val(d.base);
                    $('#task_urlcount').val(d.url_count);
                    $('#createScan').modal('show');
                }
            }
        );
    });
}



// 单个任务记录绑定删除
function task_bind_delete(){
     $(".delete_task").bind('click',function(){
        var node = $(".open").parent().parent();
        var task_id = node.children(".hide").html();
        $.post("/task",
                {
                    'action': 'delete',
                    'task_ids': task_id
                },
                function(data){
                    if(analyse(data) !== false){
                        node.remove();
                    }
                }
            );
    });
}

// 单个任务绑定开始按键
function task_bind_start(){
    $(".start_task").bind('click',function(){
        var node = $(".open").parent().parent();
        var task_id = node.children(".hide").html();
        $.post("/task",
                {
                    'action': 'start',
                    'task_id': task_id
                },
                function(data){
                    d = analyse(data);
                    if(d!== false){
                        
                    }
                }
            );
    });
}

// 单个任务绑定停止按键
function task_bind_stop(){
    $(".stop_task").bind('click',function(){
        var node = $(".open").parent().parent();
        var task_id = node.children(".hide").html();
        $.post("/task",
                {
                    'action': 'stop',
                    'task_id': task_id
                },
                function(data){
                    d = analyse(data);
                    if(d!== false){
                        
                    }
                }
            );
    });
}

//单个任务绑定详细按钮
function task_bind_detail(){
    $(".detail_task").bind('click',function(){
        var node = $(".open").parent().parent();
        var task_id = node.children(".hide").html();
        var task_name = node.children(".taskname").html();
        $.post("/detail",
                {
                    'action': 'home',
                    'task_ids': task_id
                },
                function(data){
                    //$("#main_body").html(data);
                    var href = "task" + task_id;
                    var html = "<li class=\"active\"><a href=\"#"+href+"\" data-toggle=\"tab\"><span class=\"glyphicon glyphicon-th\"></span>&nbsp;&nbsp;扫描详细信息-"+task_name+"</h1></a></li>";
                    $('#scan_nav').append(html);
                    var body ="<div class=\"tab-pane active\" id=\""+href+"\">"+data+"</div>";
                    $('#scan_home').append(body);
                    var id = '#scan_nav a[href="'+href+'"]';
                    $(id).tab('show');
                    $('#scan_task').tab('hide');
                    /*****************刷新按钮******************/
                    $('#refresh_tab').bind("click",function(){
                        $.jstree.reference("#dir_tree").refresh();
                        $.jstree.reference("#vul_detail_tree").refresh();
                        basic_info();
                    });
                    /*****************基本信息******************/
                    var basic_info = function(){
                        $.get('/detail?action=basic&task_id=' + task_id, function (data) {
                            var d = analyse(data);
                            if(d !== false){
                                $('#current_progress_bar').attr('style','width:'+d.progress);
                                $('#current_progress').html(d.progress);
                                if(d.rule_name){
                                    $('#current_rule').html(d.rule_name);
                                }else{
                                    $('#current_rule').html('扫描已结束！');
                                    clearInterval(timer);
                                }
                                if(d.task_status == 3){ //任务已结束，清空定时器
                                    clearInterval(timer);
                                }
                            }
                        });

                    };

                    var timer = setInterval(basic_info, 2000);

                    basic_info()


                    /*****************目录结构******************/
                    $('#dir_tree')
                        .jstree({
                            'core' : {
                                'data' : {
                                    'url' : '/detail?action=node'+'&task_id='+task_id,
                                    'data' : function (node) {
                                        return { 'id' : node.id };
                                    }
                                },
                                'themes' : {
                                    'responsive' : true,
                                    'variant' : 'small'
                                    //'stripes' : true
                                }
                            }

                        });
                    /********************漏洞详情**********************/
                    $('#vul_detail_tree')
                        .jstree({
                            'core' : {
                                'data' : {
                                    'url' : '/detail?action=detail'+'&task_id='+task_id,
                                    'data' : function (node) {
                                        return { 'id' : node.id };
                                    }
                                },
                                'themes' : {
                                    'responsive' : true,
                                    'variant' : 'small'
                                    //'stripes' : true
                                }
                            }

                        })
                        .on('changed.jstree', function (e, data) {
                            if(data && data.selected && data.selected.length) {
                                var id = data.selected.join(':');
                                var index = id.indexOf('^');
                                if(index>-1){
                                    id = id.substr(0,index);
                                    var s = '&task_id='+task_id+'&id='+id;
                                    $.get('/detail?action=vul' + s, function (data) {
                                        var d = analyse(data);
                                        if(d !== false){
                                            $('#vul_desc').addClass('hide');
                                            $('#vul_detail').removeClass('hide');
                                            $('#detail_link').html(d.url);
                                            $('#detail_link').attr('href',d.url);
                                            if(d.detail == 'None' || d.detail == ''){
                                                $('#detail_detail_div').addClass('hide');
                                            }else{
                                                $('#detail_detail').html(d.detail);
                                                $('#detail_detail_div').removeClass('hide');
                                            }
                                            $('#detail_request').html(d.request);
                                            $('#detail_response').html(d.response);
                                        }
                                    });
                                }else{
                                    id = id.substr(index-1);
                                    if(id='/'){ // root
                                        return; 
                                    }
                                    var s = '&id='+id;
                                    $.get('/detail?action=desc' + s, function (data) {
                                        var d = analyse(data);
                                        if(d !== false){
                                            $('#vul_detail').addClass('hide');
                                            $('#vul_desc').removeClass('hide');
                                            $('#detail_name').html(d.name);
                                            $('#detail_desc').html(d.description);
                                            $('#detail_solution').html(d.solution);
                                        }
                                    });
                                }
                            }
                        })
                        // .on('click.jstree', function (event){
                        //     alert(event.target.nodeName);
                        // })
                        ;
                }
        );

    });
}

function task_bind_all(){
    task_bind_dblclick();
    task_bind_delete();
    task_bind_detail();
    task_bind_start();
    task_bind_stop();
}

$(function(){
    //按钮删除绑定
    $("#delete_task").bind("click",function(){
        var checked =$("input:checkbox:checked");
        if(checked.length == 0){
            bootbox.alert("请选择扫描任务！");
        }else{
            var task_ids = []
            checked.each(function(){
                task_ids.push($(this).parent().next().html());
            })

            $.post("/task",
                {
                    'action': 'delete',
                    'task_ids': task_ids.join(',')
                },
                function(data){
                    if(analyse(data) !== false){
                        checked.each(function(){
                            $(this).parent().parent().remove();
                        });
                    }               
                }
            );
        }

    });

    //新建扫描任务按钮绑定
    $("#new_task").bind("click",function(){
        $('#task_title').html("新建扫描任务");
        $('#hidden_id').val(0);
        $('#task_name').val('');
        $('#task_name').attr('placeholder','扫描测试');
        $('#task_starturl').val('');
        $('#task_starturl').attr('placeholder','http://www.baidu.com.cn/');
        $('#task_base').val('/');
        $('#task_urlcount').val(0);
        $('#createScan').modal('show');
    });

    task_bind_all();
    
})

function createTask(){
    var task_name = $("#task_name").val();
    var task_starturl = $("#task_starturl").val();
    var task_base = $("#task_base").val();
    var task_urlcount = $("#task_urlcount").val();

    var task_id = $("#hidden_id").val();
    if(task_id == 0){
        //new
        $.post("/task",
            {
                'action': 'create',
                'task_name': task_name,
                'task_starturl': task_starturl,
                'task_base': task_base,
                'task_urlcount': task_urlcount 
            },
            function(data){
                $('tbody .showcounter').each(function(){
                    $(this).html(parseInt($(this).html())+1);
                });
                $('tbody').prepend(data);
                task_bind_all();
                $('#createScan').modal('hide');
            }
        );

    }else{
        //edit
        $.post("/task",
            {
                'action': 'edit',
                'task_id': task_id,
                'task_name': task_name,
                'task_starturl': task_starturl,
                'task_base': task_base,
                'task_urlcount': task_urlcount 
            },
            function(data){
                $('tbody .hide').each(function(){
                    if($(this).html() == task_id){
                        var node = $(this).parent();
                        node.children(":eq(3)").html(task_name);
                    }
                });
                $('#createScan').modal('hide');
            }
        );

    }
}
