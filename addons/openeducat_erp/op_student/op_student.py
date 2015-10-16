# -*- coding: utf-8 -*-
# /#############################################################################
#
# Tech-Receptives Solutions Pvt. Ltd.
# Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
import string
import time, re
import logging

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import timedelta
import openerp.tools as tools
from dateutil.parser import parse

_logger = logging.getLogger(__name__)

class op_student(osv.osv):
    _name = 'op.student'
    _inherits = {'res.partner': 'partner_id'}

    def _get_curr_roll_number(self, cr, uid, ids, fields, arg, context=None):
        ret_val = {}
        for self_obj in self.browse(cr, uid, ids, context=context):
            roll_no = 0
            seq = 0
            for roll_number in self_obj.roll_number_line:
                if roll_number.standard_id.sequence > seq:
                    roll_no = roll_number.roll_number
                    seq = roll_number.standard_id.sequence
            ret_val[self_obj.id] = roll_no

        return ret_val

    def _get_roll(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('op.roll.number').browse(cr, uid, ids, context=context):
            result[line.student_id.id] = True
        return result.keys()

    def  ValidateEmail(self, cr, uid, ids, email, context=None):
        if email is not None and isinstance(email, basestring) :
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
                return True
            else:
                raise osv.except_osv('Email Invalide', 'Veuillez entrer un compte email valide!')

    def write(self, cr, uid, ids, vals, context=None):
        _logger.info("student value is %s", vals)
        batch_pool = self.pool.get('op.batch')
        for student in self.browse(cr, uid, ids, context=context):
            vals['name'] = student.first_name + " " + student.last_name
            batch_ids = student.batch_ids
            for batch_id in batch_ids:
                batch = batch_pool.browse(cr, uid, batch_id, context=context)[0]
                batch.create_invoiced_batches(cr, uid, batch_id, ids, 1, context=context)

        res = super(op_student, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        _logger.info("student value is %s", vals)
        vals['name'] = vals['first_name'] + " " + vals['last_name']
        res = super(op_student, self).create(cr, uid, vals, context=context)
        return res

    _columns = {
        'middle_name': fields.char(size=128, string='Middle Name', required=False),
        'last_name': fields.char(size=128, string='Last Name', required=True),
        'first_name': fields.char(size=128, string='First Name', required=True),
        'email': fields.char(size=256, string='Email', required=True),
        'birth_date': fields.date(string='Birth Date', required=False),
        'blood_group': fields.selection(
            [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'), ('A-', 'A-ve'), ('B-', 'B-ve'),
             ('O-', 'O-ve'), ('AB-', 'AB-ve')], string='Blood Group'),
        'gender': fields.selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender', required=True),
        'nationality': fields.many2one('res.country', string='Nationality'),
        'language': fields.many2one('res.lang', string='Mother Tongue'),
        'category': fields.many2one('op.category', string='Category', required=False),
        'religion': fields.many2one('op.religion', string='Religion'),
        'library_card': fields.char(size=64, string='Library Card'),
        'emergency_contact': fields.many2one('res.partner', string='Emergency Contact'),
        'pan_card': fields.char(size=64, string='PAN Card'),
        'bank_acc_num': fields.char(size=64, string='Bank Acc Number'),
        'visa_info': fields.char(size=64, string='Visa Info'),
        'id_number': fields.char(size=64, string='ID Card Number'),
        'photo': fields.binary(string='Photo'),
        'division_id': fields.many2one('op.division', string='Division'),
        'batch_ids': fields.many2many('op.batch', 'op_batch_student_rel', 'op_batch_id', 'op_student_id',
                                      string='Batch'),
        'roll_number_line': fields.one2many('op.roll.number', 'student_id', 'Roll Number'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete="cascade"),
        'health_lines': fields.one2many('op.health', 'student_id', 'Health Detail'),
        'roll_number': fields.function(_get_curr_roll_number,
                                       method=True,
                                       string='Current Roll Number',
                                       type='char',
                                       size=8,
                                       store={
                                           'op.roll.number': (_get_roll, [], 10),
                                       }),
        'allocation_ids': fields.many2many('op.assignment', 'op_student_assignment_rel', 'op_student_id',
                                           'op_assignment_id', string='Assignment'),
        'alumni_boolean': fields.boolean('Alumni Student'),
        'passing_year': fields.many2one('op.batch', string='Passing Year'),
        'current_position': fields.char(string='Current Position', size=256),
        'current_job': fields.char(string='Current Job', size=256),
        'phone': fields.char(string='Phone Number', size=256),
        'user_id': fields.many2one('res.users', 'User'),
        'placement_line': fields.one2many('op.placement.offer', 'student_id', 'Placement Details'),
        'activity_log': fields.one2many('op.activity', 'student_id', 'Activity Log'),
        'parent_ids': fields.many2many('op.parent', 'op_parent_student_rel', 'op_parent_id', 'op_student_id',
                                       string='Parent'),
        'gr_no': fields.char(string="GR Number", size=20),
        'batch_invoiced_ids': fields.one2many('op.batch.invoiced', 'student_id', 'Invoiced batches'),
    }






op_student()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
