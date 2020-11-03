# © 2016 Elico Corp (www.elico-corp.com).
# © 2019 信莱德软件 (www.zhsunlight.cn).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Docx",
    "version": '13.0.1',
    "category": "Report",
    "website": "www.elico-corp.com",
    "author": "Elico Corp, Odoo Community Association (OCA), "
            "信莱德软件",
    'description':
    '''
word模板报表引擎
===========================================================
* 扩展报表数据源，增加支持dict、models.TransientModel作为数据源
* dict 格式数据源同样支持"."操作，与models 获取属性的方式保持一致
* 该模块为 odoo 增加一个新的报表生成引擎
* 使用 word 编写报表
* 使用 jinja2 语法，语法参考： http://docs.jinkan.org/docs/jinja2/templates.html
    ''',
    "depends": [
        "base","web"
    ],
    'external_dependencies': {
        'python': [
            'docxtpl',
#            'python-ooxml',
#            'pdfkit',
        ],
    },
    "data": [
        'views/ir_actions.xml',
        'views/template.xml',
    ],
    'demo': [
        'demo/report.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False
}
