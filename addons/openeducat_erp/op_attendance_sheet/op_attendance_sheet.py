# -*- coding: utf-8 -*-
# /#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# /#############################################################################
import logging
from openerp.osv import osv, fields

_logger = logging.getLogger(__name__)


class op_attendance_sheet(osv.osv):
    _name = 'op.attendance.sheet'

    def _total_present(self, cr, uid, ids, name, arg, context=None):
        res = {}

        for sheet in self.browse(cr, uid, ids, context):
            present_cnt = 0
            for line in sheet.attendance_line:

                if line.present == True:
                    present_cnt = present_cnt + 1
            res[sheet.id] = present_cnt
        return res

    def _total_absent(self, cr, uid, ids, name, arg, context=None):
        res = {}

        for sheet in self.browse(cr, uid, ids, context):
            absent_cnt = 0
            for line in sheet.attendance_line:
                if line.present == False:
                    absent_cnt = absent_cnt + 1
            res[sheet.id] = absent_cnt
        return res

    def fill_in_sheet(self, cr, uid, ids, context={}):
        for attend_sheet in self.browse(cr, uid, ids, context=context):
            if len(attend_sheet.attendance_line) == 0:
                batch_id = attend_sheet.register_id.batch_id
                student_ids = batch_id.student_ids
                for student_id in student_ids:
                    self.create_attendance_line(cr, uid, ids, student_id, context=context)

    def create_attendance_line(self, cr, uid, ids, student_id, context=None):
        _logger.info("create attendance line for %s", student_id)
        attendance_line_pool = self.pool.get('op.attendance.line')
        _logger.info("attendance line pool %s", attendance_line_pool)
        new_attendance_line = {
                        'student_id': student_id['id'],
                        'attendance_id': ids[0],
                    }
        attendance_line_pool.create(cr, uid, new_attendance_line, context=context)



    _columns = {
        'name': fields.char(size=8, string='Name'),
        'register_id': fields.many2one('op.attendance.register', string='Register', required=True),
        'attendance_date': fields.date(string='Date', required=True),
        'attendance_line': fields.one2many('op.attendance.line', 'attendance_id', string='Attendance Line', required=True),
        'total_present': fields.function(_total_present, string='Total Present', type='integer', method=True),
        'total_absent': fields.function(_total_absent, string='Total Absent', type='integer', method=True),
        'teacher_id': fields.many2one('op.faculty', string='Teacher'),
    }

op_attendance_sheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
