

from odoo import fields, models, api


class BuyPayment(models.TransientModel):
    _name = 'buy.payment'
    _description = '采购付款一览表'

    s_category_id = fields.Many2one('core.category', '供应商类别')
    partner_id = fields.Many2one('partner', '供应商')
    type = fields.Char('业务类别')
    date = fields.Date('单据日期')
    warehouse_dest_id = fields.Many2one('warehouse', '仓库')
    order_name = fields.Char('单据编号')
    purchase_amount = fields.Float('采购金额', digits='Amount')
    discount_amount = fields.Float('优惠金额', digits='Amount')
    amount = fields.Float('成交金额', digits='Amount')
    payment = fields.Float('已付款', digitse='Amount')
    balance = fields.Float('应付款余额', digits='Amount')
    payment_rate = fields.Float('付款率(%)')
    note = fields.Char('备注')

    def view_detail(self):
        '''查看明细按钮'''
        self.ensure_one()
        order = self.env['buy.receipt'].search(
            [('name', '=', self.order_name)])
        if order:
            if not order.is_return:
                view = self.env.ref('buy.buy_receipt_form')
            else:
                view = self.env.ref('buy.buy_return_form')

            return {
                'name': '采购入库单',
                '': 'form',
                'view_mode': 'form',
                'view_id': False,
                'views': [(view.id, 'form')],
                'res_model': 'buy.receipt',
                'type': 'ir.actions.act_window',
                'res_id': order.id,
            }
