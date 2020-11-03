
from odoo import http
from odoo.http import request
from json import dumps
from datetime import datetime


class ActionStatistics(http.Controller):

    @http.route('/get_user_info', auth='public')
    def get_user_info(self):
        user = request.env.user

        return dumps({
            'user': user.name,
            'login': user.login,
            'company': user.company_id.name,
            'company_phone': user.company_id.phone,
            'company_start_date': datetime.strftime(user.company_id.start_date,"%Y-%m-%d"),
            'company_street': user.company_id.street
        })
