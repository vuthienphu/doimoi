# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.database import Database
from werkzeug.exceptions import NotFound


# class BravestarDatabase(Database):
#
#     @http.route(['/web/database/manager', '/web/database/selector'], type='http', auth='none')
#     def database_manager(self, **kw):
#         raise NotFound()


class BravestarLoginController(http.Controller):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        raise NotFound()

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        raise NotFound()
