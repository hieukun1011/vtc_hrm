from odoo import fields, api, models, _
from odoo.addons.test_convert.tests.test_env import record
from odoo.cli.scaffold import env
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, time
from random import randint
from bs4 import BeautifulSoup

class BlogWebsite(models.Model):
    _name = 'blog'
    _inherit = 'image.mixin'

    name = fields.Char(string='Title Blog')
    tag_ids = fields.Many2many(
        'blog.tag', string='Category')
    content = fields.Html('Content')
    question_form = fields.Html('Content')
    description = fields.Html('Description')
    state = fields.Selection(
        [('draft', 'Draft'), ('wait', 'Waiting'), ('approve', 'Approve')], default="draft")
    website_published = fields.Boolean(string='Push on website', readonly=1)
    # question = fields.Boolean("Question")
    atts = fields.Binary('File Attachment')
    url = fields.Char('URL')
    total_view = fields.Integer('Total View')
    date_push = fields.Date('Date push')
    meta = fields.Many2many('blog.meta', string='Meta')

    def send_request(self):
        self.state = 'wait'

    def approve_blog(self):
        self.state = 'approve'
        self.website_published = True

    def close_blog(self):
        self.state = 'draft'
        self.website_published = False

    @api.model
    def create(self, vals_list):
        content = vals_list.get('content')
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            list_img_tags = soup.find_all('img')
            for element in list_img_tags:
                if 'base64' in element['src']:
                    src_old = element['src']
                    val = {
                        'name': element['data-file-name'],
                        'datas': element['src'].split(',')[1],
                        'public': True,
                        'access_token': self.env['ir.attachment']._generate_access_token(),
                        'res_model': 'blog',
                        'res_id': self.id
                    }
                    check = self.env['ir.attachment'].search([('name', '=', val.get('name')),
                                                              ('res_model', '=', val.get('res_model')),
                                                              ('res_id', '=', self.id)])
                    if not check:
                        attachment_id = self.env['ir.attachment'].create(val)
                        attachment = self.env['ir.attachment'].browse(attachment_id.id)
                    else:
                        attachment = check
                    src_new = '/web/image/{}-{}/{}'.format(attachment.id, attachment.checksum[:8], attachment.name)
                    content = content.replace(src_old, src_new)
            vals_list['content'] = content
        return super(BlogWebsite, self).create(vals_list)

    def write(self, vals):
        self.ensure_one()
        content = vals.get('content')
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            list_img_tags = soup.find_all('img')
            for element in list_img_tags:
                if 'base64' in element['src']:
                    src_old = element['src']
                    val = {
                        'name': element['data-file-name'],
                        'datas': element['src'].split(',')[1],
                        'public': True,
                        'access_token': self.env['ir.attachment']._generate_access_token(),
                        'res_model': 'blog',
                        'res_id': self.id
                    }
                    check = self.env['ir.attachment'].search([('name', '=', val.get('name')),
                                                              ('res_model', '=', val.get('res_model')),
                                                              ('res_id', '=', self.id)])
                    if not check:
                        attachment_id = self.env['ir.attachment'].create(val)
                        attachment = self.env['ir.attachment'].browse(attachment_id.id)
                    else:
                        attachment = check
                    src_new = '/web/image/{}-{}/{}'.format(attachment.id, attachment.checksum[:8], attachment.name)
                    content = content.replace(src_old, src_new)
            vals['content'] = content
        return super(BlogWebsite, self).write(vals)

class BlogTag(models.Model):
    _name = 'blog.tag'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10, index=True, required=True)
    color = fields.Integer(
        string='Color Index', default=lambda self: randint(1, 11), )


class BlogMeta(models.Model):
    _name = 'blog.meta'
    _description = 'Blog Meta'

    name = fields.Char('Tag')
    color = fields.Integer(
        string='Color Index', default=lambda self: randint(1, 11), )