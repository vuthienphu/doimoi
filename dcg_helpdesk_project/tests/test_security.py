from odoo.tests import tagged, HttpCase
from .common import HelpdeskProjectSyncCommon
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install')
class TestSecurityRestrictions(HttpCase, HelpdeskProjectSyncCommon):

    def test_20_public_user_security_restriction(self):
        """Test 20: Public user cannot read/write Helpdesk Tickets or Backend Models directly."""
        public_user = self.env.ref('base.public_user')
        public_env = self.env(user=public_user)

        # Public user reading helpdesk.ticket directly should raise AccessError or return empty
        with self.assertRaises(AccessError):
            public_env['helpdesk.ticket'].search([])

        # Public user reading project.task directly should raise AccessError
        with self.assertRaises(AccessError):
            public_env['project.task'].search([])

        # Public user reading res.partner directly should raise AccessError
        with self.assertRaises(AccessError):
            public_env['res.partner'].search([])
