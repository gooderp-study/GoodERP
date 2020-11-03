from odoo import models, fields, api
import math


class ReportVoucher(models.AbstractModel):
    _name = 'report.finance.report_voucher_view'
    _description = '会计凭证打印'

    def _rmb_upper(self, value):
        return self.env['res.currency'].rmb_upper(value)

    def _rmb_format(self, value):
        """
                        将数值按位数分开
        """
        if abs(value) < 0.01:
            # 值为0的不输出，即返回12个空格
            return ['' for i in range(12)]
        # 先将数字转为字符，去掉小数点，然后和12个空格拼成列表，取最后12个元素返回
        return (['' for i in range(12)] + list(('%0.2f' % value).replace('.', '')))[-12:]

    def _paginate(self, items, max_per_page=5):
        """
        分页函数
        items 为要分页的条目们
        max_per_page 设定每页条数
        返回：页数
        """
        count = len(items)
        return int(math.ceil(float(count) / max_per_page))
    
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['voucher'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'voucher',
            'data': data,
            'docs': docs,
            'rmb_upper': self._rmb_upper,
            'rmb_format': self._rmb_format,
            'paginate': self._paginate,
        }
    
