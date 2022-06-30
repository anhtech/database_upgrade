odoo.define('pos_salesperson_coupons.pos', function(require) {
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

    models.load_models({
        model: 'pos.coupon.salesperson',
        fields: ['ref','salesperson_id','remaining_to_use','valid_til','is_discount_products'
                ,'is_discount_on_all_products','discount_all_products_per','product_lines','is_discount_value','discount_value','salesperson_commission'],
        domain: function(self){ return [['remaining_to_use','>',0]]; },
        loaded: function(self,coupons){
            self.coupons = coupons;
        },
    });

    models.load_models({
        model: 'coupon.product.line',
        fields: ['coupon_id','product_id','discount_per'],
        loaded: function(self,coupon_lines){
            self.coupon_lines = coupon_lines;
        },
    });

    models.load_models({
        model: 'sales.person',
        fields: ['name'],
        loaded: function(self,salespersons){
            self.salespersons = salespersons;
        },
    });

    function get_discount_product(products) {
        for (var i in products){
            if(products[i]['display_name'] == 'Coupon Discount')
                return products[i]['id'];
        }
        return false;
    }

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var self = this;
            _super_order.initialize.apply(this,arguments);
            this.is_coupon_applied = false;
            this.coupon = false;
            this.save_to_db();
        },
        get_coupon_productlines: function(productlines_ids) {
            var result = [];
            var coupon_lines = this.pos.coupon_lines;
            for (var i in coupon_lines){
                for (var j in productlines_ids){
                    if (productlines_ids[j] == coupon_lines[i].id) {
                        result.push(coupon_lines[i]);
                    }
                }
                if (result.length == productlines_ids.length)
                    break;
            }
            return result;
        },
        get_salesperson_by_id: function(id) {
            var salespersons = this.pos.salespersons;
            var results = [];
            for(var i = 0; i < salespersons.length; i++){
                if (salespersons[i].id == id) {
                    return salespersons[i];
                }
            }
            return false;
        },
        update_coupon_remaining: function(coupon) {
            var coupons = this.pos.coupons;
            for (var i in coupons){
                if(coupons[i] == coupon) {
                    coupons[i].remaining_to_use = coupons[i].remaining_to_use-1;
                }
            }
            this.pos.coupons = coupons;
        },
        apply_offer_noor1: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            var isU02 = false;
            var isL02 = false;
            for (var i in orderlines) {
                if (orderlines[i].product.display_name == 'U02 | عطر شجن') {
                    isU02 = true;
                } else if (orderlines[i].product.display_name == 'L02 | عطر وِئام') {
                    isL02 = true;
                }
            }
            if (isU02 && isL02) {
                for (var i in orderlines) {
                    if (orderlines[i].product.display_name == 'U02 | عطر شجن') {
                        orderlines[i].set_discount(20.000);
                    } else if (orderlines[i].product.display_name == 'L02 | عطر وِئام') {
                        orderlines[i].set_discount(25.000);
                    }
                }
            }
            return true;
        },
        apply_offer_wala2: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 4);
            if (count > 0) {
                var maxCount = count*4;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(21.875);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(21.875);
                            }
                        }
                    }
                }
            }
            return true;
        },
        apply_offer_b7r2: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 4);
            if (count > 0) {
                var maxCount = count*4;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(37.500);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(37.500);
                            }
                        }
                    }
                }
            }
            return true;
        },
        apply_offer_b7r3: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var countPERFUMES = 0;
            var countBAKHOR = 0;
            var countMARASH = 0;
            console.log(orderlines);
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        countMARASH += orderlines[i].quantity;
                    } else if (orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق' || orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب') {
                        countPERFUMES += orderlines[i].quantity;
                    }
                }
                if (orderlines[i].product.display_name == 'Bakhoor Aleshk | بخور العشق') {
                    countBAKHOR += orderlines[i].quantity;
                }
            }
            console.log(countMARASH);
            console.log(countPERFUMES);
            console.log(countBAKHOR);
            countMARASH = parseInt(countMARASH / 3);
            if (countMARASH > 0 && countPERFUMES > 0 && countBAKHOR > 0) {
                console.log("Correct Combination");
                var maxCount = Math.min(countMARASH, countBAKHOR, countPERFUMES)*3;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_unit_price(10);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_unit_price(10);
                            }
                        }
                    }
                }
                var maxCount = Math.min(countMARASH, countBAKHOR, countPERFUMES);
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق' || orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(100.000);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(100.000);
                            }
                        }
                    }
                }

            }
            return true;
        },
        apply_offer_b7r5: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'BAKHOOR | البخور') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 2);
            if (count > 0) {
                var maxCount = count*2;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'BAKHOOR | البخور') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(25.000);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(25.000);
                            }
                        }
                    }
                }
            }
            return true;
        },
        apply_offer: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 4);
            if (count > 0) {
                var maxCount = count*4;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(21.875);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(21.875);
                            }
                        }
                    }
                }
                for (var i in orderlines) {
                    if (orderlines[i].product.display_name == 'Delivery Fees') {
                        orderlines[i].set_discount(100);
                    }
                }
            }
            return true;
        },
        apply_offer4: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 4);
            if (count > 0) {
                var maxCount = count*4;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(6.25);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(6.25);
                            }
                        }
                    }
                }

            }
            return true;
        },
        apply_off1: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if ((orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق') || (orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب')) {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 3);
            if (count > 0) {
                var maxCount = count;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if ((orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق') || (orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب')) {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                console.log(qtyToNotDiscount);
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(100.00);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(100.00);
                            }
                        }
                    }
                }
            }
            return true;
        },
        apply_off2: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            var count_36r = 0;
            var count_marash = 0;
            var count_bukhoor = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if ((orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق') || (orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب')) {
                        count_36r += orderlines[i].quantity;
                    }
                    else if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count_marash += orderlines[i].quantity;
                    }
                    else if (orderlines[i].product.pos_categ_id[1] == 'BAKHOOR | البخور') {
                        count_bukhoor += orderlines[i].quantity;
                    }
                }
            }
            if (count_36r > 0 && count_marash > 0 && count_bukhoor > 0) {
                var count = Math.min(count_36r, count_marash, count_bukhoor);
                var maxCount = count;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'LOVE GROUP | مجموعة حُب') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(40.00);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(40.00);
                            }
                        }
                        else if (orderlines[i].product.pos_categ_id[1] == 'USHK GROUP | مجموعة عشق') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(52.00);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(52.00);
                            }
                        }
                    }
                }
            }
            return true;
        },
        apply_off3: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 4);
            if (count > 0) {
                var maxCount = count*4;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(28.125);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(28.125);
                            }
                        }
                    }
                }

            }
            return true;
        },
        apply_offer6: function(coupon_discount_product) {
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            // Discount on the products level (Percentage)
            // Count the number of المرشات
            var count = 0;
            for (var i in orderlines) {
                if (orderlines[i].product.pos_categ_id) {
                    if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                        count += orderlines[i].quantity;
                    }
                }
            }
            count = parseInt(count / 6);
            if (count > 0) {
                var maxCount = count*6;
                var counter = 0;
                for (var i in orderlines) {
                    var remainingQtyToDiscount = maxCount-counter
                    if (remainingQtyToDiscount == 0)
                        break;
                    if (orderlines[i].product.pos_categ_id) {
                        if (orderlines[i].product.pos_categ_id[1] == 'HOME FRAGRANCE | المرشات') {
                            if (orderlines[i].quantity > remainingQtyToDiscount) {
                                var qtyToNotDiscount = orderlines[i].quantity-remainingQtyToDiscount
                                order.add_product(orderlines[i].product, {quantity: qtyToNotDiscount, price: orderlines[i].price});
                                orderlines[i].set_quantity(remainingQtyToDiscount);
                                orderlines[i].set_discount(12.50);
                                counter = counter + remainingQtyToDiscount
                            } else {
                                counter = counter + orderlines[i].quantity
                                orderlines[i].set_discount(12.50);
                            }
                        }
                    }
                }

            }
            return true;
        },
        apply_coupon: function(coupon_arg, coupon_discount_product) {
            if (!this.is_coupon_applied) {
                var order = this.pos.get_order();
                var orderlines = order.get_orderlines();
                // Discount on the products level (Percentage)
                if (coupon_arg.is_discount_on_all_products) {
                    for (var i in orderlines){
                        orderlines[i].set_discount(coupon_arg.discount_all_products_per);
                    }
                } else {
                    if (coupon_arg.is_discount_products) {
                        var product_lines = this.get_coupon_productlines(coupon_arg.product_lines);
                        for (var i in orderlines) {
                            for (var j in product_lines) {
                                if (orderlines[i].product.id == product_lines[j].product_id[0]) {
                                    orderlines[i].set_discount(product_lines[j].discount_per);
                                }
                            }
                        }
                    }
                }
                if (coupon_arg.is_discount_value) {
                    if (coupon_arg.discount_value > 0) {
                        var alreadyThere = false;
                        orderlines.forEach(function (line) {
                            if (line.product.id == coupon_discount_product) {
                                line.set_quantity(1);
                                line.set_unit_price(coupon_arg.discount_value*-1.0);
                                alreadyThere = true;
                            }
                        });
                        if (!alreadyThere) {
                            order.add_product(this.pos.db.get_product_by_id(coupon_discount_product), {quantity: 1, price: coupon_arg.discount_value*-1.0});
                        }
                    }
                }
                if (coupon_arg.salesperson_id) {
                    if (coupon_arg.salesperson_id.length > 0) {
                        order.set_salesperson(this.get_salesperson_by_id(coupon_arg.salesperson_id[0]));
                    }
                }
                this.is_coupon_applied = true;
                this.coupon = coupon_arg;
                this.update_coupon_remaining(coupon_arg);
                return true;
            }
            return false;
        },
        /* ---- Salesperson --- */
        // the salesperson related to the current order.
        set_salesperson: function(salesperson){
            this.assert_editable();
            this.set('salesperson',salesperson);
        },
        get_salesperson: function(){
            return this.get('salesperson');
        },
        get_salesperson_name: function(){
            var salesperson = this.get('salesperson');
            return salesperson ? salesperson.name : "";
        },
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.coupon = this.coupon ? this.coupon : false;
            json.salesperson_id = this.get_salesperson() ? this.get_salesperson() : false;
            return json;
        },
    });

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            var self = this;
            _super_posmodel.initialize.apply(this,arguments);
            // Forward the 'client' attribute on the selected order to 'selectedClient'
            function update_client() {
                var order = self.get_order();
                this.set('selectedClient', order ? order.get_client() : null );
                this.set('selectedSalesperson', order ? order.get_salesperson() : null );
            }
            this.get('orders').bind('add remove change', update_client, this);
            this.bind('change:selectedOrder', update_client, this);
        },
        get_salesperson: function() {
            var order = this.get_order();
            if (order) {
                return order.get_salesperson();
            }
            return null;
        },
    });

    screens.ActionpadWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            this.pos.bind('change:selectedSalesperson', function() {
                self.renderElement();
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.set-salesperson').click(function(){
                self.gui.show_screen('salespersonlist');
            });
        }
    });

    var SalespersonListScreenWidget = screens.ScreenWidget.extend({
        template: 'SalespersonListScreenWidget',

        init: function(parent, options){
            this._super(parent, options);
            this.salesperson_cache = new screens.DomCache();
        },
        auto_back: true,
        show: function(){
            var self = this;
            this._super();

            this.renderElement();
            this.details_visible = false;
            this.old_salesperson = this.pos.get_order().get_salesperson();

            this.$('.back').click(function(){
                self.gui.back();
            });

            this.$('.next').click(function(){
                self.save_changes();
                self.gui.back();    // FIXME HUH ?
            });

            var salespersons = this.pos.salespersons;

            this.render_list(salespersons);

            this.reload_salespersons();

            this.$('.salesperson-list-contents').delegate('.salesperson-line','click',function(event){
                self.line_select(event,$(this),parseInt($(this).data('id')));
            });

            var search_timeout = null;

            if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress',function(event) {
                clearTimeout(search_timeout);

                var searchbox = this;

                search_timeout = setTimeout(function(){
                    self.perform_search(searchbox.value, event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
        },
        hide: function () {
            this._super();
            this.new_salesperson = null;
        },
        perform_search: function(query, associate_result){
            var salespersons = this.pos.salespersons;
            var results = [];
            for(var i = 0; i < salespersons.length; i++){
                if (salespersons[i].name.toLowerCase().includes(query.toLowerCase())) {
                    results.push(salespersons[i]);
                }
            }
            this.render_list(results);
        },
        clear_search: function(){
            var salespersons = this.pos.salespersons;
            this.render_list(salespersons);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        render_list: function(salespersons){
            var contents = this.$el[0].querySelector('.salesperson-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = Math.min(salespersons.length,1000); i < len; i++){
                var salesperson    = salespersons[i];
                var salespersonline = this.salesperson_cache.get_node(salesperson.id);
                if(!salespersonline){
                    var salespersonline_html = QWeb.render('SalespersonLine',{widget: this, salesperson:salespersons[i]});
                    var salespersonline = document.createElement('tbody');
                    salespersonline.innerHTML = salespersonline_html;
                    salespersonline = salespersonline.childNodes[1];
                    this.salesperson_cache.cache_node(salesperson.id,salespersonline);
                }
                if( salesperson === this.old_salesperson ){
                    salespersonline.classList.add('highlight');
                }else{
                    salespersonline.classList.remove('highlight');
                }
                contents.appendChild(salespersonline);
            }
        },
        save_changes: function(){
            var order = this.pos.get_order();
            if( this.has_salesperson_changed() ){
                order.set_salesperson(this.new_salesperson);
            }
        },
        has_salesperson_changed: function(){
            if( this.old_salesperson && this.new_salesperson ){
                return this.old_salesperson.id !== this.new_salesperson.id;
            }else{
                return !!this.old_salesperson !== !!this.new_salesperson;
            }
        },
        toggle_save_button: function(){
            var $button = this.$('.button.next');
            if( this.new_salesperson ){
                if( !this.old_salesperson){
                    $button.text(_t('Set Salesperson'));
                }else{
                    $button.text(_t('Change Salesperson'));
                }
            }else{
                $button.text(_t('Deselect Salesperson'));
            }
            $button.toggleClass('oe_hidden',!this.has_salesperson_changed());
        },
        get_salesperson_by_id: function(id) {
            var salespersons = this.pos.salespersons;
            var results = [];
            for(var i = 0; i < salespersons.length; i++){
                if (salespersons[i].id == id) {
                    return salespersons[i];
                }
            }
            return false;
        },
        reload_salespersons: function(){
            var self = this;
            return this.pos.load_new_partners().then(function(){
                // partners may have changed in the backend
                self.salesperson_cache = new screens.DomCache();

                self.render_list(this.pos.salespersons);

                // update the currently assigned client if it has been changed in db.
                var curr_salesperson = self.pos.get_order().get_salesperson();
                if (curr_salesperson) {
                    self.pos.get_order().set_salesperson(this.get_salesperson_by_id(curr_salesperson.id));
                }
            });
        },
        line_select: function(event,$line,id){
            var salesperson = this.get_salesperson_by_id(id);
            this.$('.salesperson-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.new_salesperson = null;
                this.toggle_save_button();
            }else{
                this.$('.salesperson-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                var y = event.pageY - $line.parent().offset().top;
                this.new_salesperson = salesperson;
                this.toggle_save_button();
            }
        },
        close: function(){
            this._super();
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.hide();
            }
        },
    });
    gui.define_screen({name:'salespersonlist', widget: SalespersonListScreenWidget});

    var CouponScreenWidget = screens.ScreenWidget.extend({
        template: 'CouponScreenWidget',

        init: function(parent, options) {
            this.coupon_discount_product = null;
            this._super(parent, options);
        },
        get_coupon_by_code: function(code) {
            var coupons = this.pos.coupons;
            for (var i in coupons){
                if(coupons[i].ref == code)
                    return coupons[i];
            }
            return false;
        },
        show: function() {
            var self = this;
            this._super();
            if(!this.coupon_discount_product)
                this.coupon_discount_product = get_discount_product(this.pos.db.product_by_id);
            if (this.coupon_discount_product == false) {
                self.gui.close_popup();
                console.log("You must have a product called 'Coupon Discount' to continue.");
            }
            self.$(".error-message").hide();
            this.$('.confirm').on('click',function() {
                var inputValue = self.$('.popup-input').val();
                if (inputValue.length!=0) {
                    var order = self.pos.get_order();
                    var coupon = self.get_coupon_by_code(inputValue);
                    if (coupon) {
                        if (coupon.remaining_to_use > 0) {
                            if (!order.is_coupon_applied) {
                                var orderlines = order.get_orderlines();
                                if (orderlines.length!=0) {
                                    order.apply_coupon(coupon, self.coupon_discount_product);
                                    if (inputValue == 'B7R2') {
                                        order.apply_offer_b7r2(self.coupon_discount_product);
                                    }
                                    if (inputValue == 'B7R3') {
                                        order.apply_offer_b7r3(self.coupon_discount_product);
                                    }
                                    if (inputValue == 'B7R5') {
                                        order.apply_offer_b7r5(self.coupon_discount_product);
                                    }
                                    if (inputValue == 'WALA2') {
                                        order.apply_offer_wala2(self.coupon_discount_product);
                                    }
                                    if (inputValue == 'NOOR1') {
                                        order.apply_offer_noor1(self.coupon_discount_product);
                                    }
                                    if (inputValue == 'NOOR2') {
                                        order.apply_offer_wala2(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFFER') {
                                        order.apply_offer(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFFER4') {
                                        order.apply_offer4(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFFER6') {
                                        order.apply_offer6(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFF1') {
                                        order.apply_off1(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFF2') {
                                        order.apply_off2(self.coupon_discount_product);
                                    }
                                    else if (inputValue == 'OFF3') {
                                        order.apply_off3(self.coupon_discount_product);
                                    }
                                    self.$(".popup-input").removeClass("az-error");
                                    self.$(".empty-value").hide();
                                    self.$(".negative-value").hide();
                                    self.$(".already-applied").hide();
                                    self.$(".wrong-value").hide();
                                    self.$(".not-valid").hide();
                                    self.$(".empty-orderline").hide();
                                    self.gui.close_popup();
                                } else {
                                    self.$(".empty-value").hide();
                                    self.$(".negative-value").hide();
                                    self.$(".wrong-value").hide();
                                    self.$(".already-applied").hide();
                                    self.$(".not-valid").hide();
                                    self.$(".popup-input").removeClass("az-error");
                                    self.$(".empty-orderline").show();
                                    self.$(".popup-input").addClass("az-error");
                                }
                            } else {
                                self.$(".empty-value").hide();
                                self.$(".negative-value").hide();
                                self.$(".wrong-value").hide();
                                self.$(".not-valid").hide();
                                self.$(".empty-orderline").hide();
                                self.$(".popup-input").removeClass("az-error");
                                self.$(".already-applied").show();
                                self.$(".popup-input").addClass("az-error");
                            }
                        } else {
                            self.$(".empty-value").hide();
                            self.$(".negative-value").hide();
                            self.$(".wrong-value").hide();
                            self.$(".already-applied").hide();
                            self.$(".empty-orderline").hide();
                            self.$(".popup-input").removeClass("az-error");
                            self.$(".not-valid").show();
                            self.$(".popup-input").addClass("az-error");
                        }
                    } else {
                        self.$(".empty-value").hide();
                        self.$(".negative-value").hide();
                        self.$(".not-valid").hide();
                        self.$(".already-applied").hide();
                        self.$(".empty-orderline").hide();
                        self.$(".popup-input").removeClass("az-error");
                        self.$(".wrong-value").show();
                        self.$(".popup-input").addClass("az-error");
                    }
                } else {
                    self.$(".wrong-value").hide();
                    self.$(".negative-value").hide();
                    self.$(".not-valid").hide();
                    self.$(".already-applied").hide();
                    self.$(".empty-orderline").hide();
                    self.$(".popup-input").removeClass("az-error");
                    self.$(".empty-value").show();
                    self.$(".popup-input").addClass("az-error");
                }
            });
            this.$('.cancel').on('click',function() {
                self.$(".popup-input").removeClass("az-error");
                self.$(".empty-value").hide();
                self.$(".already-applied").hide();
                self.$(".wrong-value").hide();
                self.$(".not-valid").hide();
                self.$(".empty-orderline").hide();
                self.gui.close_popup();
            });
        },
    });
    gui.define_popup({name:'CouponScreenWidget', widget: CouponScreenWidget});

    var CouponButton = screens.ActionButtonWidget.extend({
        template: 'CouponButton',
        button_click: function(){
            this.gui.show_popup('CouponScreenWidget',{});
       }
    });

    screens.define_action_button({
            'name': 'coupon',
            'widget': CouponButton
    });

    return {
        CouponScreenWidget: CouponScreenWidget,
        SalespersonListScreenWidget: SalespersonListScreenWidget,
    };
});
