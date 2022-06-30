odoo.define('customer_address_format.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var PosDB = require('point_of_sale.DB');
	var _t = core._t;

    models.load_fields("res.partner", "street2");

});
