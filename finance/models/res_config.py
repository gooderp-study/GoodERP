# #############################################################################

# #############################################################################
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class FinanceConfigWizard(models.TransientModel):
    _name = 'finance.config.settings'
    _inherit = 'res.config.settings'
    _description = '会计默认设置'

    # 凭证
    # 凭证日期
    defaul_voucher_date = fields.Selection([('today', '当前日期'), ('last', '上一凭证日期')],
                                            string='新凭证的默认日期', default='today', help='选择新凭证的默认日期')
    # 凭证号重置设置  此部分参与了步科的设计
    defaul_auto_reset = fields.Boolean('是否重置凭证号', )
    defaul_reset_period = fields.Selection([('year', '每年'), ('month', '每月')], '重置间隔', required=True,
                                            default='month')
    defaul_reset_init_number = fields.Integer(
        '重置后起始数字', required=True, default=1, help="重置后，起始编号的数字，例从1起：1，2，3....")

    # 资产负债表 利润表
    # 是否能查看未结账期间
    defaul_period_domain = fields.Selection([('can', '能'), ('cannot', '不能')],
                                             string='是否能查看未结账期间', default='can', help='是否能查看未结账期间')
    company_id = fields.Many2one(
        'res.company',
        string='公司',
        change_default=True,
        default=lambda self: self.env.company)

    # 科目编码规则
    defaul_account_hierarchy_level = fields.Selection(
        string='科目层级级别',
        selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5')], default='5', required=True
    )
    defaul_top_length = fields.Selection(
        string='一级科目编码长度',
        selection=[('4', '4')],default='4'
    )
    defaul_child_step = fields.Selection(
        string='下级科目编码递增长度',
        selection=[('2', '2')],default='2'
    )

    @api.model
    def set_defaults(self):
        self.env['ir.default'].set( 'finance.config.settings', 'defaul_auto_reset', True)
        self.env['ir.default'].set('finance.config.settings', 'defaul_account_hierarchy_level', '5')
        self.env['ir.default'].set('finance.config.settings', 'defaul_top_length', '4')
        self.env['ir.default'].set('finance.config.settings', 'defaul_child_step', '2')
        self.env['ir.default'].set('finance.config.settings', 'defaul_voucher_date', 'today')
        self.env['ir.default'].set('finance.config.settings', 'defaul_reset_period', 'month')
        self.env['ir.default'].set('finance.config.settings', 'defaul_reset_init_number', 1)
        self.env['ir.default'].set('finance.config.settings', 'defaul_period_domain', 'can')

        return True

    def set_account_hierarchy_level(self):
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_account_hierarchy_level', self.defaul_account_hierarchy_level)
        return res

    def set_top_length(self):
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_top_length', self.defaul_top_length)
        return res

    def set_child_step(self):
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_child_step', self.defaul_child_step)
        return res

    def set_voucher_date(self):
        voucher_date = self.defaul_voucher_date
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_voucher_date', voucher_date)
        return res

    def set_period_domain(self):
        period_domain = self.defaul_period_domain
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_period_domain', period_domain)
        return res

    def set_auto_reset(self):
        auto_reset = self.defaul_auto_reset
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_auto_reset', auto_reset)
        return res

    def set_reset_period(self):
        reset_period = self.defaul_reset_period
        res = self.env['ir.default'].set(
            'finance.config.settings', 'defaul_reset_period', reset_period)
        return res

    def set_reset_init_number(self):
        reset_init_number = self.defaul_reset_init_number
        res = self.env['ir.default'].set('finance.config.settings', 'defaul_reset_init_number',
                                                reset_init_number)
        return res
