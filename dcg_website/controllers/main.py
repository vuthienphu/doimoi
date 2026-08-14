# -*- coding: utf-8 -*-
import time
import json

from markupsafe import Markup
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class DoimoiWebsite(Website):
    def _structured_data(self, extra=None):
        settings = request.env['doimoi.site.settings'].sudo().search(self._website_domain(), order='website_id desc', limit=1)
        base_url = request.httprequest.url_root.rstrip('/')
        graph = [{
            '@type': 'Organization', '@id': base_url + '/#organization',
            'name': settings.copyright_name or request.website.name,
            'url': settings.website_url or base_url,
            'logo': base_url + '/web/image/website/%s/logo' % request.website.id,
            'email': settings.email or '', 'telephone': settings.phone or '',
            'address': {'@type': 'PostalAddress', 'streetAddress': settings.address or '', 'addressLocality': settings.location or ''},
            'sameAs': [url for url in [settings.facebook_url, settings.linkedin_url, settings.youtube_url] if url],
        }, {
            '@type': 'WebSite', '@id': base_url + '/#website', 'url': base_url,
            'name': request.website.name, 'publisher': {'@id': base_url + '/#organization'},
        }]
        if extra:
            graph.append(extra)
        return Markup(json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False))

    def _website_domain(self):
        return [('website_id', 'in', [False, request.website.id])]

    def _page_banner(self, page):
        return request.env['doimoi.hero'].sudo().search([
            ('page', '=', page), ('is_published', '=', True)
        ] + self._website_domain(), order='website_id desc, sequence, id', limit=1)

    def _page_sections(self, page):
        sections = request.env['doimoi.page.section'].sudo().search([
            ('page', '=', page), ('is_published', '=', True)
        ] + self._website_domain(), order='website_id desc, sequence, id')
        return {section.key: section for section in sections}

    def _page_values(self, page, include_sections=False, structured_extra=None):
        banner = self._page_banner(page)
        values = {
            'page_banner': banner,
            'additional_title': banner.seo_title or banner.title,
            'structured_data': self._structured_data(structured_extra),
        }
        if include_sections:
            values['page_sections'] = self._page_sections(page)
        return values

    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        hero = self._page_banner('home')
        clients = request.env['doimoi.client'].sudo().search([('is_published', '=', True)] + self._website_domain(), order='sequence, id')
        services = request.env['doimoi.service'].sudo().search([('is_published', '=', True)] + self._website_domain(), order='sequence')
        service_groups = services.mapped('service_group_id').sorted(key=lambda group: (group.sequence, group.id))
        statistics = request.env['doimoi.statistic'].sudo().search([('is_published', '=', True)] + self._website_domain(), order='sequence', limit=4)
        projects = request.env['doimoi.project'].sudo().search([('is_published', '=', True), ('is_featured', '=', True)] + self._website_domain(), order='sequence, id', limit=3)
        values = self._page_values('home', include_sections=True)
        values.update({
            'doimoi_clients': clients,
            'doimoi_hero': hero,
            'doimoi_service_groups': service_groups,
            'doimoi_all_services': services,
            'doimoi_statistics': statistics,
            'doimoi_projects': projects,
        })
        return request.render('website.homepage', values)

    @http.route(['/solutions', '/solutions/page/<int:page>'], type='http', auth="public", website=True, sitemap=True)
    def solutions(self, page=1, **kw):
        domain = [('is_published', '=', True)] + self._website_domain()
        total = request.env['doimoi.service'].sudo().search_count(domain)
        pager = request.website.pager(url='/solutions', total=total, page=page, step=12)
        services = request.env['doimoi.service'].sudo().search(domain, order='sequence, id', limit=12, offset=pager['offset'])
        service_groups = services.mapped('service_group_id').sorted(key=lambda group: (group.sequence, group.id))
        
        values = self._page_values('solutions')
        values.update({
            'doimoi_service_groups': service_groups,
            'doimoi_all_services': services,
            'pager': pager,
        })
        return request.render('dcg_website.solutions_page', values)

    @http.route(['/industries', '/industries/page/<int:page>'], type='http', auth="public", website=True, sitemap=True)
    def industries(self, page=1, **kw):
        domain = [('is_published', '=', True)] + self._website_domain()
        total = request.env['doimoi.industry'].sudo().search_count(domain)
        pager = request.website.pager(url='/industries', total=total, page=int(page), step=6)
        industries = request.env['doimoi.industry'].sudo().search(domain, order='sequence, id', limit=6, offset=pager['offset'])
        values = self._page_values('industries')
        values.update({
            'doimoi_industries': industries,
            'pager': pager,
        })
        return request.render('dcg_website.industries_page', values)

    @http.route(['/projects', '/projects/page/<int:page>'], type='http', auth='public', website=True, sitemap=True)
    def projects(self, page=1, **kw):
        domain = [('is_published', '=', True)] + self._website_domain()
        total = request.env['doimoi.project'].sudo().search_count(domain)
        pager = request.website.pager(url='/projects', total=total, page=page, step=6)
        projects = request.env['doimoi.project'].sudo().search(domain, order='sequence, id desc', limit=6, offset=pager['offset'])
        item_list = {'@type': 'ItemList', 'name': 'Dự án tiêu biểu', 'itemListElement': [
            {'@type': 'ListItem', 'position': index + 1, 'name': project.name, 'url': project.project_url or request.httprequest.url}
            for index, project in enumerate(projects)
        ]}
        values = self._page_values('projects', structured_extra=item_list)
        values.update({
            'projects': projects,
            'pager': pager,
        })
        return request.render('dcg_website.projects_page', values)

    @http.route('/about', type='http', auth="public", website=True, sitemap=True)
    def about(self, **kw):
        return request.render('dcg_website.about_page', self._page_values('about', include_sections=True))

    @http.route('/contactus', type='http', auth="public", website=True, sitemap=True,
                methods=['GET'])
    def contactus(self, **kw):
        settings = request.env['doimoi.site.settings'].sudo().search(self._website_domain(), order='website_id desc', limit=1)
        request.session['doimoi_form_started_at'] = time.time()
        values = self._page_values('contact', include_sections=True)
        values.update({
            'site_settings': settings,
            'form_error': kw.get('error'),
            'form_success': kw.get('submitted'),
            'request_type': kw.get('request_type') or 'consulting',
        })
        return request.render('dcg_website.contact_page', values)

    @http.route('/contactus/submit', type='http', auth="public", website=True,
                methods=['POST'], csrf=True)
    def contactus_submit(self, **post):
        name = (post.get('name') or '').strip()
        company_name = (post.get('company_name') or '').strip()
        phone = (post.get('phone') or '').strip()
        email = (post.get('email') or '').strip()
        description = (post.get('description') or '').strip()
        request_type = (post.get('request_type') or 'consulting').strip()

        started_at = request.session.get('doimoi_form_started_at', 0)
        last_submit = request.session.get('doimoi_last_submit_at', 0)
        now = time.time()
        if post.get('website_check') or not started_at or now - started_at < 2 or now - last_submit < 60:
            return request.redirect('/contactus?error=spam#contact-form')

        if not name or not company_name or not phone:
            return request.redirect('/contactus?error=required#contact-form')

        sales_team = request.env['crm.team'].sudo().search([
            ('active', '=', True),
            ('company_id', 'in', [False, request.website.company_id.id]),
        ], order='sequence, id', limit=1)
        request.env['crm.lead'].sudo().create({
            'name': 'Yêu cầu tư vấn - %s - %s' % (company_name, name),
            'contact_name': name,
            'partner_name': company_name,
            'phone': phone,
            'email_from': email,
            'description': 'Loại yêu cầu: %s\n\n%s' % (request_type, description),
            # Đưa yêu cầu website thẳng vào Pipeline và giao cho trưởng nhóm Sales,
            # tránh bị bộ lọc "My Pipeline" ẩn khỏi màn hình của quản trị viên.
            'type': 'opportunity',
            'team_id': sales_team.id or False,
            'user_id': sales_team.user_id.id or False,
            'company_id': request.website.company_id.id,
        })
        request.session['doimoi_last_submit_at'] = now
        return request.redirect('/contactus?submitted=1#contact-form')
