
from odoo import fields, models, api, tools
from .supplier_statements import create_source_docx_partner



class CustomerStatementsReport(models.Model):
    _name = "customer.statements.report"
    _description = u"客户对账单"
    _auto = False
    _order = 'id, date'

    @api.depends('amount', 'pay_amount', 'partner_id')
    def _compute_balance_amount(self):
        # 相邻的两条记录，partner不同，应收款余额重新计算
        for cba in self:
            pre_record = cba.search(
                [('id', '<=', cba.id), ('partner_id', '=', cba.partner_id.id)])
            for pre in pre_record:
                cba.balance_amount += pre.amount - pre.pay_amount - pre.discount_money

    partner_id = fields.Many2one('partner', string=u'业务伙伴', readonly=True)
    name = fields.Char(string=u'单据编号', readonly=True)
    date = fields.Date(string=u'单据日期', readonly=True)
    done_date = fields.Datetime(string=u'完成日期', readonly=True)
    amount = fields.Float(string=u'应收金额', readonly=True,
                          digits='Amount')
    pay_amount = fields.Float(string=u'实际收款金额', readonly=True,
                              digits='Amount')
    balance_amount = fields.Float(string=u'应收款余额',
                                  compute='_compute_balance_amount',
                                  digits='Amount')
    discount_money = fields.Float(string=u'收款折扣', readonly=True,
                                  digits='Amount')
    note = fields.Char(string=u'备注', readonly=True)

    def init(self):
        # union money_order(type = 'get'), money_invoice(type = 'income')
        cr = self._cr
        tools.drop_view_if_exists(cr, 'customer_statements_report')
        cr.execute("""
            CREATE or REPLACE VIEW customer_statements_report AS (
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
                        m.discount_amount as discount_money,
                        0 AS balance_amount,
                        m.note
                FROM money_order AS m
                WHERE m.type = 'get' AND m.state = 'done'
                UNION ALL
                SELECT  mi.partner_id,
                        mi.name,
                        mi.date,
                        mi.create_date AS done_date,
                        mi.amount,
                        0 AS pay_amount,
                        0 as discount_money,
                        0 AS balance_amount,
                        mi.note AS note
                FROM money_invoice AS mi
                LEFT JOIN core_category AS c ON mi.category_id = c.id
                WHERE c.type = 'income' AND mi.state = 'done'
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
