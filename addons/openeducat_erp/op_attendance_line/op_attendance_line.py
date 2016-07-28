# -*- coding: utf-8 -*-
#/#############################################################################
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
#/#############################################################################
from openerp.osv import osv, fields

class op_attendance_line(osv.osv):
    _name = 'op.attendance.line'
    _rec_name = 'attendance_id'

    _columns = {
            'attendance_id': fields.many2one('op.attendance.sheet', string='Attendance', required=True),
            'student_id': fields.many2one('op.student', string='Student', required=True),
            'present': fields.boolean(string='Present ?'),
            'remark': fields.char(size=256, string="Remark")
    }

op_attendance_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
