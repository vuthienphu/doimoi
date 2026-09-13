# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import http, fields, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class MobileAuthController(http.Controller):

    def _get_json_payload(self):
        """Lấy dữ liệu JSON từ body của request an toàn"""
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

    def _verify_google_id_token(self, id_token):
        """
        Xác thực Google ID Token với server Google OAuth2
        Trả về (email, error_message)
        """
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                return None, "Google ID Token không hợp lệ hoặc đã hết hạn."

            payload = res.json()
            email = payload.get('email')
            email_verified = payload.get('email_verified')
            # Lưu ý email_verified có thể là boolean hoặc string 'true'
            is_verified = email_verified is True or str(email_verified).lower() == 'true'

            if not email or not is_verified:
                return None, "Email Google chưa được xác thực."

            return email, None
        except Exception as e:
            _logger.exception("Lỗi kết nối Google verify token: %s", e)
            return None, "Không thể kết nối đến máy chủ xác thực Google."

    def _record_login_history(self, user=None, email=None, device_token=None, device_name=None, device_id=None, platform=None, app_version=None, status='success', failure_reason=None):
        """Ghi nhận lịch sử đăng nhập"""
        try:
            ip = request.httprequest.remote_addr or ''
            user_agent = request.httprequest.headers.get('User-Agent', '')

            request.env['mobile.login.history'].sudo().create({
                'user_id': user.id if user else False,
                'email_attempted': email or (user.login if user else ''),
                'device_token_id': device_token.id if device_token else False,
                'device_name': device_name or (device_token.device_name if device_token else ''),
                'device_id': device_id or (device_token.device_id if device_token else ''),
                'platform': platform or (device_token.platform if device_token else 'android'),
                'app_version': app_version or (device_token.app_version if device_token else ''),
                'ip_address': ip,
                'user_agent': user_agent,
                'status': status,
                'failure_reason': failure_reason,
            })
        except Exception as e:
            _logger.warning("Không thể ghi nhận mobile.login.history: %s", e)

    @http.route('/api/v1/mobile/auth/login', type='http', auth='public', methods=['POST'], cors='*', csrf=False)
    def mobile_login(self, **kw):
        """
        API Đăng nhập & Đăng ký thiết bị cho Mobile App
        Hỗ trợ:
        - google_id_token: Token do Google cấp trên App
        - email: Email của user
        - device_token: FCM Token của thiết bị
        - device_id: Hardware UUID
        - device_name: Tên dòng máy (iPhone, Samsung...)
        - platform: 'ios' | 'android' | 'web'
        - app_version: Phiên bản app
        """
        payload = self._get_json_payload()
        if not payload and kw:
            payload = kw

        email = (payload.get('email') or '').strip().lower()
        google_id_token = payload.get('google_id_token')
        device_token_str = (payload.get('device_token') or '').strip()
        device_id = (payload.get('device_id') or '').strip()
        device_name = (payload.get('device_name') or '').strip()
        platform = (payload.get('platform') or 'android').strip().lower()
        if platform not in ('ios', 'android', 'web'):
            platform = 'android'
        app_version = (payload.get('app_version') or '').strip()

        # 1. Xác thực Google Token nếu app gửi lên
        if google_id_token:
            verified_email, err = self._verify_google_id_token(google_id_token)
            if err:
                self._record_login_history(
                    email=email or 'unknown',
                    device_name=device_name,
                    device_id=device_id,
                    platform=platform,
                    app_version=app_version,
                    status='failed',
                    failure_reason=err,
                )
                return request.make_json_response({
                    'code': 401,
                    'message': err
                }, status=401)
            email = verified_email.lower()

        if not email:
            return request.make_json_response({
                'code': 400,
                'message': 'Vui lòng cung cấp email hoặc google_id_token.'
            }, status=400)

        # 2. Kiểm tra tài khoản trong Odoo (CHẶN MAIL LẠ - KHÔNG TỰ TẠO MỚI)
        User = request.env['res.users'].sudo()
        user = User.search([
            ('login', '=ilike', email),
            ('active', '=', True)
        ], limit=1)

        if not user:
            # Tra cứu phụ theo email field nếu login khác email
            user = User.search([
                ('email', '=ilike', email),
                ('active', '=', True)
            ], limit=1)

        if not user:
            # Ghi nhận log đăng nhập thất bại
            self._record_login_history(
                email=email,
                device_name=device_name,
                device_id=device_id,
                platform=platform,
                app_version=app_version,
                status='failed',
                failure_reason='Email không tồn tại trong hệ thống hoặc tài khoản đã bị khóa (Mail lạ)',
            )
            return request.make_json_response({
                'code': 403,
                'message': f'Tài khoản ({email}) chưa được cấp quyền truy cập hệ thống. Vui lòng liên hệ Quản trị viên.'
            }, status=403)

        # 3. Kiểm tra phân quyền truy cập
        allowed_groups = [
            'helpdesk_community.group_helpdesk_user',
            'helpdesk_community.group_helpdesk_team_leader',
            'helpdesk_community.group_helpdesk_manager',
            'base.group_user',
        ]
        has_access = any(user.has_group(grp) for grp in allowed_groups)
        if not has_access:
            self._record_login_history(
                user=user,
                email=email,
                device_name=device_name,
                device_id=device_id,
                platform=platform,
                app_version=app_version,
                status='failed',
                failure_reason='User không thuộc nhóm quyền cho phép truy cập app',
            )
            return request.make_json_response({
                'code': 403,
                'message': 'Bạn không có quyền truy cập ứng dụng này.'
            }, status=403)

        # 4. Ghi nhận/Cập nhật Device Token (FCM Token)
        dev_token_record = None
        if device_token_str:
            DeviceToken = request.env['mobile.device.token'].sudo()
            dev_token_record = DeviceToken.search([
                ('token', '=', device_token_str)
            ], limit=1)

            token_vals = {
                'user_id': user.id,
                'device_name': device_name or 'Thiết bị di động',
                'device_id': device_id,
                'platform': platform,
                'app_version': app_version,
                'is_active': True,
                'last_login': fields.Datetime.now(),
            }

            if dev_token_record:
                dev_token_record.write(token_vals)
            else:
                token_vals['token'] = device_token_str
                dev_token_record = DeviceToken.create(token_vals)

        # 5. Ghi log lịch sử đăng nhập thành công
        self._record_login_history(
            user=user,
            email=email,
            device_token=dev_token_record,
            device_name=device_name,
            device_id=device_id,
            platform=platform,
            app_version=app_version,
            status='success',
        )

        # 6. Kích hoạt phiên đăng nhập (Session)
        request.session.uid = user.id
        request.update_env(user=user.id)

        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')

        # Kiểm tra vai trò
        role = 'user'
        if user.has_group('helpdesk_community.group_helpdesk_manager') or user.has_group('base.group_system'):
            role = 'manager'
        elif user.has_group('helpdesk_community.group_helpdesk_team_leader'):
            role = 'team_leader'

        return request.make_json_response({
            'code': 200,
            'message': 'Đăng nhập thành công',
            'data': {
                'session_id': request.session.sid,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email or user.login,
                    'role': role,
                    'avatar_url': f"{base_url}/web/image/res.users/{user.id}/avatar_128",
                },
                'device': {
                    'registered': bool(dev_token_record),
                    'token_id': dev_token_record.id if dev_token_record else None,
                    'is_active': dev_token_record.is_active if dev_token_record else False,
                }
            }
        })

    @http.route('/api/v1/mobile/auth/logout', type='http', auth='public', methods=['POST'], cors='*', csrf=False)
    def mobile_logout(self, **kw):
        """
        API Đăng xuất & Hủy kích hoạt Device Token
        """
        payload = self._get_json_payload()
        if not payload and kw:
            payload = kw

        device_token_str = (payload.get('device_token') or '').strip()

        uid = request.session.uid
        user = request.env['res.users'].sudo().browse(uid) if uid else None

        dev_token_record = None
        if device_token_str:
            dev_token_record = request.env['mobile.device.token'].sudo().search([
                ('token', '=', device_token_str)
            ], limit=1)
            if dev_token_record:
                dev_token_record.write({'is_active': False})
                if not user:
                    user = dev_token_record.user_id

        # Ghi log đăng xuất
        self._record_login_history(
            user=user,
            email=user.login if user else '',
            device_token=dev_token_record,
            status='revoked',
            failure_reason='Người dùng chủ động đăng xuất khỏi app',
        )

        # Xóa session
        request.session.logout()

        return request.make_json_response({
            'code': 200,
            'message': 'Đăng xuất thành công'
        })
