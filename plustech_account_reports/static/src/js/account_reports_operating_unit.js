odoo.define('plustech_account_reports.account_reports_operating_unit', function (require) {
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


    var M2MBranchFilters = Widget.extend(StandaloneFieldManagerMixin, {
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
            var $content = $(QWeb.render("m2mWidgetTable", { fields: this.fields }));
            self.$el.append($content);
            _.each(this.fields, function (field, fieldName) {
                self.widgets[fieldName].appendTo($content.find('#' + fieldName + '_field'));
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
            this.trigger_up('value_changed', data);
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
                    { mode: 'edit', }
                );
                self._registerWidget(recordID, fieldName, self.widgets[fieldName]);
            });
        },
    });




    accountReportsWidget.include({

        custom_events: _.extend({}, accountReportsWidget.prototype.custom_events, {

            'value_changed': function (ev) {
                var self = this;

                console.log(ev.data)
                self.report_options.operating_unit_ids = ev.data.operating_unit_id;
                self.report_options.partner_ids = ev.data.partner_ids;
                self.report_options.partner_categories = ev.data.partner_categories;
                self.report_options.analytic_accounts = ev.data.analytic_accounts;
                self.report_options.analytic_tags = ev.data.analytic_tags;
                return self.reload().then(function () {
                    self.$searchview_buttons.find('.account_partner_filter').click();
                    self.$searchview_buttons.find('.account_analytic_filter').click();
                    self.$searchview_buttons.find('.account_operating_unit_id_filter').click();
                });
            },
        }),

        render_searchview_buttons: function () {
            var self = this;

            self._super();

            if (self.report_options.operating_unit_id) {
                if (!self.M2MBranchFilters) {
                    var fields = {};
                    if (self.report_options.operating_unit_id) {
                        fields['operating_unit_id'] = {
                            label: _t('Operating Unit'),
                            modelName: 'operating.unit',
                            value: self.report_options.operating_unit_ids.map(Number),
                        };
                    }

                    if (!_.isEmpty(fields)) {
                        self.M2MBranchFilters = new M2MBranchFilters(self, fields);
                        self.M2MBranchFilters.appendTo(self.$searchview_buttons.find('.js_account_operating_unit_id_m2m'));
                    }
                } else {
                    self.$searchview_buttons.find('.js_account_operating_unit_id_m2m').append(self.M2MBranchFilters.$el);
                }
            }
        },

    });

});
