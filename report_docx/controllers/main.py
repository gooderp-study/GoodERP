# Copyright 2019 信莱德软件
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
from werkzeug import exceptions, url_decode

from odoo.http import route, request

from odoo.addons.web.controllers import main
from odoo.addons.web.controllers.main import (
    _serialize_exception,
    content_disposition
)
from odoo.tools import html_escape

import logging
_logger = logging.getLogger(__name__)


class ReportController(main.ReportController):
    TYPES_MAPPING = {
        'doc': 'application/vnd.ms-word',
        'html': 'text/html',
        'odt': 'application/vnd.oasis.opendocument.text',
        'pdf': 'application/pdf',
        'sxw': 'application/vnd.sun.xml.writer',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter != 'docx':
            return super(ReportController, self).report_routes(
                reportname=reportname, docids=docids, converter=converter,
                **data)
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the
            # one from the webclient *but* if the user explicitely wants to
            # change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])

        ir_action = request.env['ir.actions.report']
        action_docx_report = ir_action.get_from_report_name(
            reportname, "docx").with_context(context)
        if not action_docx_report:
            raise exceptions.HTTPException(
                description='Docx action report not found for report_name '
                            '%s' % reportname)
        res, filetype = action_docx_report.render(docids, data)
        filename = action_docx_report.gen_report_download_filename(
            docids, data)
        if not filename.endswith(filetype):
            filename = "{}.{}".format(filename, filetype)

        content_type = self.TYPES_MAPPING.get(
            filetype, 'octet-stream')

        http_headers = [('Content-Type', content_type),
                        ('Content-Length', len(res)),
                        ('Content-Disposition', content_disposition(filename))
                        ]
        return request.make_response(res, headers=http_headers)

    @route()
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger
        the download of a docx/controller report.

        :param data: a javascript array JSON.stringified containg report
        internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        if 'docx' not in report_type:
            return super(ReportController, self).report_download(data, token)
        try:
            reportname = url.split('/report/docx/')[1].split('?')[0]
            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                # Generic report:
                response = self.report_routes(
                    reportname, docids=docids, converter='docx')
            else:
                # Particular report:
                # decoding the args represented in JSON
                data = list(url_decode(url.split('?')[1]).items())
                response = self.report_routes(
                    reportname, converter='docx', **dict(data))
            response.set_cookie('fileToken', token)
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
