
from odoo import fields, models, api, tools

class SupplierStatementsReport(models.Model):
    _name = "supplier.statements.report"
    _description = u"供应商对账单"
    _auto = False
    _order = 'id, date'

    @api.depends('amount', 'pay_amount', 'partner_id')
    def _compute_balance_amount(self):
        # 相邻的两条记录，partner不同，应付款余额要清零并重新计算
        for ssp in self:
            pre_record = ssp.search(
                [('id', '<=', ssp.id), ('partner_id', '=', ssp.partner_id.id)])
            for pre in pre_record:
                ssp.balance_amount += pre.amount - pre.pay_amount + pre.discount_money

    partner_id = fields.Many2one('partner', string=u'业务伙伴', readonly=True)
    name = fields.Char(string=u'单据编号', readonly=True)
    date = fields.Date(string=u'单据日期', readonly=True)
    done_date = fields.Datetime(string=u'完成日期', readonly=True)
    amount = fields.Float(string=u'应付金额', readonly=True,
                          digits='Amount')
    pay_amount = fields.Float(string=u'实际付款金额', readonly=True,
                              digits='Amount')
    discount_money = fields.Float(string=u'付款折扣', readonly=True,
                                  digits='Amount')
    balance_amount = fields.Float(
        string=u'应付款余额',
        compute='_compute_balance_amount',
        readonly=True,
        digits='Amount')
    note = fields.Char(string=u'备注', readonly=True)

    def init(self):
        # union money_order(type = 'pay'), money_invoice(type = 'expense')
        cr = self._cr
        tools.drop_view_if_exists(cr, 'supplier_statements_report')
        cr.execute("""
            CREATE or REPLACE VIEW supplier_statements_report AS (
            SELECT  ROW_NUMBER() OVER(ORDER BY partner_id, date, amount desc) AS id,
                    partner_id,
                    name,
                    date,
                    done_date,
                    amount,
                    pay_amount,
                    discount_money,
                    balance_amount,
                    note
            FROM
                (
                SELECT m.partner_id,
                        m.name,
                        m.date,
                        m.write_date AS done_date,
                        0 AS amount,
                        m.amount AS pay_amount,
                        m.discount_amount AS discount_money,
                        0 AS balance_amount,
                        m.note
                FROM money_order AS m
                WHERE m.type = 'pay' AND m.state = 'done'
                UNION ALL
                SELECT  mi.partner_id,
                        mi.name,
                        mi.date,
                        mi.create_date AS done_date,
                        mi.amount,
                        0 AS pay_amount,
                        0 AS discount_money,
                        0 AS balance_amount,
                        Null AS note
                FROM money_invoice AS mi
                LEFT JOIN core_category AS c ON mi.category_id = c.id
                WHERE c.type = 'expense' AND mi.state = 'done'
                ) AS ps)
        """)

    @api.model
    def get_report_data(self, data=None):
        '''生成报表源数据
        
        '''
        records = self.search([('partner_id', '=', data.get('partner_id')),
                                ('date', '>=', data.get('from_date')),
                                ('date', '<=', data.get('to_date'))])
        if records:
            return create_source_docx_partner(self, records, 0, data)
        else:
            pre_records = self.search(
                [('partner_id', '=', data.get('partner_id')),
                 ('date', '<', data.get('from_date'))], order='id desc')
            if pre_records:
                init_pay = pre_records[0].balance_amount
                return create_source_docx_partner(self, None, init_pay, data)
            else:
                return create_source_docx_partner(self, None, 0, data)


# 与客户对账单共用的函数
def create_source_docx_partner(obj, records, init_pay, data=None):
    partner = obj.env.get('partner').search([('id', '=', data.get('partner_id'))])
    simple_dict = {'partner_name': partner.name,
                   'from_date': data.get('from_date'),
                   'to_date': data.get('to_date'),
                   'report_line': [],
                   'init_pay': {},
                   'final_pay': {}}
    if not records:
        if init_pay:
            simple_dict['init_pay'] = init_pay
            simple_dict['final_pay'] = init_pay
        return simple_dict

    data = records
    for p_value in data:
        simple_dict['report_line'].append({
            'date': p_value.date,
            'name': p_value.name,
            'note': p_value.note,
            'amount': p_value.amount,
            'pay_amount': p_value.pay_amount,
            'discount_money': p_value.discount_money,
            'balance_amount': p_value.balance_amount
        })

    if data:
        simple_dict['init_pay'] = data[0].balance_amount - data[0].amount + data[0].pay_amount - data[
            0].discount_money
        simple_dict['final_pay'] = data[-1].balance_amount

    return simple_dict

