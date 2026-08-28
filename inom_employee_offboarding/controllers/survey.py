# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey


class OffboardingSurvey(Survey):

    @http.route()
    def survey_retry(self, survey_token, answer_token, **post):
        """Chặn làm lại khảo sát phỏng vấn nghỉ việc.

        Với khảo sát ``is_exit_interview`` đã hoàn thành, không cho tạo lượt
        trả lời mới. Điều hướng về trang kết quả của lượt trả lời hiện tại thay
        vì tạo ``survey.user_input`` mới.
        """
        access_data = self._get_access_data(
            survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is True:
            survey_sudo = access_data['survey_sudo']
            answer_sudo = access_data['answer_sudo']
            if survey_sudo.is_exit_interview and answer_sudo \
                    and answer_sudo.state == 'done':
                return request.redirect(
                    '/survey/start/%s?answer_token=%s' % (
                        survey_sudo.access_token, answer_sudo.access_token))
        return super().survey_retry(survey_token, answer_token, **post)
