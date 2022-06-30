odoo.define('pos_total_amount_discount.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var PosDB = require('point_of_sale.DB');
	var rpc = require('web.rpc');
	var _t = core._t;

    function get_discount_product(products) {
        for (var i in products){
            if(products[i]['display_name'] == 'Discount Amount')
                return products[i]['id'];
        }
        return false;
    }

    var DiscountScreenWidget = screens.ScreenWidget.extend({
        template: 'DiscountScreenWidget',

        init: function(parent, options) {
            this.discount_product = null;
            this._super(parent, options);
        },
        show: function() {
            var self = this;
            this._super();
            if(!this.discount_product)
                this.discount_product = get_discount_product(this.pos.db.product_by_id);
            self.$(".error-message").hide();
            this.$('.confirm').on('click',function() {
                var inputValue = self.$('.popup-input').val();
                if (inputValue.length!=0) {
                    if (!isNaN(inputValue)) {
                        var inputValueFloat = (+inputValue).toFixed(3);
                        if (inputValueFloat>0) {
                            var order = self.pos.get_order();
                            var product = self.pos.db.get_product_by_id(self.discount_product);
                            self.$(".popup-input").removeClass("az-error");
                            self.$(".empty-value").hide();
                            self.$(".wrong-value").hide();
                            self.$(".negative-value").hide();
                            var order = self.pos.get_order();
                            var orderlines = order.get_orderlines();
                            var alreadyThere = false;
                            orderlines.forEach(function (line) {
                                if (line.product.id == self.discount_product) {
                                    line.set_quantity(1);
                                    line.set_unit_price(inputValueFloat*-1.0);
                                    alreadyThere = true;
                                }
                            });
                            if (!alreadyThere) {
                                order.add_product(product, {quantity: 1, price: inputValueFloat*-1.0});
                            }
                            self.$('.popup-input').val("0");
                            self.gui.close_popup();
                        } else {
                            self.$(".empty-value").hide();
                            self.$(".wrong-value").hide();
                            self.$(".popup-input").removeClass("az-error");
                            self.$(".negative-value").show();
                            self.$(".popup-input").addClass("az-error");
                        }
                    } else {
                        self.$(".empty-value").hide();
                        self.$(".negative-value").hide();
                        self.$(".popup-input").removeClass("az-error");
                        self.$(".wrong-value").show();
                        self.$(".popup-input").addClass("az-error");
                    }
                } else {
                    self.$(".wrong-value").hide();
                    self.$(".negative-value").hide();
                    self.$(".popup-input").removeClass("az-error");
                    self.$(".empty-value").show();
                    self.$(".popup-input").addClass("az-error");
                }
            });
            this.$('.cancel').on('click',function() {
                self.$(".popup-input").removeClass("az-error");
                self.$(".empty-value").hide();
                self.$(".wrong-value").hide();
                self.$(".negative-value").hide();
                self.gui.close_popup();
            });
        },
    });
    gui.define_popup({name:'DiscountScreenWidget', widget: DiscountScreenWidget});

    screens.ProductScreenWidget.include({
        show: function(){
            var self = this;
            this._super();
            $('#discount_amount').on('click',function(){
                self.gui.show_popup('DiscountScreenWidget');

//                self.gui.show_popup('error',{
//                    'title': _t('Unable to apply Coupon !'),
//                    'body': _t('This coupon is not applicable on the products or category you have selected !'),
//                });
            });
        },
    });

//    models.load_models({
//        model: 'product.multi.barcode',
//        fields: ['barcode','product_id','product_tmpl_id'],
//        loaded: function(self,barcodes){
//            self.multi_barcodes = barcodes;
//        }
//    });
//
//	var _super_posmodel = models.PosModel.prototype;
//	models.PosModel = models.PosModel.extend({
//		initialize: function (session, attributes) {
//			var product_model = _.find(this.models, function(model){ return model.model === 'product.product'; });
//			return _super_posmodel.initialize.call(this, session, attributes);
//		},
//		scan_product: function(parsed_code) {
//			var selectedOrder = this.get_order();
//			var self = this;
//			var product = this.db.get_product_by_barcode(parsed_code.base_code);
//			var multi_barcodes_var = this.multi_barcodes;
//			for (var i = 0; i < multi_barcodes_var.length; i++) {
//			    if (multi_barcodes_var[i]['barcode'] == parsed_code.base_code) {
//			        if (multi_barcodes_var[i]['product_tmpl_id']) {
//			            product = this.db.get_product_by_id(multi_barcodes_var[i]['product_tmpl_id'][0])
//			        } else if (multi_barcodes_var[i]['product_id']) {
//			            product = this.db.get_product_by_id(multi_barcodes_var[i]['product_id'][0])
//			        }
//			    }
//			}
//            if (!product) {
//                return false;
//            }
//            if(parsed_code.type === 'price'){
//                selectedOrder.add_product(product, {price:parsed_code.value});
//            }else if(parsed_code.type === 'weight'){
//                selectedOrder.add_product(product, {quantity:parsed_code.value, merge:false});
//            }else if(parsed_code.type === 'discount'){
//                selectedOrder.add_product(product, {discount:parsed_code.value, merge:false});
//            }else{
//                selectedOrder.add_product(product);
//            }
//            return true;
//		},
//	});

//	screens.ActionpadWidget.include({
//        renderElement: function() {
//            var self = this;
//            this._super();
//            this.$('.pay').unbind();
//            this.$('.set-customer').unbind();
//            this.$('.cash-customer').click(function(){
//                var config = self.pos.config;
//                var partner = self.pos.db.get_partner_by_id(config['cash_customer'][0]);
//                var order = self.pos.get_order();
//                order.set_client(partner);
//            });
//            this.$('.pay').click(function(){
//                var client = self.pos.get_client();
//                if (client) {
//                    var order = self.pos.get_order();
//                    var has_valid_product_lot = _.every(order.orderlines.models, function(line){
//                        return line.has_valid_product_lot();
//                    });
//                    if(!has_valid_product_lot){
//                        self.gui.show_popup('error',{
//                            'title': _t('Empty Serial/Lot Number'),
//                            'body':  _t('One or more product(s) required serial/lot number.'),
////                            confirm: function(){
////                                order.set_to_invoice(true);
////                                self.gui.show_screen('payment');
////                            },
//                        });
//                    }else{
//                        order.set_to_invoice(true);
//                        self.gui.show_screen('payment');
//                    }
//                } else {
//                        self.gui.show_popup('error',{
//                            'title': _t('No Customer Found'),
//                            'body':  _t('You need to select a customer before making a payment !'),
//                        });
//                }
//            });
//            this.$('.set-customer').click(function(){
//                self.gui.show_screen('clientlist');
//            });
//        }
//	});
    return DiscountScreenWidget;
});
