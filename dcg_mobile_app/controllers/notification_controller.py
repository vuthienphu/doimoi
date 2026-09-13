# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class MobileNotificationController(http.Controller):

    def _get_json_payload(self):
        try:
            data = request.get_json_data()
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        try:
            if request.httprequest.data:
                return json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            pass
        return {}

    @http.route('/api/v1/mobile/notification/send', type='http', auth='public', methods=['POST'], cors='*', csrf=False)
    def send_notification(self, **kw):
        """
        API gửi Push Notification thủ công hoặc từ hệ thống ngoài
        Payload:
        {
            "user_ids": [1, 2],
            "title": "Tiêu đề thông báo",
            "body": "Nội dung thông báo",
            "model": "helpdesk.ticket",
            "res_id": 123,
            "extra_data": {}
        }
        """
        payload = self._get_json_payload()
        if not payload and kw:
            payload = kw

        user_ids = payload.get('user_ids')
        title = (payload.get('title') or '').strip()
        body = (payload.get('body') or '').strip()
        model = payload.get('model')
        res_id = payload.get('res_id')
        extra_data = payload.get('extra_data')

        if not user_ids or not title:
            return request.make_json_response({
                'code': 400,
                'message': 'Thiếu user_ids hoặc title trong yêu cầu.'
            }, status=400)

        try:
            service = request.env['mobile.notification.service'].sudo()
            result = service.send_notification_to_users(
                user_ids=user_ids,
                title=title,
                body=body,
                model=model,
                res_id=res_id,
                extra_data=extra_data,
            )
            return request.make_json_response({
                'code': 200,
                'message': 'Gửi thông báo hoàn tất',
                'data': result
            })
        except Exception as e:
            _logger.exception("Error sending notification via API: %s", e)
            return request.make_json_response({
                'code': 500,
                'message': f'Lỗi khi gửi thông báo: {str(e)}'
            }, status=500)
