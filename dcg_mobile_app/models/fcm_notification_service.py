# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    _HAS_FIREBASE_ADMIN = True
except ImportError:
    _HAS_FIREBASE_ADMIN = False
    _logger.info("firebase_admin is not installed. Will use HTTP/REST fallback for FCM if configured.")


class MobileNotificationService(models.AbstractModel):
    _name = 'mobile.notification.service'
    _description = 'Dịch vụ Push Notification Firebase Cloud Messaging (FCM)'

    @api.model
    def _get_fcm_config(self):
        """Lấy cấu hình Firebase từ System Parameters"""
        ICP = self.env['ir.config_parameter'].sudo()
        project_id = ICP.get_param('dcg_mobile_app.fcm_project_id', '').strip()
        service_account_json = ICP.get_param('dcg_mobile_app.fcm_service_account_json', '').strip()
        server_key = ICP.get_param('dcg_mobile_app.fcm_server_key', '').strip()
        return {
            'project_id': project_id,
            'service_account_json': service_account_json,
            'server_key': server_key,
        }

    @api.model
    def _init_firebase_app(self, service_account_json):
        """Khởi tạo Firebase Admin SDK nếu có cài đặt"""
        if not _HAS_FIREBASE_ADMIN:
            return None
        try:
            # Kiểm tra app default đã khởi tạo chưa
            return firebase_admin.get_app()
        except ValueError:
            pass

        if not service_account_json:
            _logger.warning("FCM: Chưa cấu hình service_account_json trong System Parameters.")
            return None

        try:
            cred_dict = json.loads(service_account_json)
            cred = credentials.Certificate(cred_dict)
            return firebase_admin.initialize_app(cred)
        except Exception as e:
            _logger.exception("FCM: Lỗi khởi tạo Firebase Admin SDK: %s", e)
            return None

    @api.model
    def send_notification_to_users(self, user_ids, title, body, model=None, res_id=None, extra_data=None):
        """
        Gửi push notification tới danh sách user_ids
        :param user_ids: list ID hoặc recordset res.users
        :param title: Tiêu đề thông báo
        :param body: Nội dung thông báo
        :param model: Tên model Odoo (ví dụ: 'helpdesk.ticket')
        :param res_id: ID bản ghi (ví dụ: 182)
        :param extra_data: dict dữ liệu bổ sung
        """
        if isinstance(user_ids, (int, str)):
            user_ids = [int(user_ids)]
        elif hasattr(user_ids, 'ids'):
            user_ids = user_ids.ids

        if not user_ids:
            return {'status': 'error', 'message': 'Danh sách user_ids rỗng.'}

        # Tìm các token đang active của các user này
        DeviceToken = self.env['mobile.device.token'].sudo()
        tokens = DeviceToken.search([
            ('user_id', 'in', user_ids),
            ('is_active', '=', True)
        ])

        if not tokens:
            _logger.info("FCM: Không tìm thấy thiết bị nào đang active cho user_ids=%s", user_ids)
            return {'status': 'success', 'sent_count': 0, 'message': 'Không có thiết bị active.'}

        data_payload = {
            'model': str(model or ''),
            'res_id': str(res_id or ''),
            'click_action': 'OPEN_RECORD',
        }
        if extra_data and isinstance(extra_data, dict):
            for k, v in extra_data.items():
                data_payload[str(k)] = str(v)

        config = self._get_fcm_config()

        # 1. Ưu tiên gửi qua Firebase Admin SDK nếu có
        if _HAS_FIREBASE_ADMIN and config.get('service_account_json'):
            fb_app = self._init_firebase_app(config['service_account_json'])
            if fb_app:
                return self._send_via_firebase_admin(tokens, title, body, data_payload)

        # 2. Gửi qua FCM Legacy / HTTP API nếu có server_key
        if config.get('server_key'):
            return self._send_via_fcm_http(tokens, title, body, data_payload, config['server_key'])

        # 3. Nếu chưa cấu hình credential, ghi log mô phỏng (cho dev/test)
        _logger.warning("FCM: Chưa cấu hình Firebase Service Account hoặc Server Key. Mô phỏng gửi thông báo:")
        _logger.warning("FCM Mock -> Title: %s, Body: %s, Data: %s, Target Tokens: %s", title, body, data_payload, tokens.mapped('token'))
        return {
            'status': 'mocked',
            'sent_count': len(tokens),
            'message': 'Đã mô phỏng gửi thông báo (cần cấu hình Firebase Service Account để gửi thực tế).'
        }

    @api.model
    def _send_via_firebase_admin(self, tokens, title, body, data_payload):
        """Gửi qua thư viện firebase-admin chuẩn Google"""
        success_count = 0
        failed_count = 0

        for record in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data_payload,
                    token=record.token,
                )
                response = messaging.send(message)
                success_count += 1
                _logger.info("FCM: Đã gửi thông báo tới %s, response=%s", record.name, response)
            except messaging.UnregisteredError:
                _logger.warning("FCM: Token hết hạn/không tồn tại cho thiết bị %s. Vô hiệu hóa.", record.name)
                record.write({'is_active': False})
                failed_count += 1
            except Exception as e:
                _logger.exception("FCM: Lỗi gửi tới thiết bị %s: %s", record.name, e)
                failed_count += 1

        return {
            'status': 'success',
            'sent_count': success_count,
            'failed_count': failed_count,
        }

    @api.model
    def _send_via_fcm_http(self, tokens, title, body, data_payload, server_key):
        """Gửi qua REST API FCM"""
        success_count = 0
        failed_count = 0

        headers = {
            'Authorization': f'key={server_key}',
            'Content-Type': 'application/json; UTF-8',
        }

        for record in tokens:
            body_json = {
                'to': record.token,
                'notification': {
                    'title': title,
                    'body': body,
                    'sound': 'default',
                },
                'data': data_payload,
                'priority': 'high',
            }
            try:
                res = requests.post(
                    'https://fcm.googleapis.com/fcm/send',
                    headers=headers,
                    data=json.dumps(body_json),
                    timeout=10,
                )
                if res.status_code == 200:
                    res_data = res.json()
                    if res_data.get('success', 0) > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        # Kiểm tra nếu token không hợp lệ
                        results = res_data.get('results', [])
                        if results and results[0].get('error') in ('NotRegistered', 'InvalidRegistration'):
                            record.write({'is_active': False})
                else:
                    failed_count += 1
            except Exception as e:
                _logger.exception("FCM HTTP Error: %s", e)
                failed_count += 1

        return {
            'status': 'success',
            'sent_count': success_count,
            'failed_count': failed_count,
        }
