# -*- coding: utf-8 -*-

import json
import time
from datetime import date, datetime, time as datetime_time, timedelta

from odoo import fields


_CACHE = {}
_CACHE_TTL = 45
_WIDGET_ROW_LIMIT = 10


class ProjectDashboardService:
    def __init__(self, env):
        self.env = env
        self.Project = env['project.project'].sudo()
        self.Task = env['project.task'].sudo()
        self.Stage = env['project.task.type'].sudo()
        self.User = env['res.users'].sudo()
        self.Partner = env['res.partner'].sudo()

    def get_options(self, filters):
        return self._cached('options', filters, self._get_options)

    def get_summary(self, filters):
        return self._cached('summary', filters, lambda: self._get_summary(filters))

    def get_projects(self, filters):
        return self.get_project_progress(filters)

    def get_task_stage(self, filters):
        return self._cached('task_stage', filters, lambda: self._get_task_stage(filters))

    def get_task_trend(self, filters):
        return self._cached('task_trend', filters, lambda: self._get_task_trend(filters))

    def get_workload(self, filters):
        return self._cached('workload', filters, lambda: self._get_workload(filters))

    def get_project_progress(self, filters):
        return self._cached('project_progress', filters, lambda: self._get_project_progress(filters))

    def get_overdue(self, filters):
        return self._cached('overdue', filters, lambda: self._get_task_list(filters, 'overdue'))

    def get_testing(self, filters):
        return self._cached('testing', filters, lambda: self._get_task_list(filters, 'testing'))

    def get_not_live(self, filters):
        return self._cached('not_live', filters, lambda: self._get_task_list(filters, 'not_live'))

    def get_upcoming(self, filters):
        return self._cached('upcoming', filters, lambda: self._get_task_list(filters, 'upcoming'))

    def _cached(self, name, filters, callback):
        key = (self.env.uid, name, json.dumps(filters or {}, sort_keys=True, default=str))
        now = time.time()
        cached = _CACHE.get(key)
        if cached and now - cached['time'] < _CACHE_TTL:
            return cached['value']
        value = callback()
        _CACHE[key] = {'time': now, 'value': value}
        return value

    def _get_options(self):
        projects = self.Project.search_read([], ['name'], order='name', limit=2000)
        partners = self.Partner.search_read([('is_company', '=', True)], ['name'], order='name', limit=2000)
        users = self.User.search_read([('share', '=', False)], ['name'], order='name', limit=1000)
        stages = self._standard_stages()
        return {
            'projects': [{'id': item['id'], 'name': item['name']} for item in projects],
            'partners': [{'id': item['id'], 'name': item['name']} for item in partners],
            'users': [{'id': item['id'], 'name': item['name']} for item in users],
            'stages': [{'id': stage.id, 'name': stage.name} for stage in stages],
        }

    def _get_summary(self, filters):
        today = fields.Date.context_today(self.env.user)
        project_domain = self._project_domain(filters)
        task_domain = self._task_domain(filters)
        total_projects = self.Project.search_count(project_domain)
        total_tasks = self.Task.search_count(task_domain)
        done_tasks = self.Task.search_count(task_domain + [('stage_id.is_done', '=', True)])
        return {
            'total_projects': total_projects,
            'active_projects': self.Project.search_count(project_domain + [('active', '=', True)]),
            'done_projects': self._count_done_projects(project_domain),
            'overdue_projects': self.Project.search_count(project_domain + [('date', '<', today)]),
            'total_tasks': total_tasks,
            'done_tasks': done_tasks,
            'task_overdue': self.Task.search_count(task_domain + [('date_deadline', '<', today), ('stage_id.is_done', '=', False)]),
            'task_today': self.Task.search_count(task_domain + [('date_deadline', '=', today)]),
            'task_week': self.Task.search_count(task_domain + self._date_range_domain('date_deadline', *self._period_dates('this_week'))),
            'task_month': self.Task.search_count(task_domain + self._date_range_domain('date_deadline', *self._period_dates('this_month'))),
            'task_by_stage': self._read_group_count(self.Task, task_domain, 'stage_id'),
        }

    def _get_task_stage(self, filters):
        rows = self._read_group_count(self.Task, self._task_domain(filters), 'stage_id')
        counts = {item['id']: item['count'] for item in rows if item.get('id')}
        stages = self._standard_stages()
        data = [{'id': stage.id, 'name': stage.name, 'count': counts.get(stage.id, 0)} for stage in stages]
        total = sum(item['count'] for item in data) or 1
        for item in data:
            item['percent'] = round(item['count'] * 100 / total, 1)
        return data

    def _get_task_trend(self, filters):
        start, end = self._filter_dates(filters)
        if not start or not end:
            start, end = self._period_dates('30_days')
        days = []
        current = start
        while current <= end:
            days.append(current)
            current += timedelta(days=1)
        base_filters = dict(filters or {})
        base_filters['date_from'] = False
        base_filters['date_to'] = False
        task_domain = self._task_domain(base_filters)
        created = self._count_by_day(task_domain, 'create_date', days)
        done = self._count_by_day(task_domain + [('stage_id.is_done', '=', True)], 'write_date', days)
        overdue = self._count_by_day(task_domain + [('stage_id.is_done', '=', False)], 'date_deadline', days)
        return [{
            'date': item.isoformat(),
            'created': created.get(item, 0),
            'done': done.get(item, 0),
            'overdue': overdue.get(item, 0),
        } for item in days]

    def _get_workload(self, filters):
        task_domain = self._task_domain(filters)
        rows = self.Task.read_group(task_domain + [('user_ids', '!=', False)], ['user_ids'], ['user_ids'], lazy=False)
        users = self.User.browse([row['user_ids'][0] for row in rows if row.get('user_ids')])
        week_start, week_end = self._period_dates('this_week')
        today = fields.Date.context_today(self.env.user)
        data = []
        for user in users:
            domain = task_domain + [('user_ids', 'in', user.ids)]
            total = self.Task.search_count(domain)
            done = self.Task.search_count(domain + [('stage_id.is_done', '=', True)])
            data.append({
                'id': user.id,
                'name': user.name,
                'processing': self.Task.search_count(domain + [('stage_id.is_processing', '=', True)]),
                'testing': self.Task.search_count(domain + [('stage_id.is_test', '=', True)]),
                'done_week': self.Task.search_count(domain + [('stage_id.is_done', '=', True)] + self._date_range_domain('write_date', week_start, week_end)),
                'not_done': self.Task.search_count(domain + [('stage_id.is_done', '=', False)]),
                'overdue': self.Task.search_count(domain + [('date_deadline', '<', today), ('stage_id.is_done', '=', False)]),
                'total': total,
                'done': done,
                'done_percent': round(done * 100 / total, 1) if total else 0,
            })
        return sorted(data, key=lambda item: item['total'], reverse=True)[:_WIDGET_ROW_LIMIT]

    def _get_project_progress(self, filters):
        projects = self.Project.search(self._project_domain(filters), order='name', limit=2000)
        task_domain = self._task_domain(filters) + [('project_id', 'in', projects.ids)]
        rows = self.Task.read_group(task_domain, ['project_id', 'stage_id'], ['project_id', 'stage_id'], lazy=False)
        done_rows = self.Task.read_group(task_domain + [('stage_id.is_done', '=', True)], ['project_id'], ['project_id'], lazy=False)
        done_by_project = {row['project_id'][0]: self._group_count(row, 'project_id') for row in done_rows if row.get('project_id')}
        stages = self._standard_stages()
        counts = {}
        totals = {}
        for row in rows:
            project = row.get('project_id')
            stage = row.get('stage_id')
            if not project:
                continue
            project_id = project[0]
            totals[project_id] = totals.get(project_id, 0) + row['__count']
            if stage:
                counts.setdefault(project_id, {})[stage[0]] = row['__count']
        data = []
        for project in projects:
            total = totals.get(project.id, 0)
            done = done_by_project.get(project.id, 0)
            data.append({
                'id': project.id,
                'name': project.name,
                'pm': project.user_id.name if project.user_id else '',
                'deadline': fields.Date.to_string(project.date) if getattr(project, 'date', False) else '',
                'total_tasks': total,
                'done_tasks': done,
                'progress': round(done * 100 / total, 1) if total else 0,
                'stage_counts': [{'id': stage.id, 'name': stage.name, 'count': counts.get(project.id, {}).get(stage.id, 0)} for stage in stages],
            })
        return data

    def _get_task_list(self, filters, list_type):
        today = fields.Date.context_today(self.env.user)
        domain = self._task_domain(filters)
        if list_type == 'overdue':
            domain += [('date_deadline', '<', today), ('stage_id.is_done', '=', False)]
        elif list_type == 'testing':
            domain += [('stage_id.is_test', '=', True)]
        elif list_type == 'not_live':
            domain += [('stage_id.is_done', '=', True), ('stage_id.is_live', '=', False)]
        elif list_type == 'upcoming':
            domain += [('date_deadline', '>=', today), ('date_deadline', '<=', today + timedelta(days=3))]
        tasks = self.Task.search(domain, order='date_deadline asc, id desc', limit=_WIDGET_ROW_LIMIT)
        result = []
        for task in tasks:
            deadline = self._as_date(task.date_deadline)
            overdue_days = (today - deadline).days if deadline and deadline < today else 0
            result.append({
                'id': task.id,
                'name': task.name,
                'project': task.project_id.name if task.project_id else '',
                'users': ', '.join(task.user_ids.mapped('name')),
                'stage': task.stage_id.name if task.stage_id else '',
                'deadline': fields.Date.to_string(deadline) if deadline else '',
                'overdue_days': overdue_days,
            })
        return result

    def _project_domain(self, filters):
        filters = filters or {}
        domain = []
        for field_name, filter_name in [('id', 'project_ids'), ('partner_id', 'partner_ids'), ('user_id', 'pm_ids')]:
            ids = self._ids(filters.get(filter_name))
            if ids:
                domain.append((field_name, 'in', ids))
        if filters.get('stats_basis') == 'project_create':
            domain += self._date_range_domain('create_date', *self._filter_dates(filters))
        return domain

    def _task_domain(self, filters):
        filters = filters or {}
        domain = []
        mapping = [
            ('project_id', 'project_ids'),
            ('partner_id', 'partner_ids'),
            ('project_id.user_id', 'pm_ids'),
            ('user_ids', 'user_ids'),
            ('stage_id', 'stage_ids'),
        ]
        for field_name, filter_name in mapping:
            ids = self._ids(filters.get(filter_name))
            if ids:
                domain.append((field_name, 'in', ids))
        domain += self._date_range_domain(self._stats_field(filters.get('stats_basis')), *self._filter_dates(filters))
        return domain

    def _stats_field(self, stats_basis):
        return {
            'project_create': 'create_date',
            'task_create': 'create_date',
            'deadline': 'date_deadline',
            'completed': 'actual_finish_date',
            'live': 'write_date',
        }.get(stats_basis or 'task_create', 'create_date')

    def _filter_dates(self, filters):
        filters = filters or {}
        if filters.get('date_from') or filters.get('date_to'):
            return self._parse_date(filters.get('date_from')), self._parse_date(filters.get('date_to'))
        return self._period_dates(filters.get('period') or '30_days')

    def _period_dates(self, period):
        today = fields.Date.context_today(self.env.user)
        if period == 'today':
            return today, today
        if period == 'yesterday':
            day = today - timedelta(days=1)
            return day, day
        if period == '7_days':
            return today - timedelta(days=6), today
        if period == 'this_week':
            start = today - timedelta(days=today.weekday())
            return start, start + timedelta(days=6)
        if period == 'this_month':
            start = today.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            return start, next_month - timedelta(days=1)
        if period == 'this_quarter':
            month = ((today.month - 1) // 3) * 3 + 1
            start = today.replace(month=month, day=1)
            next_month = month + 3
            year = today.year + (1 if next_month > 12 else 0)
            next_month = next_month if next_month <= 12 else 1
            return start, date(year, next_month, 1) - timedelta(days=1)
        if period == 'this_year':
            return date(today.year, 1, 1), date(today.year, 12, 31)
        return today - timedelta(days=29), today

    def _date_range_domain(self, field_name, start, end):
        domain = []
        if start:
            domain.append((field_name, '>=', self._date_value(field_name, start, True)))
        if end:
            domain.append((field_name, '<=', self._date_value(field_name, end, False)))
        return domain

    def _date_value(self, field_name, value, is_start):
        if field_name in ('create_date', 'write_date', 'actual_finish_date'):
            return datetime.combine(value, datetime_time.min if is_start else datetime_time.max)
        return value

    def _parse_date(self, value):
        if not value:
            return False
        if isinstance(value, date):
            return value
        return fields.Date.from_string(value)

    def _as_date(self, value):
        if not value:
            return False
        if isinstance(value, datetime):
            return value.date()
        return value

    def _ids(self, value):
        if not value:
            return []
        if isinstance(value, str):
            value = value.split(',')
        return [int(item) for item in value if item]

    def _read_group_count(self, model, domain, groupby):
        rows = model.read_group(domain, [groupby], [groupby], lazy=False)
        data = []
        for row in rows:
            group = row.get(groupby)
            data.append({
                'id': group[0] if group else False,
                'name': group[1] if group else 'Không xác định',
                'count': row.get('%s_count' % groupby, row.get('__count', 0)),
            })
        return data

    def _standard_stages(self):
        stages = self.env['project.task.type']
        for xmlid in [
            'dcg_project_customize.task_stage_todo',
            'dcg_project_customize.task_stage_processing',
            'dcg_project_customize.task_stage_testing',
            'dcg_project_customize.task_stage_done',
            'dcg_project_customize.task_stage_live',
        ]:
            stage = self.env.ref(xmlid, raise_if_not_found=False)
            if stage:
                stages |= stage.sudo()
        return stages.sorted(lambda stage: (stage.sequence, stage.id))

    def _count_done_projects(self, project_domain):
        projects = self.Project.search(project_domain, limit=2000)
        if not projects:
            return 0
        total_rows = self.Task.read_group([('project_id', 'in', projects.ids)], ['project_id'], ['project_id'], lazy=False)
        done_rows = self.Task.read_group([('project_id', 'in', projects.ids), ('stage_id.is_done', '=', True)], ['project_id'], ['project_id'], lazy=False)
        totals = {row['project_id'][0]: self._group_count(row, 'project_id') for row in total_rows if row.get('project_id')}
        dones = {row['project_id'][0]: self._group_count(row, 'project_id') for row in done_rows if row.get('project_id')}
        return sum(1 for project_id, total in totals.items() if total and dones.get(project_id, 0) >= total)

    def _count_by_day(self, base_domain, field_name, days):
        return {
            day: self.Task.search_count(base_domain + self._date_range_domain(field_name, day, day))
            for day in days
        }

    def _group_count(self, row, groupby):
        return row.get('%s_count' % groupby, row.get('__count', 0))
