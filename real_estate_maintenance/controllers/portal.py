from collections import OrderedDict

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class ProjectCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'maintenance_request_count' in counters:
            values['maintenance_request_count'] = request.env['maintenance.request'].search_count([]) \
                if request.env['maintenance.request'].check_access_rights('read', raise_exception=False) else 0
        if 'real_estate_property_count' in counters:
            values['real_estate_property_count'] = \
                len(request.env['sale.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)]).mapped('operating_unit_id')) \
                if request.env['sale.order'].check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/issue-type/get'], type='json', method=["GET", "POST"], auth="public")
    def issue_types_get(self, **kwargs):
        issue_types = request.env['maintenance.issue.type'].sudo().search([])
        res = []
        for issue_type in issue_types:
            res.append({"id": issue_type.id, "name": issue_type.name})
        return res

    @http.route(['/my/maintenance-requests', '/my/maintenance-requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_maintenance_requests(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        maintenance_request = request.env['maintenance.request']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'request_date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'state': {'label': _('Status'), 'order': 'state'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'closed': {'label': _('Closed'), 'domain': [('state', '=', 'closed')]},
            'refused': {'label': _('Refused'), 'domain': [('state', '=', 'refused')]},
            'ongoing': {'label': _('Ongoing'), 'domain': [('state', '=', 'ongoing')]},
            'confirm': {'label': _('Confirm'), 'domain': [('state', '=', 'confirm')]},
        }
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin),
                       ('create_date', '<=', date_end)]

        maintenance_request_count = maintenance_request.search_count(domain)
        pager = portal_pager(
            url="/my/maintenance-requests",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=maintenance_request_count,
            page=page,
            step=self._items_per_page
        )
        maintenance_requests = maintenance_request.search(domain, order=order, limit=self._items_per_page,
                                                          offset=pager['offset'])
        request.session['my_maintenance_requests_history'] = maintenance_requests.ids[:100]

        values.update({
            'date': date_begin,
            'maintenance_requests': maintenance_requests,
            'page_name': 'maintenance_requests',
            'pager': pager,
            'default_url': '/my/maintenance-requests',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("real_estate_maintenance.portal_my_maintenance_requests", values)

    @http.route(['/my/maintenance-request'], type='http', methods=["POST"], auth="user", website=True)
    def portal_maintenance_request_new(self, **post):

        product_id = request.env['product.product'].browse(int(post['property_id']))
        maintenance_request = request.env['maintenance.request'].create({
            'property_id': int(post['property_id']),
            'property_rent_id': product_id.property_id.id,
            'operating_unit_id': product_id.property_id.property_address_area.id,
            'requester_id': request.env.user.partner_id.id,
            'issue_type': int(post['issue_type']),
            'issue_description': post['issue_description']
        })
        return request.redirect('/my/maintenance-request/{}'.format(maintenance_request.id))

    @http.route(['/my/maintenance-request/<int:maintenance_request_id>'], type='http', auth="public", website=True)
    def portal_my_maintenance_request(self, maintenance_request_id, access_token=None, **kw):
        try:
            maintenance_request_sudo = self._document_check_access('maintenance.request', maintenance_request_id,
                                                                   access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        maintenance_request_sudo = maintenance_request_sudo if access_token\
            else maintenance_request_sudo.with_user(request.env.user)
        for attachment in maintenance_request_sudo.attachment_ids:
            attachment.sudo().generate_access_token()
        values = self._maintenance_request_get_page_view_values(
            maintenance_request_sudo, access_token, **kw)
        return request.render("real_estate_maintenance.portal_my_maintenance_request", values)

    def _maintenance_request_get_page_view_values(self, maintenance_request, access_token, **kwargs):
        history = 'my_maintenance_requests_history'
        values = {
            'page_name': 'maintenance_request',
            'maintenance_request': maintenance_request.sudo(),
            'user': request.env.user,
        }
        return self._get_page_view_values(maintenance_request, access_token, values, history, False, **kwargs)

    @http.route(['/my/properties'], type='http', auth="user", website=True)
    def portal_my_properties(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        real_estate_property = request.env['product.template'].sudo()
        properties = request.env['sale.order.line'].sudo().search([('order_id', 'in' , request.env['sale.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)]).ids)]).mapped('product_id').ids

        domain = [('id', 'in', properties)]

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name desc'},
        }

        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []}
        }
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        real_estate_property_count = real_estate_property.search_count(domain)
        pager = portal_pager(
            url="/my/maintenance-requests",
            url_args={'date_begin': date_begin,
                      'date_end': date_end, 'sortby': sortby},
            total=real_estate_property_count,
            page=page,
            step=self._items_per_page
        )
        real_estate_properties = real_estate_property.search(domain)
        print("6666666666666666666666    ", domain)
        request.session['my_real_estate_properties_history'] = real_estate_properties.ids[:100]
        print(real_estate_properties)

        values.update({
            'real_estate_properties': real_estate_properties,
            'page_name': 'real_estate_properties',
            'pager': pager,
            'default_url': '/my/properties',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })

        return request.render("real_estate_maintenance.portal_my_properties", values)
