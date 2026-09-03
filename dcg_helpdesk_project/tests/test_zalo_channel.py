from odoo.tests import tagged
from .common import HelpdeskProjectSyncCommon


@tagged('post_install', '-at_install')
class TestZaloChannel(HelpdeskProjectSyncCommon):

    def test_05_company_multiple_zalo_channels(self):
        """Test 5: A company (res.partner) can have multiple Zalo channels."""
        channel_1 = self.env['res.partner.zalo.channel'].create({
            'partner_id': self.partner_company_a.id,
            'name': 'Zalo Support 01',
            'channel_id': 'ZALO_CHAN_01',
        })
        channel_2 = self.env['res.partner.zalo.channel'].create({
            'partner_id': self.partner_company_a.id,
            'name': 'Zalo Support 02',
            'channel_id': 'ZALO_CHAN_02',
        })

        self.assertIn(channel_1, self.partner_company_a.zalo_channel_ids)
        self.assertIn(channel_2, self.partner_company_a.zalo_channel_ids)
        self.assertEqual(len(self.partner_company_a.zalo_channel_ids), 2)

    def test_06_zalo_channel_mapping(self):
        """Test 6: Zalo channel correctly maps back to company (partner_id)."""
        channel = self.env['res.partner.zalo.channel'].create({
            'partner_id': self.partner_company_b.id,
            'name': 'Zalo VIP Group',
            'channel_id': 'ZALO_VIP_99',
        })
        self.assertEqual(channel.partner_id, self.partner_company_b)
