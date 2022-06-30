odoo.define('pos_ushk_website.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var PosDB = require('point_of_sale.DB');
	var rpc = require('web.rpc');
	var PaymentScreenWidget = screens.PaymentScreenWidget;
	var _t = core._t;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var self = this;
            _super_order.initialize.apply(this,arguments);
            this.ushk_ref = false;
            this.save_to_db();
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.ushk_ref = this.ushk_ref ? this.ushk_ref : false;
            return json;
        },
    });

    PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            var self = this;
            var ushkwebsite_ref = self.$('.ushkwebsite-ref-input').val();
            console.log(ushkwebsite_ref);
            if (true == false)
                this._super(force_validation);
        }
    });


});
