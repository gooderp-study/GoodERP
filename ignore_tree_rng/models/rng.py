import odoo.tools.view_validation

old_relaxng = odoo.tools.view_validation.relaxng

def new_relaxng(view_type):
    '''对于 tree view 不进行 RNG 检查，其它类型的 view 仍按原来方式处理'''
    if view_type == 'tree':
        return None
    else:
        return old_relaxng(view_type)

odoo.tools.view_validation.relaxng = new_relaxng
