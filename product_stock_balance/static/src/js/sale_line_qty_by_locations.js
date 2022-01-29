odoo.define('product_stock_balance.sale_line_qty_by_locations', function (require) {
"use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var _t = core._t;

    var QtyByLocations = Widget.extend({
        template: 'saleLineByLocations',
        events: _.extend({}, Widget.prototype.events, {
            'click .fa-list': '_onShowStocks',
        }),
        init: function (parent, params) {
            // to apply row data
            this.data = params.data;
            this._super(parent);
        },
        updateState: function (state) {
            //  to get the changes if product is changed
            this.$el.popover('dispose');
            var candidate = state.data[this.getParent().currentRow];
            if (candidate) {
                this.data = candidate.data;
                this.renderElement();
            }
        },
        _onShowStocks: function () {
            // The method to show stocks wizard
            this.$el.find('.fa-list').prop('special_click', true);
            var productID = this.data.product_id;
            if (productID && productID.data.id) {
                this.do_action({
                    name: this.data.name,
                    type: 'ir.actions.act_window',
                    res_model: 'product.product',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    view_type: 'form',
                    target: 'new',
                    context: {
                        form_view_ref: 'product_stock_balance.product_product_form_only_locations',
                    },
                    res_id: productID.data.id,
                });
            }
            else {
                this.do_warn(_t('Please define product first'));
            }
        },
    });

    widget_registry.add('qty_by_locations', QtyByLocations);

    return QtyByLocations;
});
