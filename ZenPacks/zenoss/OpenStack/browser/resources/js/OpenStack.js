(function(){

var ZC = Ext.ns('Zenoss.component');

ZC.registerName('OpenStackFlavor', _t('Flavor'), _t('Flavors'));
ZC.registerName('OpenStackImage', _t('Image'), _t('Images'));
ZC.registerName('OpenStackServer', _t('Server'), _t('Servers'));

var addOpenStack = new Zenoss.Action({
    text: _t('Add OpenStack Endpoint (User)') + '...',
    id: 'addopenstack-item',
    permission: 'Manage DMD',
    handler: function(btn, e){
        // store for the region dropdown
        regionStore = new Zenoss.NonPaginatedStore({
            fields: ['key', 'label'],
            root: 'data',
            directFn: Zenoss.remote.OpenStackRouter.getRegions,
            remoteFilter: false,
            autoload: false
        });

        var win = new Zenoss.dialog.CloseDialog({
            width: 640,
            title: _t('Add OpenStack Endpoint (User)'),
            items: [{
                xtype: 'form',
                id: 'addopenstackuser-form',
                buttonAlign: 'left',
                monitorValid: true,
                labelAlign: 'top',
                footerStyle: 'padding-left: 0',
                border: false,
                items: [{
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'textfield',
                        name: 'device_name',
                        fieldLabel: _t('Device to Create'),
                        labelWidth: 120,
                        id: "openstack_device_name",
                        width: 350,
                        allowBlank: false,
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(Do not use an actual hostname)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'textfield',
                        name: 'auth_url',
                        fieldLabel: _t('Auth URL'),
                        labelWidth: 120,
                        id: "openstack_auth_url",
                        width: 350,
                        allowBlank: false,
                        listeners: {
                            blur: this.updateRegions,
                            scope: this
                        }
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(OS_AUTH_URL)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'textfield',
                        name: 'username',
                        fieldLabel: _t('Username'),
                        labelWidth: 120,
                        id: "openstack_username",
                        width: 350,
                        allowBlank: false,
                        listeners: {
                            blur: this.updateRegions,
                            scope: this
                        }
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(OS_USERNAME)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'password',
                        name: 'api_key',
                        fieldLabel: _t('Password / API Key'),
                        labelWidth: 120,
                        id: "openstack_api_key",
                        width: 350,
                        allowBlank: false,
                        listeners: {
                            blur: this.updateRegions,
                            scope: this
                        }
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(OS_PASSWORD)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'textfield',
                        name: 'project_id',
                        fieldLabel: _t('Project/Tenant ID'),
                        labelWidth: 120,
                        id: "openstack_project_id",
                        width: 350,
                        allowBlank: false,
                        listeners: {
                            blur: this.updateRegions,
                            scope: this
                        }
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(NOVA_PROJECT_ID or OS_TENANT_NAME)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [{
                        xtype: 'combo',
                        width: 350,
                        name: 'region_name',
                        fieldLabel: _t('Region Name'),
                        labelWidth: 120,
                        id: 'region_name',
                        triggerAction: 'all',
                        queryMode: 'local',
                        valueField: 'key',
                        displayField: 'label',
                        store: regionStore,
                        forceSelection: true,
                        editable: false,
                        allowBlank: false,
                        triggerAction: 'all',
                        selectOnFocus: false,
                    },{
                        xtype: 'label',
                        style: 'font-style: italic',
                        text: '(OS_REGION_NAME)',
                        margin: '0 0 0 10'
                    }]
                }, {
                    xtype: 'combo',
                    width: 350,
                    name: 'collector',
                    fieldLabel: _t('Collector'),
                        labelWidth: 120,
                    id: 'openstack_collector',
                    mode: 'local',
                    store: new Ext.data.ArrayStore({
                        data: Zenoss.env.COLLECTORS,
                        fields: ['name']
                    }),
                    valueField: 'name',
                    displayField: 'name',
                    forceSelection: true,
                    editable: false,
                    allowBlank: false,
                    triggerAction: 'all',
                    selectOnFocus: false,
                    listeners: {
                        'afterrender': function(component) {
                            var index = component.store.find('name', 'localhost');
                            if (index >= 0) {
                                component.setValue('localhost');
                            }
                        }
                    }
                }],
                buttons: [{
                    xtype: 'DialogButton',
                    id: 'addOpenStackdevice-submit',
                    text: _t('Add'),
                    formBind: true,
                    handler: function(b) {
                        var form = b.ownerCt.ownerCt.getForm();
                        var opts = form.getFieldValues();

                        Zenoss.remote.OpenStackRouter.addOpenStack(opts,
                        function(response) {
                            if (response.success) {
                                if (Zenoss.JobsWidget) {
                                    Zenoss.message.success(_t('Add OpenStack job submitted.'));
                                } else {
                                    Zenoss.message.success(
                                        _t('Add OpenStack job submitted. <a href="/zport/dmd/JobManager/jobs/{0}/viewlog">View Job Log</a>'),
                                        response.jobId);
                                }
                            }
                            else {
                                Zenoss.message.error(_t('Error adding OpenStack: {0}'),
                                    response.msg);
                            }
                        });
                    }
                }, Zenoss.dialog.CANCEL]
            }]
        });

        win.show();
    },

    updateRegions: function () {
        form = Ext.getCmp('addopenstackuser-form').getForm();
        formvalues = form.getFieldValues();
        combo = Ext.getCmp('region_name');
        store = combo.getStore();

        if (formvalues.username && formvalues.api_key && formvalues.project_id && formvalues.auth_url) {
            store.load({
               params: {
                   username: formvalues.username,
                   api_key: formvalues.api_key,
                   project_id: formvalues.project_id,
                   auth_url: formvalues.auth_url
               },
               callback: function(records, operation, success) {
                    combo.select(store.getAt(0));
                    combo.fireEvent('select');
               }
            });
        } else {
            store.removeAll()
        }
    }
});

// Push the addOpenStack action to the adddevice button
Ext.ns('Zenoss.extensions');
Zenoss.extensions.adddevice = Zenoss.extensions.adddevice instanceof Array ?
                              Zenoss.extensions.adddevice : [];
Zenoss.extensions.adddevice.push(addOpenStack);


/*
 * Inspectors.
 */
var NS = Ext.namespace('Zenoss.zenpacks.OpenStack');


// OpenStackEndPoint Inspector
function addOpenStackEndPointInspectorFields(inspector) {
    inspector.addPropertyTpl(_t('Device Name'), '{values.device_name}');
    inspector.addPropertyTpl(_t('Username'), '{values.username}');
    inspector.addPropertyTpl(_t('Project ID'), '{values.project_id}');
    inspector.addPropertyTpl(_t('Auth URL'), '{values.auth_url}');
    inspector.addPropertyTpl(_t('Region Name'), '{values.region_name}');
    inspector.addPropertyTpl(_t('Total Servers'), '{values.serverCount}');
    inspector.addPropertyTpl(_t('Total Flavors'), '{values.flavorCount}');
    inspector.addPropertyTpl(_t('Total Images'), '{values.imageCount}');
}

if (Ext.define === undefined) {
    // Compatibility with Zenoss versions earlier than 4.2.
    NS.OpenStackEndpointInspector = Ext.extend(Zenoss.inspector.DeviceInspector, {
        constructor: function(config) {
            NS.OpenStackEndpointInspector.superclass.constructor.call(this, config);
            addOpenStackEndPointInspectorFields(this);
        }
    });

    Ext.reg('OpenStackEndpointInspector', NS.OpenStackEndpointInspector);
} else {
    // Zenoss 4.2+ compatibility.
    Ext.define("Zenoss.zenpacks.OpenStack.OpenStackEndpointInspector", {
        extend: "Zenoss.inspector.DeviceInspector",
        alias: ["widget.OpenStackEndpointInspector"],
        constructor: function(config) {
            this.callParent(arguments);
            addOpenStackEndPointInspectorFields(this);
        }
    });
}

Zenoss.inspector.registerInspector('OpenStackEndpoint', 'OpenStackEndpointInspector');


// OpenStackServer Inspector
function addOpenStackServerInspectorFields(inspector) {
    inspector.addPropertyTpl(_t('Guest Device'),
        '{[Zenoss.render.link(values.guestDevice)]}');

    inspector.addPropertyTpl(_t('Server Status'), '{values.serverStatus}');
    inspector.addPropertyTpl(_t('Public IPs'), '{values.publicIps}');
    inspector.addPropertyTpl(_t('Private IPs'), '{values.privateIps}');
    inspector.addPropertyTpl(_t('Flavor'),
        '{[Zenoss.render.link(values.flavor)]}');

    inspector.addPropertyTpl(_t('Image'),
        '{[Zenoss.render.link(values.image)]}');

    inspector.addPropertyTpl(_t('Host ID'), '{values.hostId}');
}

if (Ext.define === undefined) {
    // Compatibility with Zenoss versions earlier than 4.2.
    NS.OpenStackServerInspector = Ext.extend(Zenoss.inspector.ComponentInspector, {
        constructor: function(config) {
            NS.OpenStackServerInspector.superclass.constructor.call(this, config);
            addOpenStackServerInspectorFields(this);
        }
    });

    Ext.reg('OpenStackServerInspector', NS.OpenStackServerInspector);
} else {
    // Zenoss 4.2+ compatibility.
    Ext.define("Zenoss.zenpacks.OpenStack.OpenStackServerInspector", {
        extend: "Zenoss.inspector.DeviceInspector",
        alias: ["widget.OpenStackServerInspector"],
        constructor: function(config) {
            this.callParent(arguments);
            addOpenStackServerInspectorFields(this);
        }
    });
}

Zenoss.inspector.registerInspector('OpenStackServer', 'OpenStackServerInspector');

}());
