odoo.define('core.gooderp', function (require) {
    "use strict";

    /* 标题换成 GoodERP */
    var WebClient = require('web.WebClient');
    var UserMenu = require('web.UserMenu');

    WebClient.include({
        init: function() {
            this._super.apply(this, arguments);
            this.set('title_part', {"zopenerp": document.title});
        }
    });

    UserMenu.include({
        _onMenuDocumentation: function () {
            window.open('http://osbzr.com/GoodERPJeff/gooderp_user_manual/src/branch/master/SUMMARY.md', '_blank');
        },
        _onMenuSupport: function () {
            window.open('http://osbzr.com/GoodERPJeff/gooderp/wiki', '_blank');
        },
    });

});