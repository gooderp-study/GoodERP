
{
    'name': '忽略对 Tree View 的RNG检查',
    'version': '13.00',
    'summary': '''
            
    ''',
    'category': 'Hidden',
    'author': '信莱德软件',
    'website': 'https://zhsunlight.cn',
    'depends': ['base'],
    'description':
    '''
忽略对 Tree View 的RNG检查
===========================================
* 由于多行表头要用到一些自定义字段属性，
* 而从odoo13开始，对XML属性会使用严格的RNG检查，
* 本模块让系统略过对tree类型的XML属性使用RNG检查，
* 以便可以在 tree 类型的视图中添加各种属性，
    ''',
    'data': [
    ],
    'installable': True,
}
