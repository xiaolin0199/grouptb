$(function() {
    'use strict';
    /* 目录：
     * 0. 预定义function
     *    0.1 load_group_tree载入左侧菜单的区县树形
     *    0.2 load_table载入右侧正文的表格
     *    0.3 load_chart载入右侧正文的趋势图
	 *    0.4 load_details 
     * 1. 载入页面时的初始化工作：
     *    1.1 载入左侧菜单的树形
     *    1.2 载入右侧表格
     * 2. 左侧菜单绑定点击事件：
     *    2.1 切换active
     *    2.2 更新右侧的标题
     *    2.3 更新右侧的内容
     * 3. 为左侧菜单的树形绑定点击事件：
     *    3.1 切换active
     *    3.2 更新右侧的标题
     *    3.3 更新右侧内容->趋势图
     */
    /* 0 ------------------------------------------------------------------  */
    var load_group_tree = function() {
        $.get('group-tree/', function(response) {
            var tree = response.data.tree;
            var tree_data = new Array();
            tree_data.push({'text': '省级列表', 'children': []});
            for(var province_id in tree) {
                if(tree.hasOwnProperty(province_id)) {
                    var cities = tree[province_id].children;
                    var city_array = new Array();
                    for(var city_id in cities) {
                        if(cities.hasOwnProperty(city_id)) {
                            var countries = cities[city_id].children;
                            var country_array = new Array();
                            for(var country_id in countries) {
                                if(countries.hasOwnProperty(country_id)) {
                                    country_array.push({
                                        'data': 'country',
                                        'id': country_id,
                                        'text': countries[country_id].name,
                                    });
                                }
                            }
                            city_array.push({
                                'data': 'city',
                                'id': city_id,
                                'text': cities[city_id].name,
                                'children': country_array,
                            });
                        }
                    }
                    tree_data[0].children.push({
                        'data': 'province',
                         'id': province_id,
                         'text': tree[province_id].name,
                         'children': city_array,
                    });
                }
            }
            $('#myTree').jstree({
                'core' : {
                    'data' : tree_data,
                    'multiple': false,
                },
                'plugins' : ['sort', 'wholerow'],
                'sort': function(id1, id2) {
                    return id1 > id2 ? 1 : -1;
                },
            });
        });
    };

    /* 初始化表格 */
    var load_table = function() {
        $('#myTable').bootstrapTable({
            url: 'dailylog/',
            classes: 'table table-striped',
            columns: [{
                field: 'log_datetime',
                title: '日期',
                sortable: false,
            }, {
                field: 'usage',
                formatter: function(value) {
                    return parseInt(value) / 1024.0 / 1024 / 1024;
                },
                title: '空间使用量（GB）',
                sortable: false,
            }],
            pagination: true,
            responseHandler: function(ret) {
                return ret.data.records;
            },
            striped: true,
        });
    };
	var chart_object;
    var load_chart = function(url, name) {
        $.get(url, function(response) {
            var records = response.data.records;
            var length = records.length;
            var chart_data = new Array(length);
            /* 取中间值和最近值，平均之后判断一下，用GB/MB/KB/字节做单位 */
            var usage_array = new Array(length);
            for(var i = 0; i < length; i++) {
                usage_array[i] = records[i].usage;
            }
            var usage_max = Math.max.apply(null, usage_array);
            var usage_min = Math.min.apply(null, usage_array);
            var unit = '';
            var factor = 0;
            var usage = (usage_max + usage_min) / 2;
            console.log('%s %s %s', usage_max, usage, usage_min);
            if(usage < 1024) {
                unit = '字节';
                factor = 1;
            } else if(usage < 1024 * 1024) {
                unit = 'KB';
                factor = 1024;
            } else if(usage < 1024 * 1024 * 1024) {
                 unit = 'MB';
                 factor = 1024 * 1024;
            } else {
                unit = 'GB';
                factor = 1024 * 1024 * 1024;
            }
			// 最小的单位是 KB
			factor = 1;
            for(var i = 0; i < length; i++) {
                chart_data[i] = [
                    new Date(records[length - 1 - i].log_datetime),
                    records[length - 1 - i].usage / factor,
                ];
            }
			if(!chart_object) {
				chart_object = new Dygraph(
					document.getElementById('nav-menuitem-2-content'),
					chart_data,
					{
						axes: {
							x: {
								axisLabelFormatter: function(ms){
									return (new Date(ms)).toISOString().substr(0, 10);
								},
								valueFormatter: function(ms) {
									return (new Date(ms)).toISOString().substr(0, 10);
								},
							},
							y: {
								labelsKMG2: true
							}
						},
						 height: 480,
						 labels: ['日期', '使用量'],
						 title: name + ' 左键选取放大范围；按住shift拖动；双击缩小还原。',
						 width: 800,
						 valueFormatter: function(x, opts, name, g, row, col){
							 var unit, factor;
							 if(x < 1024) {
								unit = 'bytes';
								factor = 1;
							} else if(x < 1024 * 1024) {
								unit = 'KB';
								factor = 1024;
							} else if(x < 1024 * 1024 * 1024) {
								 unit = 'MB';
								 factor = 1024 * 1024;
							} else {
								unit = 'GB';
								factor = 1024 * 1024 * 1024;
							}
							return (x/factor).toFixed(2) + unit;
						 }
					}
				);
			} else {
				chart_object.updateOptions({file: chart_data});
			}
        });
    };

	var load_details = function(){
		var table = $('#usage-table');
		if(table.data('rendered')) {
			table.bootstrapTable('refresh');
			return;
		}
		table.data('rendered', true).bootstrapTable({
            url: 'districts-usage/',
            classes: 'table table-striped',
            columns: [{
				field: 'upyungrouptb__grouptb__parent__name',
				title: '城市',
				sortable: false
			}, {
                field: 'upyungrouptb__grouptb__name',
                title: '区县',
                sortable: false,
            }, {
                field: 'usage',
                formatter: function(value) {
                    return parseInt(value) / 1024.0 / 1024 / 1024;
                },
                title: '空间使用量（GB）',
                sortable: false,
            }],
            pagination: true,
            responseHandler: function(ret) {
				$('#last-update-at').text(ret.log_datetime);
                return ret.usage;
            },
            striped: true,
        });
	};

    /* 1 ------------------------------------------------------------------  */
    load_group_tree();
    load_table();

    /* 2 ------------------------------------------------------------------  */
	$('[data-menuitem]').click(function(e){
		var me = $(this), current;
		current = me.closest('.sidebar').find('.active');
		if(current[0] === me[0]) { return; }
		current.removeClass('active');
		$('#' + current.attr('id') + '-content').hide();
		me.addClass('active');
		$('#page-header').text(me.attr('data-menuitem'));
		$('#' + me.attr('id') + '-content').show();
		({
			'nav-menuitem-1': load_table,
			'nav-menuitem-2': function(){ load_chart('dailylog/', '全网'); },
			'nav-menuitem-3': load_details,
		})[me.attr('id')]();
	});
	/*
    $('#nav-menuitem-1').click(function(e) {
        if($(this).hasClass('active')) return;
        $(this).addClass('active');
        $('#nav-menuitem-2').removeClass('active');
        $('#page-header').text('全网空间使用量');
        $('#page-content').removeClass('row').addClass('table-responsive')
            .html('<table id="myTable"></table>');
        load_table();
    });
    $('#nav-menuitem-2').click(function(e) {
        if($(this).hasClass('active')) return;
        $(this).addClass('active');
        $('#nav-menuitem-1').removeClass('active');
        $('#page-header').text('趋势');
        $('#page-content').removeClass('table-responsive').addClass('row').children().remove();
        load_chart('dailylog/', '全网');
    });
	*/
    $('#myTree').on('select_node.jstree', function(e, data) {
		$('#nav-menuitem-2').trigger('click');
        if(data.node.data === 'country') {
            load_chart('detaillog/?group_id=' + data.node.id, data.node.text);
        }
    });
});
