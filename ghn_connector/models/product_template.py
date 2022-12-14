from odoo import fields, models, api


class GHNProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Customize Attributes'

    gross_length = fields.Float(string='Length (cm)', required=True)
    gross_width = fields.Float(string='Width (cm)', required=True)
    gross_height = fields.Float(string='Height (cm)', required=True)
    is_auto_compute_weight = fields.Boolean(string='Auto compute weight', default=False)
    cm_uom_name = fields.Char(string='Height unit of measure label', compute='_compute_cm_uom_name')
    vol_weight_uom_name = fields.Char(string='Volumetric weight unit of measure label', compute='_compute_vol_weight_uom_name')

    @api.model
    def _get_vol_weight_uom_name_from_ir_config_parameter(self):
        return self._get_grams_uom_id_from_ir_config_parameter().display_name

    def _compute_vol_weight_uom_name(self):
        self.vol_weight_uom_name = self._get_vol_weight_uom_name_from_ir_config_parameter()

    @api.model
    def _get_grams_uom_id_from_ir_config_parameter(self):
        """ Get the unit of measure to interpret the `weight` field. By default, we considerer
        that weights are expressed in grams. Users can configure to express them in kilograms
        by adding an ir.config_parameter record with "product.weight_in_gram" as key
        and "0" as value.
        """
        product_weight_in_klgs_param = self.env['ir.config_parameter'].sudo().get_param('product.weight_in_gram')
        if product_weight_in_klgs_param == '0':
            return self.env.ref('uom.product_uom_kgm')
        else:
            return self.env.ref('uom.product_uom_gram')

    @api.model
    def create(self, vals):
        if vals.get('is_auto_compute_weight', False):
            gross_height = vals.get('gross_height') if vals.get('gross_height', False) else self.gross_height
            gross_width = vals.get('gross_width') if vals.get('gross_width', False) else self.gross_width
            gross_length = vals.get('gross_length') if vals.get('gross_length', False) else self.gross_length
            gross_weight = gross_height * gross_width * gross_length / 5000 * 1000
            vals.update({'weight': gross_weight})
        res = super(GHNProductTemplate, self).create(vals)
        return res

    def write(self, vals):
        if self.is_auto_compute_weight:
            gross_height = vals.get('gross_height') if vals.get('gross_height', False) else self.gross_height
            gross_width = vals.get('gross_width') if vals.get('gross_width', False) else self.gross_width
            gross_length = vals.get('gross_length') if vals.get('gross_length', False) else self.gross_length
            gross_weight = gross_height * gross_width * gross_length / 5000 * 1000
            vals.update({'weight': gross_weight})
        res = super(GHNProductTemplate, self).write(vals)
        return res

    @api.model
    def _get_cm_uom_name_from_ir_config_parameter(self):
        return self._get_common_uom_id_from_ir_config_parameter().display_name

    def _compute_cm_uom_name(self):
        self.cm_uom_name = self._get_cm_uom_name_from_ir_config_parameter()

    @api.model
    def _get_common_uom_id_from_ir_config_parameter(self):
        """ Get the unit of measure to interpret the `height, width, depth` field. By default, we considerer
        that height, width, depth are expressed in cm. Users can configure to express them in millimeter
        by adding an ir.config_parameter record with "product.product_in_mm" as key
        and "1" as value.
        -- It is recommended to use cm in units of Giao Hang Nhanh Carrier --
        """
        product_cm_in_lbs_param = self.env['ir.config_parameter'].sudo().get_param('product.product_in_mm')
        if product_cm_in_lbs_param == '1':
            return self.env.ref('uom.product_uom_millimeter')
        else:
            return self.env.ref('uom.product_uom_cm')
