from odoo.tests import tagged, HttpCase
from .common import HelpdeskProjectSyncCommon


@tagged('post_install', '-at_install')
class TestCustomerRequest(HttpCase, HelpdeskProjectSyncCommon):

    def test_01_public_form_creates_ticket(self):
        """Test 1: Public form creates a Helpdesk Ticket with request_source='web'."""
        response = self.url_open('/customer/request/submit', data={
            'company_name': 'ACME Corp',
            'contact_name': 'John Doe',
            'contact_phone': '0901234567',
            'contact_email': 'john@acme.com',
            'contact_department': 'IT',
            'contact_position': 'Manager',
            'name': 'System Outage',
            'description': 'Server is down',
        })
        self.assertEqual(response.status_code, 200)

        ticket = self.env['helpdesk.ticket'].sudo().search([('name', '=', 'System Outage')], limit=1)
        self.assertTrue(ticket.exists(), "Ticket should be created from public form")
        self.assertEqual(ticket.request_source, 'web')

    def test_02_company_name_saved_as_text(self):
        """Test 2: Company name submitted from form is saved as text company_name without auto res.partner mapping."""
        ticket = self.env['helpdesk.ticket'].sudo().create({
            'name': 'Feature Request',
            'description': 'Add dark mode',
            'request_source': 'web',
            'company_name': 'Stark Industries',
        })
        self.assertEqual(ticket.company_name, 'Stark Industries')
        self.assertFalse(ticket.partner_id, "partner_id should not be set automatically")

    def test_03_contact_info_saved(self):
        """Test 3: Contact information (name, email, phone, dept, pos) saved accurately on Ticket."""
        ticket = self.env['helpdesk.ticket'].sudo().create({
            'name': 'Bug Report',
            'description': 'Login issue',
            'request_source': 'web',
            'contact_name': 'Alice Smith',
            'contact_email': 'alice@example.com',
            'contact_phone': '0987654321',
            'contact_department': 'Finance',
            'contact_position': 'Accountant',
        })
        self.assertEqual(ticket.contact_name, 'Alice Smith')
        self.assertEqual(ticket.contact_email, 'alice@example.com')
        self.assertEqual(ticket.contact_phone, '0987654321')
        self.assertEqual(ticket.contact_department, 'Finance')
        self.assertEqual(ticket.contact_position, 'Accountant')

    def test_04_email_optional(self):
        """Test 4: Email field is optional on public request submission."""
        ticket = self.env['helpdesk.ticket'].sudo().create({
            'name': 'Urgent Help',
            'description': 'Printer broken',
            'request_source': 'web',
            'company_name': 'Wayne Enterprises',
            'contact_name': 'Bruce Wayne',
            'contact_phone': '0911111111',
            'contact_email': '',
        })
        self.assertTrue(ticket.exists())
        self.assertFalse(ticket.contact_email)
