# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import random
from docxtpl import DocxTemplate
from odoo.tools import misc
# import ooxml
# from ooxml import parse, serialize, importer
import codecs
from datetime import datetime

# import pdfkit
_logger = logging.getLogger(__name__)
import pytz

from odoo import models
from odoo import fields
from odoo import api
import tempfile
import os


class DataModelProxy(object):
    '''使用一个代理类，来转发 model 的属性，用来消除掉属性值为 False 的情况
       且支持 selection 字段取到实际的显示值
    '''
    DEFAULT_TZ = 'Asia/Shanghai'

    def __init__(self, data):
        self.data = data

    def _compute_by_selection(self, field, temp):
        if field and field.type == 'selection':
            # _description_selection 会将标签翻译到对应语言
            selection = field._description_selection(self.data.env)

            try:
                return [value for _, value in selection if _ == temp][0]
            except KeyError:
                temp = ''

        return temp

    def _compute_by_datetime(self, field, temp):
        if field and field.type == 'datetime' and temp:
            tz = pytz.timezone(
                self.data.env.context.get('tz') or self.DEFAULT_TZ)
            temp_date = fields.Datetime.from_string(temp) + tz._utcoffset
            temp = fields.Datetime.to_string(temp_date)

        return temp

    def _compute_temp_false(self, field, temp):
        if not temp:
            if field and field.type in ('integer', 'float'):
                return 0
        if field.type == 'float' and int(temp) == temp:
            temp = int(temp)

        return temp or ''

    def __getattr__(self, key):
        if not self.data:
            return ""

        # 支持 dict 类型的报表数据源，并支持使用 "." 操作符获取属性值
        if isinstance(self.data, dict):
            value = self.data.get(key,'')
            if isinstance(value, (dict, models.Model, models.TransientModel)):
                value = DataModelProxy(value)
            return value

        temp = getattr(self.data, key)
        field = self.data._fields.get(key)
        if isinstance(temp, str) and ('&' in temp or '<' in temp or '>' in temp):
            temp = temp.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # 增加支持 models.TransientModel 数据源
        if isinstance(temp, (models.Model, models.TransientModel)):
            return DataModelProxy(temp)

        # 允许从 method 中获得数据
        if callable(temp):
            return temp()

        temp = self._compute_by_selection(field, temp)
        temp = self._compute_by_datetime(field, temp)

        return self._compute_temp_false(field, temp)

    def __getitem__(self, index):
        '''支持列表取值'''
        if isinstance(self.data, dict):
            return DataModelProxy(dict([list(self.data.items())[index]]))
        return DataModelProxy(self.data[index])

    def __iter__(self):
        '''支持迭代器行为'''
        return IterDataModelProxy(self.data)

    def __len__(self):
        '''支持返回长度'''
        if isinstance(self.data, dict):
            return len(self.data.items())
        return len(self.data)

    def __str__(self):
        '''支持直接在word 上写 many2one 字段'''
        name = ''
        if isinstance(self.data, dict):
            val = list(self.data.values())
            if len(val)>0:
                name = str(val[0])
            return name

        if self.data and self.data.display_name:
            name = self.data.display_name
            if '&' in self.data.display_name:
                name = name.replace('&', '&amp;')
            if '<' in self.data.display_name:
                name = name.replace('<', '&lt;')
            if '>' in self.data.display_name:
                name = name.replace('>', '&gt;')
        return name


class IterDataModelProxy(object):
    '''迭代器类，用 next 函数支持 for in 操作'''

    def __init__(self, data):
        self.data = data
        if isinstance(self.data, dict):
            self.length = len(list(data.items()))
        else: 
            self.length = len(data)
        self.current = 0

    def __next__(self):
        if self.current >= self.length:
            raise StopIteration()

        if isinstance(self.data, dict):
            temp = DataModelProxy(dict([list(self.data.items())[self.current]]))
        else:
            temp = DataModelProxy(self.data[self.current])
        self.current += 1

        return temp


class ReportDocx(models.TransientModel):

    _name = 'gooderp.report.docx'
    _description = 'docx report'

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        required=True
    )


    def generate_temp_file(self, tempname, suffix='docx'):
        return os.path.join(tempname, 'temp_%s_%s.%s' %
                            (os.getpid(), random.randint(1, 10000), suffix))

    def create_report(self, res_ids, data):
        # 如果提供了 res_ids（报表model的IDS）则优先使用此数据， 
        # data 提供额外的筛选条件，在 res_ids为空的情况下，使用
        # data 提供的筛选条件生成自定义数据，通过调用 model 的 
        # get_report_data 获得 dict 格式数据
        report_data = DataModelProxy(self.get_docx_data(self.ir_actions_report_id, res_ids, data))

        tempname = tempfile.mkdtemp()
        temp_out_file = self.generate_temp_file(tempname)

        doc = DocxTemplate(misc.file_open(self.ir_actions_report_id.template_file).name)
        # 2016-11-2 支持了图片
        # 1.导入依赖，python3语法
        from . import report_helper
        # 2. 需要添加一个"tpl"属性获得模版对象
        doc.render({'obj': report_data, 'tpl': doc}, report_helper.get_env())
        doc.save(temp_out_file)

        if self.ir_actions_report_id.output_type == 'pdf':
            temp_file = self.render_to_pdf(temp_out_file)
        else:
            temp_file = temp_out_file

        report_stream = ''
        with open(temp_file, 'rb') as input_stream:
            report_stream = input_stream.read()
        os.remove(temp_file)
        return report_stream, self.ir_actions_report_id.output_type

    def render_to_pdf(self, temp_file):
        tempname = tempfile.mkdtemp()
        temp_out_file_html = self.generate_temp_file(tempname, suffix='html')
        temp_out_file_pdf = self.generate_temp_file(tempname, suffix='pdf')
        '''
        ofile = ooxml.read_from_file(temp_file)
        html = """<html style="height: 100%">
            <head>
                <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
            </head>
            <body>
            """

        html += serialize.serialize(ofile.document).decode('utf-8')
        html += "</body></html>"

        with codecs.open(temp_out_file_html, 'w', 'utf-8') as f:
            f.write(html)

        pdfkit.from_file(temp_out_file_html, temp_out_file_pdf)

        os.remove(temp_out_file_html)
        '''
        return temp_out_file_pdf

    def get_docx_data(self, report, res_ids, data=None):
        # 打印时， 在消息处显示打印人
        # 2019.10.28 信莱德软件，并不是每个 
        # report.model 都继续自 mail.thread，
        # 所以这里不能强求 message_post 执行成功
        try:
            message = str((datetime.now()).strftime('%Y-%m-%d %H:%M:%S')) + ' ' + self.env.user.name + u' 打印了该单据'
            for record in self.env.get(report.model).browse(res_ids):
                record.message_post(body=message)
        except Exception as e:
            pass

        res = self.env.get(report.model).browse(res_ids)
        if len(res) ==0:
            data = data and dict(data) or {}
            report_func = data.get('report_function', 'get_report_data')
            func = getattr(self.env.get(report.model), report_func)
            if callable(func):
                res = func(data=data)
        return res

    def _save_file(self, folder_name, file):
        out_stream = open(folder_name, 'wb')
        try:
            out_stream.writelines(file)
        finally:
            out_stream.close()
