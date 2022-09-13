"""Part of odoo. See LICENSE file for full copyright and licensing details."""
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AttachmentController(http.Controller):

    @http.route(['/web/content2',
                 '/web/content2/<string:xmlid>',
                 '/web/content2/<string:xmlid>/<string:filename>',
                 '/web/content2/<int:id>',
                 '/web/content2/<int:id>/<string:filename>',
                 '/web/content2/<string:model>/<int:id>/<string:field>',
                 '/web/content2/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        return request.env['ir.http'].sudo()._get_content_common(xmlid=xmlid, model=model, res_id=id, field=field,
                                                                 unique=unique, filename=filename,
                                                                 filename_field=filename_field, download=download,
                                                                 mimetype=mimetype, access_token=access_token,
                                                                 token=token)
