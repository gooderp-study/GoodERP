

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

AVAILABLE_PRIORITIES = [
    ('0', 'E'),
    ('1', 'D'),
    ('2', 'C'),
    ('3', 'B'),
    ('4', 'A'),
]

class Partner(models.Model):
    '''
    业务伙伴可能是客户： c_category_id 非空

    '''
    _name = 'partner'
    _description = '业务伙伴'
    _inherit = ['mail.thread']

    code = fields.Char('编号')
    name = fields.Char('名称', required=True,)
    main_mobile = fields.Char('主要联系方式', required=True,)
    main_address = fields.Char('注册地址 电话')
    priority = fields.Selection(AVAILABLE_PRIORITIES, '客户重要性', default='0')
    supp_priority = fields.Selection(AVAILABLE_PRIORITIES, '供应商重要性', default='0')
    c_category_id = fields.Many2one('core.category', '客户类别',
                                    ondelete='restrict',
                                    domain=[('type', '=', 'customer')],
                                    context={'type': 'customer'})
    s_category_id = fields.Many2one('core.category', '供应商类别',
                                    ondelete='restrict',
                                    domain=[('type', '=', 'supplier')],
                                    context={'type': 'supplier'})
    receivable = fields.Float('应收余额', readonly=True,
                              digits='Amount')
    payable = fields.Float('应付余额', readonly=True,
                           digits='Amount')
    tax_num = fields.Char('税务登记号')
    tax_rate = fields.Float('税率(%)',
                            help='业务伙伴税率')
    bank_name = fields.Char('开户行')
    bank_num = fields.Char('银行账号')

    credit_limit = fields.Float('信用额度', track_visibility='onchange',
                                help='客户购买商品时，本次发货金额+客户应收余额要小于客户信用额度')
    credit_time = fields.Float('信用天数', track_visibility='onchange',
                                help='客户购买商品时，本次结算单的到期日为结算单日期+信用天数')
    recon_day = fields.Integer("对账日")
    active = fields.Boolean('启用', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)
    tag_ids = fields.Many2many('core.value',
                               ondelete='restrict',
                               string='标签',
                               domain=[('type', '=', 'partner_tag')],
                               context={'type': 'partner_tag'})
    channel_id = fields.Many2one('core.category', '渠道',
                                ondelete='restrict',
                                domain=[('type', '=', 'channel')],
                                context={'type': 'channel'})
    source = fields.Char('来源')
    note = fields.Text('备注')
    main_contact = fields.Char('主联系人')
    responsible_id = fields.Many2one('res.users',
                                     '负责人员')
    share_id = fields.Many2one('res.users',
                               '共享人员')
    pay_method = fields.Many2one('pay.method',
                                 string='付款方式',
                                 ondelete='restrict')
    date_qualify = fields.Date('资质到期日期')
    days_qualify = fields.Float('资质到期天数',
                                compute='compute_days_qualify',
                                store=True,
                                help='当天到资质到期日期的天数差',
                                )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', '业务伙伴不能重名')
    ]

    @api.constrains('name', 'c_category_id', 's_category_id')
    def _check_category_exists(self):
        # 客户 或 供应商 类别有一个必输
        if self.name and  not self.s_category_id and not self.c_category_id:
            raise UserError('请选择类别')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        在many2one字段中支持按编号搜索
        """
        args = args or []
        if name:
            res_id = self.search([('code','=',name)])
            if res_id:
                return res_id.name_get()
            args.append(('code', 'ilike', name))
            partners = self.search(args)
            if partners:
                return partners.name_get()
            else:
                args.remove(('code', 'ilike', name))
        return super(Partner, self).name_search(name=name,
                                                args=args,
                                                operator=operator,
                                                limit=limit)

    def write(self, vals):
        # 业务伙伴应收/应付余额不为0时，不允许取消对应的客户/供应商身份
        if self.c_category_id and vals.get('c_category_id') == False and self.receivable != 0:
            raise UserError('该客户应收余额不为0，不能取消客户类型')
        if self.s_category_id and vals.get('s_category_id') == False and self.payable != 0:
            raise UserError('该供应商应付余额不为0，不能取消供应商类型')
        return super(Partner, self).write(vals)

    @api.depends('date_qualify')
    def compute_days_qualify(self):
        for partner in self:
            """计算当天距离资质到期日期的天数"""
            day = 0
            if partner.date_qualify:
                day = (partner.date_qualify - fields.Date.context_today(self)).days
            partner.days_qualify = day
