odoo.define('account_custom.account_report', function (require) {
'use strict';

var core = require('web.core');
var account_reports = require('account_reports.account_report');
var Widget = require('web.Widget');

var QWeb = core.qweb;
var _t = core._t;

var accountReportsWidget = account_reports.include({


    events: {
        'click .o_ssss': 'select_all_journals',
    },

    select_all_journals: function () {
        var elements = document.querySelectorAll('.js_account_report_journal_choice_filter');
        var self = this;
        for (var i = 0; i < elements.length; i++) {
            elements[i].classList.add('selected');
        }
        
        // for (var i = 0; i < elements.length; i++) {
        //     console.log("@@@@@@@@@@@@@@@@@@ all",elements[i])
        //     console.log("@@@@@@@@@@@@@@@@@@ $el",$(elements[i]))
        //     self.report_options.__journal_group_action = { 'action': 'add', 'id': parseInt($(elements[i]).data('id')) };
        // }
            // var $el = $(this);
            // // Change the corresponding element in option.
            // var options = _.filter(self.report_options.journals, function (item) {
            //     return item.model == $el.data('model') && item.id.toString() == $el.data('id');
            // });
            // if (options.length > 0) {
            //     let option = options[0];
            //     option.selected = !option.selected;
            // }
            console.log("@@@@@@@@@@@@@@@@@@ option",self.report_options)
            console.log("@@@@@@@@@@@@@@@@@@ option",this.$searchview_buttons)
            console.log("@@@@@@@@@@@@@@@@@@ option ",self.report_options.__journal_group_action)

            // Specify which group has been clicked.
            // if ($el.data('model') == 'account.journal.group') {
            //     if ($el.hasClass('selected')) {
            //         self.report_options.__journal_group_action = { 'action': 'remove', 'id': parseInt($el.data('id')) };
            //     } else {
            //         self.report_options.__journal_group_action = { 'action': 'add', 'id': parseInt($el.data('id')) };
            //     }
            // }
            // self.reload();
    },

    
    
});
// core.action_registry.add('account_report', accountReportsWidget);

// return accountReportsWidget;

});
