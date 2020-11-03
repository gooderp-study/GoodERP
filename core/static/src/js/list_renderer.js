odoo.define('core.multi_row_header', function (require) {
"use strict";

var ListRenderer = require('web.ListRenderer');


ListRenderer.include({

    _renderBody: function () {
        var self = this;
        var $rows = this._renderRows();
        return $('<tbody>').append($rows);
    },

    _renderHeader: function () {
        var $header = this._super.apply(this, arguments);

        if ($header.find('[data-merge]').length>0){

            $header.find('th.o_list_record_selector')
            .eq(0)
            .attr('rowspan','2')
            .css({'vertical-align': 'middle'});
            
            _.each($header.find('[data-normal]'), function (el) {
                $(el).attr('rowspan','2');
            });
            
            var $tr = $('<tr>');
            _.each($header.find('[data-merge]'), function (el) {
                var $el = $(el);
                var $th = $('<th>').text($el.data('child-name'));

                if($el.data('name')){
                    $th.attr('data-name', $el.data('name'));
                    $el.removeAttr('data-name');
                }
                if($el.data('original-title')){
                    $th.attr('data-original-title', $el.data('original-title'));
                    $el.removeAttr('data-original-title');
                }
                if($el.attr('aria-sort')){
                    $th.attr('aria-sort', $el.attr('aria-sort'));
                    $el.removeAttr('aria-sort');
                }
                if($el.attr('title')){
                    $th.attr('title', $el.attr('title'));
                    $el.removeAttr('title');
                }
                if($el.attr('class')){
                    $th.attr('class', $el.attr('class'));
                    $el.removeAttr('class');
                }

                $tr.append($th);

                if($el.data('merge')==='True'){
                    $el.remove();
                }
            });
            $header.append($tr);
        }

        return $header;
    },


    _renderHeaderCell: function (node) {
        var $th = this._super.apply(this, arguments);

        if (node.attrs.base_string){
            $th.attr('colspan', node.attrs.colspan);
            $th.text(node.attrs.base_string);
        }

        if (node.attrs.child_name){
            $th.attr('data-child-name', node.attrs.child_name);
            $th.attr('data-merge', node.attrs.merge);
            $th.css({'text-align': 'center','border-bottom':'none'});
        }else{
            $th.attr('data-normal', 'true');
            $th.css({'vertical-align': 'middle'});
        }

        return $th;
    }
});

});
