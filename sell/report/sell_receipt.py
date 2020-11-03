

from odoo import fields, models, api


class SellReceipt(models.TransientModel):
    _name = 'sell.receipt'
    _description = '销售收款一览表'

    c_category_id = fields.Many2one('core.category', '客户类别')
    partner_id = fields.Many2one('partner', '客户')
    user_id = fields.Many2one('res.users', '销售员')
    type = fields.Char('业务类别')
    date = fields.Date('单据日期')
    warehouse_id = fields.Many2one('warehouse', '仓库')
    order_name = fields.Char('单据编号')
    sell_amount = fields.Float('销售金额', digits='Amount')
    discount_amount = fields.Float('优惠金额',
                                   digits='Amount')
    amount = fields.Float('成交金额', digits='Amount')
    partner_cost = fields.Float('客户承担费用', digits='Amount')
    receipt = fields.Float('已收款', digits='Amount')
    balance = fields.Float('应收款余额', digits='Amount')
    receipt_rate = fields.Float('回款率(%)')
    note = fields.Char('备注')

    def view_detail(self):
        '''销售收款一览表查看明细按钮'''
        self.ensure_one()
        order = self.env['sell.delivery'].search(
            [('name', '=', self.order_name)])
        if order:
            if not order.is_return:
                view = self.env.ref('sell.sell_delivery_form')
            else:
                view = self.env.ref('sell.sell_return_form')

            return {
                'name': '销售发货单',
    
                'view_mode': 'form',
                'view_id': False,
                'views': [(view.id, 'form')],
                'res_model': 'sell.delivery',
                'type': 'ir.actions.act_window',
                'res_id': order.id,
            }

    def generate_reconcile_order(self):
        """新建核销单，应收冲预收，客户为所选行客户"""
        self.ensure_one()
        view = self.env.ref('money.reconcile_order_form')
        # 如果已存在该客户核销单，则查看核销单，否则创建
        order = self.env['reconcile.order'].search([
            ('partner_id', '=', self.partner_id.id),
            ('business_type', '=', 'adv_pay_to_get')])
        if order:
            return {
                'name': '核销单',
                'view_mode': 'form',
                'views': [(view.id, 'form')],
                'res_model': 'reconcile.order',
                'type': 'ir.actions.act_window',
                'res_id': order.id,
            }

        order = self.env['reconcile.order'].create({
            'partner_id': self.partner_id.id,
            'business_type': 'adv_pay_to_get',
        })
        order.onchange_partner_id()
        return {
            'name': '核销单',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'reconcile.order',
            'type': 'ir.actions.act_window',
            'res_id': order.id,
        }
