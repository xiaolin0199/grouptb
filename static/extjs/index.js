Ext.onReady(function(){
	Ext.widget('viewport', {
		padding: 5,
		layout: 'card',
		items: [{
			xtype: 'grid',
			tbar: [{
				text: '添加',
				action: 'addItem'
			}, {
				text: '编辑',
				action: 'editItem'
			}, {
				text: '删除',
				action: 'deleteItem'
			}, {
				xtype: 'tbtext',
				style: {marginLeft: 30},
				id: 'spread-crumbs'
			}],
			parent_areas: [],
			columns: {
				defaults: {draggable: false,menuDisabled: true,sortable: false},
				items: [{
			        "text": "记录id",
			        "dataIndex": "group_id"
			    }, {
			        "text": "名称",
			        "dataIndex": "name",
			        renderer: function(v){
			        	return '<a href="javascript:void(0);" action="down" title="' + v + '">' + v + '</a>';
			        }
			    }, {
			        "text": "上级节点id",
			        "dataIndex": "parent_id"
			    }, {
			        "text": "桌面预览服务商",
			        width: 120,
			        "dataIndex": "desktop_preview_provider"
			    }, {
			        "text": "桌面预览服务bucket名",
			        width: 160,
			        "dataIndex": "desktop_preview_bucket"
			    }, {
			        "text": "桌面预览服务用户名",
			        width: 140,
			        "dataIndex": "desktop_preview_username"
			    }, {
			        "text": "桌面预览服务密码",
			        width: 130,
			        "dataIndex": "desktop_preview_password"
			    }, {
			        "text": "网盘服务商",
			        "dataIndex": "storage_provider"
			    }, {
			        "text": "网盘服务bucket名",
			        width: 130,
			        "dataIndex": "storage_bucket"
			    }, {
			        "text": "网盘服务access key",
			        width: 160,
			        "dataIndex": "storage_access"
			    }, {
			        "text": "网盘服务secret key",
			        width: 160,
			        "dataIndex": "storage_secret"
			    }, {
			        "text": "备注",
			        "dataIndex": "remark"
			    }]
			},
			store: new Ext.data.Store({
				autoLoad: true,
				fields: ["group_id","name","parent_id","desktop_preview_provider","desktop_preview_bucket","desktop_preview_username","desktop_preview_password","storage_provider","storage_bucket","storage_access","storage_secret","remark"],
				proxy: {
					url: 'grouptb/list/',
					type: 'ajax',
					reader: {
						type: 'json',
						root: 'data.records',
						totalProperty: 'data.record_count'
					}
				},
				pageSize: 1000
			}),
			listeners: {
				itemclick: function(v, rc, el, i, e){
					var action = e.target.getAttribute('action');
					if(action == "down") {
						this.store.load({params: {parent_id: rc.get('group_id')}});
						this.parent_areas.push({id: rc.get('group_id'), name: rc.get('name')});
					}
				},
				afterrender: function(){
					var me = this;
					Ext.each(this.down('toolbar[dock=top]').query('button'), function(btn){
						btn.setHandler(me[btn.action], me);
					});
					Ext.getCmp('spread-crumbs').el.on('click', function(e){
						var arr = this.parent_areas, tmp, tid = e.target.getAttribute('data-id');
						tid = parseInt(tid);
						tmp = arr.pop() || {};
						while(tmp.id !== tid) {
							tmp = arr.pop()||{};
							if(!arr.length) { break; }
						}
						arr.push(tmp);
						me.store.load({params: {parent_id: tid}});
					}, me, {delegate: 'a'})
					me.store.on('load', me.updateCrumbs, me);
				},
			},
			updateCrumbs: function(){
				var htmls = [], arr = this.parent_areas,i, len;
				for(i=0,len=arr.length;i<len;i++) {
					if(i+1 === len) {
						htmls.push(arr[i].name);
					} else {
						htmls.push('<a href="javascript:void(0);" data-id="' + arr[i].id + '">' + arr[i].name + '</a>');
					}
				}
				Ext.getCmp('spread-crumbs').el.dom.innerHTML = htmls.join('&gt;');
			},
			getSelectItem: function(){
				var sel = this.getSelectionModel().getSelection();
				if(sel.length === 0) {
					Ext.Msg.alert('提示', '请先选择一条记录!');
				}
				return sel[0];
			},
			addItem: function(){
				var item = this.getSelectItem(), config, win;
				if(!item) { return; }
				config = this.getItemWindowConfig('添加记录')
				win = Ext.widget(config);
				win.submitUrl = 'grouptb/add/';
				win.show();
				win.down('[name=parent]').setValue(item.get('group_id'));
			},
			editItem: function(){
				var item = this.getSelectItem(), config, win, fm;
				if(!item) { return; }
				config = this.getItemWindowConfig('编辑记录')
				win = Ext.widget(config);
				win.submitUrl = 'grouptb/edit/';
				win.show();
				fm = win.down('form').getForm();
				fm.setValues(item.data);
				fm.findField('parent').setValue(item.data.parent_id)
			},
			deleteItem: function(){
				var item = this.getSelectItem(), cb;
				if(!item) { return; }
				cb = function(){
					Ext.Ajax.request({
						url: 'grouptb/delete/',
						params: {group_id: item.get('group_id')},
						method: 'POST',
						callback: function(opts, _, resp){
							var data = Ext.decode(resp.responseText);
							if(data.status == "success") {
								item.store.remove(item);
							}
						}
					});
				};
				Ext.Msg.confirm('提示', '确定要删除' + item.get('name') + '吗？', function(b){
					(b == 'yes') && cb();
				});
			},
			getItemWindowConfig: function(title){
				var winc = {
					xtype: 'window',
					title: title,
					__parent: this,
					modal: true,
					closable: false,
					resizable: false,
					width: 650,
					layout: 'fit',
					bodyStyle: {backgroundColor: '#FFF'},
					items: [{
						xtype: 'form',
						border: false,
						margin: 20,
						defaultType: 'textfield',
						layout: 'column',
						defaults: {columnWidth: 0.5, allowBlank: true, labelWidth: 150, margin: '10 0 0 0'},
						items: [{
							name: 'group_id',
							fieldLabel: '编号',
							allowBlank: false
						}, {
					        "name": "name",
					        "fieldLabel": "名称",
					        allowBlank: false,
					        margin: '10 0 0 10'
					    }, {
					    	readOnly: true,
					        "name": "parent",
					        "fieldLabel": "上级节点"
					    }, {
					        "name": "desktop_preview_provider",
					        "fieldLabel": "桌面预览服务商",
					        margin: '10 0 0 10'
					    }, {
					        "name": "desktop_preview_bucket",
					        "fieldLabel": "桌面预览服务bucket名"
					    }, {
					        "name": "desktop_preview_username",
					        "fieldLabel": "桌面预览服务用户名",
					        margin: '10 0 0 10'
					    }, {
					        "name": "desktop_preview_password",
					        "fieldLabel": "桌面预览服务密码"
					    }, {
					        "name": "storage_provider",
					        "fieldLabel": "网盘服务商",
					        margin: '10 0 0 10'
					    }, {
					        "name": "storage_bucket",
					        "fieldLabel": "网盘服务bucket名"
					    }, {
					        "name": "storage_access",
					        "fieldLabel": "网盘服务access key",
					        margin: '10 0 0 10'
					    }, {
					        "name": "storage_secret",
					        "fieldLabel": "网盘服务secret key"
					    }, {
					        "name": "remark",
					        "fieldLabel": "备注",
					        margin: '10 0 0 10'
					    }]
					}],
					buttonAlign: 'center',
					buttons: [{
						text: '保存',
						handler: function(){
							var win = this.up('window'),
								fm = win.down('form').getForm(),
								store = win.__parent.store;
							if(!fm.isValid()) { return; }
							fm.submit({
								url: win.submitUrl,
								success: function(_, action){
									var data = action.result;
									if(data.status == "success") {
										store.reload();
									}
									win.destroy();
								},
								failure: function(){win.destroy();}
							});

						}
					}, {
						text: '关闭',
						handler: function(){
							this.up('window').destroy();
						}
					}]
				};
				return winc;
			}
		}, {
			xtype: 'treepanel',
			store: new Ext.data.TreeStore({
				root: {text: 'root'}
			})
		}]
	});
});
