# © 2016 Elico Corp (www.elico-corp.com).
# © 2019 信莱德软件 (www.zhsunlight.cn).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval
import time


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report'

    report_type = fields.Selection(selection_add=[('docx', 'Docx')])
    template_file = fields.Char('Template File')
    output_type = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('docx', 'Docx'),
        ],
        'Output Type', required=True, default='docx'
    )

    @api.model
    def get_from_report_name(self, report_name, report_type):
        return self.search(
            [("report_name", "=", report_name),
             ("report_type", "=", report_type)])

    def render_docx(self, res_ids, data):
        self.ensure_one()
        if self.report_type != "docx":
            raise RuntimeError(
                "docx rendition is only available on docx report.\n"
                "(current: '{}', expected 'docx'".format(self.report_type))

        docx = self.env['gooderp.report.docx'].create({
            'ir_actions_report_id': self.id
        })

        return docx.create_report(res_ids, data)

    def gen_report_download_filename(self, res_ids, data):
        """Override this function to change the name of the downloaded report
        """
        self.ensure_one()
        report = self.get_from_report_name(self.report_name, self.report_type)
        if report.print_report_name and not len(res_ids) > 1:
            obj = self.env[self.model].browse(res_ids)
            return safe_eval(report.print_report_name,
                             {'object': obj, 'time': time})
        return "%s.%s" % (self.name, self.output_type)
