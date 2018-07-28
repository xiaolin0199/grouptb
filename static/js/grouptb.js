$(function() {
    'use strict';
    /* 目录：
     * 1. 初始化导航条和表格的显示
     * 2. load_data公共函数
     * 3. 事件绑定
     *     3. 点击导航条
     *     4. 点击工具栏
     *     1. 点击表格的group_id列
     *     2. 点击表格的操作列中的每个按钮
     */
    /* 初始化breadcrumb */
    $('.breadcrumb li:first-child').addClass('active');
    /* 初始化表格 */
    $('#table').bootstrapTable({
        url: 'list/',
        classes: 'table table-hover table-condensed',
        columns: [{
            /* 显示操作按钮：删除，编辑…… */
            title: '操作',
            sortable: false,
            width: 80,
            formatter: function(value, row, index) {
                var html = '';
                html += '<div class="btn-group">';
                html += '    <button type="button" class="btn btn-default btn-xs" data-id="' + row.group_id + '">';
                html += '        <i class="glyphicon glyphicon-edit"></i>';
                html += '    </button>';
                html += '    <button type="button" class="btn btn-default btn-xs" data-id="' + row.group_id + '">';
                html += '        <i class="glyphicon glyphicon-cloud"></i>';
                html += '    </button>';
                html += '    <button type="button" class="btn btn-danger btn-xs" data-id="' + row.group_id + '">';
                html += '        <i class="glyphicon glyphicon-trash"></i>';
                html += '    </button>';
                html += '</div>';
                return html;
            },
        }, {
            field: 'group_id',
            formatter: function(value) {
                return '<a href="javascript:void(0);" class="group_id">' + value + '</a>';
            },
            title: '记录id',
            sortable: true,
        }, {
            field: 'name',
            title: '名称',
            sortable: true,
        }, {
            field: 'parent_id',
            title: '上级节点id',
            sortable: true,
        }],
        responseHandler: function(ret) {
            return ret.data.records;
        },
        striped: true,
        toolbar: '#toolbar',
    });

    var load_data = function(parent_id) {
        $('#table').bootstrapTable('refresh', {url: 'list/?parent_id=' + parent_id});
    };

    /* 为breadcrumb绑定点击事件：
     * 1.刷新表格数据
     * 2.清除点击位置之后的导航
     * 3.点击位置去掉<a></a>，设为active
     */
    $('.breadcrumb').on('click', 'a.breadcrumb_item', function() {
        var parent_id = parseInt($(this).parent().attr('data-id')) || '';
        load_data(parent_id);
        $(this).parent().addClass('active').nextAll().remove();
        $(this).contents().unwrap();
    });

    /* 为btn-add绑定点击事件：显示新增记录的bootbox */
    $('#btn-add').click(function(e) {
        var html = '<div class="row">' +
                   '    <div class="col-md-6">' +
                   '        <form class="form-horizontal" role="form">' +
                   '            <div class="form-group">' +
                   '                <label class="col-md-1 control-label" for="group_id">group_id</label>' +
                   '                <div class="col-md-5 pull-right">' +
                   '                    <input id="group_id" name="group_id" type="text" placeholder="记录id" class="form-control" />' +
                   '                </div>' +
                   '            </div>' +
                   '            <div class="form-group">' +
                   '                <label class="col-md-1 control-label" for="name">name</label>' +
                   '                <div class="col-md-5 pull-right">' +
                   '                    <input id="name" name="name" type="text" placeholder="名称" class="form-control" />' +
                   '                </div>' +
                   '            </div>' +
                   '            <div class="form-group">' +
                   '                <label class="col-md-1 control-label" for="parent_id">parent_id</label>' +
                   '                <div class="col-md-5 pull-right">' +
                   '                    <input id="parent_id" name="parent_id" type="text" placeholder="上级id" class="form-control" />' +
                   '                </div>' +
                   '            </div>' +
                   '        </form>' +
                   '    </div>' +
                   '</div>';
        bootbox.dialog({
            message: html,
            title: '新增节点',
            buttons: {
                Cancel: {
                    label: 'Cancel',
                    className: 'btn-default',
                },
                Save: {
                    label: 'Save',
                    className: 'btn-primary',
                    callback: function(e) {
                        var group_id = $('#group_id').val();
                        var name = $('#name').val();
                        var parent_id = parseInt($('.breadcrumb li:last-child').attr('data-id')) || '';
                        var csrftoken = $.cookie('csrftoken');
                        var post_data = {
                            'group_id': group_id,
                            'name': name,
                            'parent': parent_id, // 注意key与grouptb_app.models.GroupTB一致
                        };
                        console.log('group_id:', group_id, name, parent_id);
                        $.ajax({
                            beforeSend: function(xhr) {
                                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                            },
                            url: 'add/',
                            type: 'POST',
                            data: post_data,
                            success: function(ret) {
                                /* {"success": true, "msg": "添加成功"} */
                                if(ret.success) {
                                    load_data(parent_id);
                                } else {
                                    console.log(ret);
                                }
                            },
                        });
                    },
                },
            },
        }).init(function(e) {
            var parent_id = parseInt($('.breadcrumb li:last-child').attr('data-id')) || '';
            var parent_name = $('.breadcrumb li:last-child').text().trim();
            $('#group_id').val('');
            $('#name').val('');
            $('#parent_id').val(parent_name).prop('disabled', true);
        });
    });
    /* 为btn-refresh绑定点击事件：刷新表格 */
    $('#btn-refresh').click(function(e) {
        var parent_id = parseInt($('.breadcrumb li:last-child').attr('data-id')) || '';
        load_data(parent_id);
    });

    /* 表格第一列的按钮 */
    $('#table').on('click', 'button', function(event) {
        var icon_class = $(this).children().attr('class');
        var group_id = $(this).parent().parent().parent().find('td>a.group_id').html();
        var parent_id = parseInt($('.breadcrumb li:last-child').attr('data-id')) || '';
        var csrftoken = $.cookie('csrftoken');
        if(icon_class.indexOf('glyphicon-edit') > -1) {
            /* 为表格的编辑按钮绑定点击事件：
             */
            console.log('edit clicked');
        } else if(icon_class.indexOf('glyphicon-cloud') > -1) {
            /* 为表格的cloud按钮绑定点击事件：
             * 1.弹出云资源状态框
             */
            var html = '<table id="cloud-table"></table>';
            bootbox.dialog({
                message: html,
                size: 'large',
                title: '云资源状态',
            });
            $('#cloud-table').bootstrapTable({
                url: 'cloud-info/?group_id=' + group_id,
                classes: 'table table-hover table-condensed',
                columns: [{
                    field: 'provider',
                    title: '云服务',
                    align: 'center',
                    valign: 'middle',
                    formatter: function(value, row, index) {
                        if(value === 'qiniu') {
                            return '<img src="http://assets.qiniu.com/qiniu-122x65.png" />';
                        } else if(value === 'upyun') {
                            return '<img src="http://upfiles.b0.upaiyun.com/logo/120x60.png" />';
                        }
                    },
                }, {
                    field: 'opened',
                    title: '已开通',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'username',
                    title: '账号',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'password',
                    title: '密码',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'bucket',
                    title: '空间名',
                    align: 'center',
                    valign: 'middle',
                }, {
                    field: 'space_used',
                    title: '已使用/限额',
                    align: 'center',
                    valign: 'middle',
                }],
                responseHandler: function(ret) {
                    return ret.data.records;
                },
                striped: true,
            });
        } else if(icon_class.indexOf('glyphicon-trash') > -1) {
            /* 为表格的删除按钮绑定点击事件：
             * 1.删除记录
             * 2.成功的话刷新表格
             * 3. TODO 失败的话显示错误信息
             */
            bootbox.confirm({
                size: 'small',
                message: 'Are you quèdìng?',
                callback: function(result) {
                    if(!result) return;
                    var post_data = {
                        'group_id': group_id,
                    };
                    $.ajax({
                        beforeSend: function(xhr) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        },
                        url: 'delete/',
                        type: 'POST',
                        data: post_data,
                        success: function(ret) {
                            if(ret.success) {
                                load_data(parent_id);
                            } else {
                                console.log(ret);
                            }
                        },
                    });
                },
            });
        }
    });

    /* 为表格的group_id单元绑定点击事件：
     * 1.刷新表格数据
     * 2.更新breadcrumb导航
     */
    $('#table').on('click', 'a.group_id', function(event) {
        var parent_id = parseInt($(this).html()) || '';
        var parent_name = $(this).parent().next().html();
        /* 为breadcrumb导航增加一个新的节点：
         * 1.去掉末尾节点的active，为末尾节点增加<a></a>
         * 2.增加一个新的末尾节点，其中data-id用于点击该导航项时传递参数刷新表格
         */
        var append_breadcrumb = function(group_id, name) {
            $('.breadcrumb li:last-child').removeClass('active')
                .wrapInner('<a href="javascript:void(0);" class="breadcrumb_item"></a>');
            $('.breadcrumb').append('<li class="active" data-id="' + group_id + '">' + name + '</li>');
        };
        load_data(parent_id);
        append_breadcrumb(parent_id, parent_name);
    });
});
