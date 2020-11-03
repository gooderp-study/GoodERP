/* Copyright 2019 信莱德软件 <www.zhsunlight.cn>
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define('report_docx.report', function (require) {

var ActionManager = require('web.ActionManager');

ActionManager.include({
    _executeReportAction: function (action, options) {
        // docx reports
        if ('report_type' in action && action.report_type === 'docx' ) {
            return this._triggerDownload(action, options, 'docx');
        } else {
            return this._super.apply(this, arguments);
        }
    },

    _makeReportUrls: function(action) {
        var reportUrls = this._super.apply(this, arguments);
        reportUrls.docx = '/report/docx/' + action.report_name;
        // We may have to build a query string with `action.data`. It's the place
        // were report's using a wizard to customize the output traditionally put
        // their options.
        if (_.isUndefined(action.data) || _.isNull(action.data) ||
            (_.isObject(action.data) && _.isEmpty(action.data))) {
            if (action.context.active_ids) {
                var activeIDsPath = '/' + action.context.active_ids.join(',');
                reportUrls.docx += activeIDsPath;;
            }
        } else {
            var serializedOptionsPath = '?options=' + encodeURIComponent(JSON.stringify(action.data));
            serializedOptionsPath += '&context=' + encodeURIComponent(JSON.stringify(action.context));
            reportUrls.docx += serializedOptionsPath;
        }
        return reportUrls;
    }
});

});
