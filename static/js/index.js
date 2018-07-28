$(function(){
    var pageSize = 20;
    var bbt = {
        setLoading: function(flag){
            var el = $('#myModal');
            el.modal(flag ? "show" : "hide");
        },
        updateUsage: function(group){
            var url, group = group || '';
            url = group ? "/upyun/detaillog/?group_id=" + group : "/upyun/dailylog/";
            this.setLoading(true);
            $.ajax({
                url: url,
                success: function(data){
                    var htmls, pager, i, len, pagerEl;
                    if(data && data.success) {
                        len = data.data.records.length;
                        htmls = [];
                        pager = [];
                        for(i=0;i<len;i+=pageSize) {
                            pager.push(data.data.records.slice(i, Math.min(i+pageSize, len)));
                        }
                        $.each(pager, function(i, piece){
                            htmls.push('<li data-page="' + i + '"><a href="javascript:void(0);">' + (i + 1) + '</a></li>');
                        });
                        pagerEl = bbt.getGroupPanel(group).children('.pagination');
                        pagerEl.find('[data-page]').remove();
                        pagerEl.find('[data-role=prev]').after(htmls.join(''));
                        pagerEl.find('[data-page]').each(function(x){
                            $(this).data('pagedata', pager[x]);
                        }).first().trigger('click');
                        /*$.each(data.data.records, function(i, item){
                            htmls.push("<tr><td>" + item.log_datetime + "</td><td>" + (item.usage/Math.pow(1024, 3)).toFixed(3) + "</td></tr>");
                        });
                        bbt.getGroupPanel(group).find('tbody').html(htmls.join(''));*/
                    }
                },
                complete: function(){
                    bbt.setLoading(false);
                }
            });
        },
        updateGroups: function(){
            $.get('/upyun/group/', function(data){
                var htmls = [];
                if(data.success) {
                    $.each(data.data.records, function(i, item){
                        var name = item.grouptb__name;
                        if(name == "直属") {
                            name += "( " + item.grouptb__group_id + " )";
                        }
                        htmls.push('<li group="' + item.grouptb__group_id + '"><a href="javascript:void(0);">' + name + '</a></li>');
                    });
                    $('#navbar').append(htmls.join(''));
                }
            });
        },
        getGroupPanel: function(group){
            var el = $('#group-' + (group||'all')), panel;
            if(!el.length) {
                el = $($.trim($('#group-template').html()));
                el.attr('id', 'group-' + group);
                el.appendTo($('#group-panel-container'));
            }
            return el;
        },
        activeGroup: function(group){
            var navbar = $('#navbar'), current;
            group = group || 'all';
            current = navbar.children('.active');
            if(current.attr('group') == group) { return; }
            current = current.removeClass('active').attr('group');
            this.getGroupPanel(current).hide();
            navbar.children('[group=' + group + ']').addClass('active');
            this.getGroupPanel(group).show();
        },
        getCurrentGroup: function(){
            return $('#navbar').children('.active').attr('group') || 'all';
        },
        init: function(){
            $('#group-panel-container').delegate('li', 'click', function(e){
                var me = $(this), data, body, htmls = [];
                
                if(me.attr('data-role') == "prev") {
                    me.siblings('.active').prev('[data-page]').trigger('click');
                    return;
                } else if(me.attr('data-role') == "next") {
                    me.siblings('.active').next('[data-page]').trigger('click');
                    return;
                }
                if(me.hasClass('active')) { return; }
                data = me.data('pagedata')
                me.siblings('.active').removeClass('active');
                body = me.closest('.group-panel').find('tbody');
                $.each(data, function(i, item){
                    htmls.push("<tr><td>" + item.log_datetime + "</td><td>" + (item.usage/Math.pow(1024, 3)).toFixed(3) + "</td></tr>");
                });
                body.html(htmls.join(''));
                me.addClass('active');
                return false;
            });
            this.updateUsage();
            this.updateGroups();
        }
    };
    var calculate = function(){
        var usageUnit = $('#usage-unit'),
            v = usageUnit.val(),
            num = parseInt(v),
            group = bbt.getCurrentGroup();
        if(isNaN(num)) {
            v && usageUnit.popover('show');
        } else {
            bbt.getGroupPanel(group).find('tbody').children('tr').each(function(){
                var row = $(this), v;
                row.attr('class', '');
                v = row.children('td').eq(1).text();
                v = parseFloat(v) || 0;
                if(v > num) {
                    row.addClass('error');
                } else if(v == num) {
                    row.addClass('warning');
                }
            });
        }
    };

    bbt.init();
    $("#usage-unit").keyup(function(e){
        var code = e.keyCode;
        if(code === 13) {
            calculate();
        }
    }).focus(function(){
        $(this).popover('hide');
    }).blur(calculate).popover({
        trigger: 'manual',
        title: '提示',
        content: '无效的数字！',
        placement: 'bottom'
    });
    $('#navbar').delegate('li', 'click', function(){
        var me = $(this), group = me.attr('group');
        if(me.hasClass('active')) { return; }
        bbt.activeGroup(group);
        bbt.updateUsage(group);
        return false;
    });
    $('#refresh').click(function(){
        var group = $('#navbar').children('.active').attr('group');
        bbt.activeGroup(group);
        bbt.updateUsage(group);
    });
    $('#myModal').modal({keyboard: false});
});
