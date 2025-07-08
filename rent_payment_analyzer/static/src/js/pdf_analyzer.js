odoo.define('rent_payment_analyzer.PDFAnalyzer', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');

    var _t = core._t;

    var PDFAnalyzer = Widget.extend({
        template: 'PDFAnalyzer',
        
        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.invoice_id = options.invoice_id;
        },
        
        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self.analyzePDF();
            });
        },
        
        analyzePDF: function() {
            var self = this;
            
            var dialog = new Dialog(this, {
                title: _t("Analyzing PDF"),
                size: 'medium',
                $content: $('<div>').text(_t("Processing PDF attachment...")),
                buttons: [
                    {text: _t("Close"), close: true}
                ]
            }).open();
            
            ajax.jsonRpc('/rent_payment_analyzer/analyze', 'call', {
                'invoice_id': self.invoice_id,
            }).then(function(result) {
                dialog.close();
                
                if (result.success) {
                    var message = _t("Analysis complete: ") + result.count + _t(" payments found");
                    self.showResult(_t("Success"), message, 'success');
                } else {
                    self.showResult(_t("Error"), result.error || _t("Error analyzing PDF"), 'danger');
                }
            }).fail(function() {
                dialog.close();
                self.showResult(_t("Error"), _t("Server error"), 'danger');
            });
        },
        
        showResult: function(title, message, type) {
            new Dialog(this, {
                title: title,
                size: 'medium',
                $content: $('<div>')
                    .addClass('alert alert-' + type)
                    .text(message),
                buttons: [
                    {text: _t("Close"), close: true}
                ]
            }).open();
        }
    });

    return {
        PDFAnalyzer: PDFAnalyzer,
        showAnalysis: function(invoice_id) {
            var analyzer = new PDFAnalyzer(null, {invoice_id: invoice_id});
            analyzer.appendTo($('<div>'));
        }
    };
});