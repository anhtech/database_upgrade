odoo.define('customer_in_pos_ticket.customer_info',function(require) {
    "use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var QWeb = core.qweb;
var _t  = require('web.core')._t;


var _super = models.Order;
models.Order = models.Order.extend({
    export_for_printing: function(){
        var receipt = _super.prototype.export_for_printing.apply(this,arguments);
        var client  = this.get('client');
        receipt.client_phone = client ? client.phone : null;
        receipt.client_address = null;
        if (client) {
            var address = "";
            if (client.country_id) {
                address = client.country_id[1];
            }
            if (client.city) {
                if (address != "") {
                    address = address + ", ";
                }
                address = address + client.city;
            }
            if (client.zip) {
                if (address != "") {
                    address = address + ", ";
                }
                address = address + "B: "+client.zip;
            }
            if (client.street) {
                if (address != "") {
                    address = address + ", ";
                }
                address = address + "R: "+client.street;
            }
            if (client.street2) {
                if (address != "") {
                    address = address + ", ";
                }
                address = address + "H: "+client.street2;
            }
            receipt.client_address = address;
        }
        return receipt;
    },
});


});