odoo.define('plustech_account_reports.account_report_analytic_group', function (require) {
'use strict';

var core = require('web.core');
var Context = require('web.Context');
var AbstractAction = require('web.AbstractAction');
var Dialog = require('web.Dialog');
var datepicker = require('web.datepicker');
var session = require('web.session');
var field_utils = require('web.field_utils');
var RelationalFields = require('web.relational_fields');
var StandaloneFieldManagerMixin = require('web.StandaloneFieldManagerMixin');
var { WarningDialog } = require("@web/legacy/js/_deprecated/crash_manager_warning_dialog");
var Widget = require('web.Widget');
var accountReportsWidget = require('account_reports.account_report');
var QWeb = core.qweb;
var _t = core._t;

    
    var M2MBranchFilters_1 = Widget.extend(StandaloneFieldManagerMixin, {
        /**
         * @constructor
         * @param {Object} fields
         */
        init: function (parent, fields) {
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.fields = fields;
            this.widgets = {};
        },
        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var defs = [this._super.apply(this, arguments)];
            _.each(this.fields, function (field, fieldName) {
                defs.push(self._makeM2MWidget(field, fieldName));
            });
            return Promise.all(defs);
        },
        /**
         * @override
         */
        start: function () {
            var self = this;
            var $content = $(QWeb.render("m2mWidgetTable", {fields: this.fields}));
            self.$el.append($content);
            _.each(this.fields, function (field, fieldName) {
                self.widgets[fieldName].appendTo($content.find('#'+fieldName+'_field'));
            });
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * This method will be called whenever a field value has changed and has
         * been confirmed by the model.
         *
         * @private
         * @override
         * @returns {Promise}
         */
        _confirmChange: function () {
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(this, arguments);
            var data = {};
            _.each(this.fields, function (filter, fieldName) {
                data[fieldName] = self.widgets[fieldName].value.res_ids;
            });
            this.trigger_up('value_changed_analytic_group', data);
            return result;
        },
        /**
         * This method will create a record and initialize M2M widget.
         *
         * @private
         * @param {Object} fieldInfo
         * @param {string} fieldName
         * @returns {Promise}
         */
        _makeM2MWidget: function (fieldInfo, fieldName) {
            var self = this;
            var options = {};
            options[fieldName] = {
                options: {
                    no_create_edit: true,
                    no_create: true,
                }
            };
            return this.model.makeRecord(fieldInfo.modelName, [{
                fields: [{
                    name: 'id',
                    type: 'integer',
                }, {
                    name: 'display_name',
                    type: 'char',
                }],
                name: fieldName,
                relation: fieldInfo.modelName,
                type: 'many2many',
                value: fieldInfo.value,
            }], options).then(function (recordID) {
                self.widgets[fieldName] = new RelationalFields.FieldMany2ManyTags(self,
                    fieldName,
                    self.model.get(recordID),
                    {mode: 'edit',}
                );
                self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
            });
        },
    });




    accountReportsWidget.include({

        custom_events: _.extend({}, accountReportsWidget.prototype.custom_events, {

            'value_changed_analytic_group': function(ev) {
                var self = this;

                self.report_options.analytic_group_ids = ev.data.analytic_group;
                return self.reload().then(function () {
                    self.$searchview_buttons.find('.account_analytic_group_filter').click();
                });
             },
        }),

        render_searchview_buttons: function() {
            var self = this;

            self._super();

            // Anaylitic group filter

            if (this.report_options.analytic_group) {
                
                if (!this.M2MBranchFilters_1) {
                    var fields = {};
                    if ('analytic_group_ids' in this.report_options) {
                        fields['analytic_group'] = {
                            label: _t('Analytic Group'),
                            modelName: 'account.analytic.group',
                            value: this.report_options.analytic_group_ids.map(Number),
                        };
                    }

                    if (!_.isEmpty(fields)) {
                        this.M2MBranchFilters_1 = new M2MBranchFilters_1(this, fields);
                        this.M2MBranchFilters_1.appendTo(this.$searchview_buttons.find('.js_account_analytic_group_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find('.js_account_analytic_group_m2m').append(this.M2MBranchFilters_1.$el);
                }
            }

         
        },

    });

});
