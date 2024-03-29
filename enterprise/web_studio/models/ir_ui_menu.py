# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class IrUiMenu(models.Model):
    _name = 'ir.ui.menu'
    _inherit = ['studio.mixin', 'ir.ui.menu']

    @api.model
    def load_menus(self, debug):
        menu_root = super(IrUiMenu, self).load_menus(debug)

        if self.env.user.company_id.background_image:
            menu_root['background_image'] = True

        return menu_root

    @api.model
    def customize(self, to_move, to_delete):
        """ Apply customizations on menus. The deleted elements will no longer be active.
            When moving a menu, we needed to resequence it. Note that this customization will
                not be kept when upgrading the module (we don't put the ir.model.data in noupdate)

            :param to_move: a dict of modifications with menu ids as keys
                ex: {10: {'parent_id': 1, 'sequence': 0}, 11: {'sequence': 1}}
            :param to_delete: a list of ids
        """

        for menu in to_move:
            menu_id = self.browse(int(menu))
            if 'parent_id' in to_move[menu]:
                menu_id.parent_id = to_move[menu]['parent_id']
            if 'sequence' in to_move[menu]:
                menu_id.sequence = to_move[menu]['sequence']

        self.browse(to_delete).write({'active': False})

        return True
