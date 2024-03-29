# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.addons.sale_coupon.tests.common import TestSaleCouponCommon


class TestSaleCouponProgramRules(TestSaleCouponCommon):

    def setUp(self):
        super(TestSaleCouponProgramRules, self).setUp()
        self.iPadMini = self.env.ref('product.product_product_6').copy()

    # Test a free shipping reward + some expected behavior
    # (automatic line addition or removal)

    def test_free_shipping_reward(self):
        # Test case 1: The minimum amount is not reached, the reward should
        # not be created
        self.immediate_promotion_program.active = False
        self.env['sale.coupon.program'].create({
            'name': 'Free Shipping if at least 100 euros',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'free_shipping',
            'rule_minimum_amount': 100.0,
            'rule_minimum_amount_tax_inclusion': 'tax_included',
            'active': True,
        })

        order = self.env['sale.order'].create({
            'partner_id': self.steve.id,
        })

        # Price of order will be 5*1.15 = 5.75 (tax included)
        order.write({'order_line': [
            (0, False, {
                'product_id': self.product_B.id,
                'name': 'Product B',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 1)

        order.carrier_id = self.env['delivery.carrier'].search([])[1]
        order.get_delivery_price()
        order.set_delivery_line()

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 2)

        # Test Case 1b: amount is not reached but is on a threshold
        # The amount of deliverable product + the one of the delivery exceeds the minimum amount
        # yet the program shouldn't be applied
        # Order price will be 5.75 + 81.74*1.15 = 99.75
        order.write({'order_line': [
            (0, False, {
                'product_id': self.product_B.id,
                'name': 'Product 1B',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
                'price_unit': 81.74,
            })
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 3)

        # Test case 2: the amount is sufficient, the shipping should
        # be reimbursed
        order.write({'order_line': [
            (0, False, {
                'product_id': self.product_A.id,
                'name': 'Product 1',
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 1.0,
                'price_unit': 0.30,
            })
        ]})

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 5)

        # Test case 3: the amount is not sufficient now, the reward should be removed
        order.write({'order_line': [
            (2, order.order_line.filtered(lambda line: line.product_id.id == self.product_A.id).id, False)
        ]})
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 3)

    def test_shipping_cost(self):
        # Free delivery should not be taken into account when checking for minimum required threshold
        p_minimum_threshold_free_delivery = self.env['sale.coupon.program'].create({
            'name': 'free shipping if > 872 tax exl',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'free_shipping',
            'program_type': 'promotion_program',
            'rule_minimum_amount': 872,
        })
        p_minimum_threshold_discount = self.env['sale.coupon.program'].create({
            'name': '10% reduction if > 872 tax exl',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'discount',
            'program_type': 'promotion_program',
            'discount_type': 'percentage',
            'discount_percentage': 10.0,
            'rule_minimum_amount': 872,
        })
        order = self.empty_order
        self.iPadMini.taxes_id = self.tax_10pc_incl
        sol1 = self.env['sale.order.line'].create({
            'product_id': self.iPadMini.id,
            'name': 'iPad Mini',
            'product_uom_qty': 3.0,
            'order_id': order.id,
        })
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 2, "We should get the 10% discount line since we bought 872.73$")
        order.carrier_id = self.env['delivery.carrier'].search([])[1]
        order.get_delivery_price()
        order.set_delivery_line()

        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 3, "We should get the delivery line but not the free delivery since we are below 872.73$ with the 10% discount")

        p_minimum_threshold_free_delivery.sequence = 10
        (order.order_line - sol1).unlink()
        order.carrier_id = self.env['delivery.carrier'].search([])[1]
        order.get_delivery_price()
        order.set_delivery_line()
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 4, "We should get both promotion line since the free delivery will be applied first and won't change the SO total")

    def test_shipping_cost_numbers(self):
        # Free delivery should not be taken into account when checking for minimum required threshold
        tax_15pc_excl = self.env['account.tax'].create({
            'name': "15% Tax excl",
            'amount_type': 'percent',
            'amount': 15,
        })
        p_minimum_threshold_free_delivery = self.env['sale.coupon.program'].create({
            'name': 'free shipping if > 872 tax exl',
            'promo_code_usage': 'code_needed',
            'promo_code': 'free_shipping',
            'reward_type': 'free_shipping',
            'program_type': 'promotion_program',
            'rule_minimum_amount': 872,
        })
        self.p2 = self.env['sale.coupon.program'].create({
            'name': 'Buy 4 ipads, get one for free',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'product',
            'program_type': 'promotion_program',
            'reward_product_id': self.iPadMini.id,
            'rule_min_quantity': 3,
            'rule_products_domain': '[["name","ilike","ipad mini"]]',
        })
        order = self.empty_order
        self.iPadMini.taxes_id = self.tax_10pc_incl
        sol1 = self.env['sale.order.line'].create({
            'product_id': self.iPadMini.id,
            'name': 'iPad Mini',
            'product_uom_qty': 3.0,
            'order_id': order.id,
        })
        # The delivery product has 15% tax on dball but not on dbbase. A module is probably adding the tax at some point.
        # We want that tax to be set so we can be sure it is not added to the order total paid amount used in coupon as
        # it was wrongly done before.
        carrier = self.env.ref('delivery.delivery_carrier')
        carrier.product_id.taxes_id = tax_15pc_excl
        order.carrier_id = carrier
        order.get_delivery_price()
        order.set_delivery_line()
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 2)
        self.assertEqual(order.reward_amount, 0)
        # Shipping is 20 + 15%tax
        self.assertEqual(sum([line.price_total for line in order._get_no_effect_on_threshold_lines()]), 23)
        self.assertEqual(order.amount_untaxed, 872.73 + 20)

        self.env['sale.coupon.apply.code'].sudo().apply_coupon(order, 'free_shipping')
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 3, "We should get the delivery line and the free delivery since we are below 872.73$ with the 10% discount")
        self.assertEqual(order.reward_amount, -20)
        self.assertEqual(sum([line.price_total for line in order._get_no_effect_on_threshold_lines()]), 0)
        self.assertEqual(order.amount_untaxed, 872.73)

        sol1.product_uom_qty = 4
        order.recompute_coupon_lines()
        self.assertEqual(len(order.order_line.ids), 4, "We should get a free iPad Mini")
        self.assertEqual(order.reward_amount, -20 -290.91)
        self.assertEqual(sum([line.price_total for line in order._get_no_effect_on_threshold_lines()]), 0)
        self.assertEqual(order.amount_untaxed, 872.73)

        p_specific_product = self.env['sale.coupon.program'].create({
            'name': '20% reduction on ipad in cart',
            'promo_code_usage': 'no_code_needed',
            'reward_type': 'discount',
            'program_type': 'promotion_program',
            'discount_type': 'percentage',
            'discount_percentage': 20.0,
            'discount_apply_on': 'cheapest_product',
        })
        p_specific_product.discount_apply_on = 'cheapest_product'
        order.recompute_coupon_lines()
        # 872.73 - (20% of 1 iPad) = 872.73 - 58.18 = 814.55
        self.assertEqual(order.amount_untaxed, 814.55, "One iPad should be discounted by 20%")
