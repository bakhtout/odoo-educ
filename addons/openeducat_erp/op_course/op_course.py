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

class op_course(osv.osv):
    _name = 'op.course'

    _columns = {
            'name': fields.char(size=255, string='Name', required=True),
            'code': fields.char(size=8, string='Code', required=False),
            'coefficient' : fields.integer(string='Coefficient'),
            'category': fields.selection([('F', 'Formation'), ('AA', 'Ateliers adultes'), ('AE', 'Ateliers enfants')], string='Catégorie', required=True),
            'course_type': fields.selection([('S', 'Standard'), ('PM', 'Aprés midi'), ('EV', 'Soirée')], string='Type de cours', required=True),
            'parent_course' : fields.many2one('op.course', 'Cours parent'),
            'section': fields.char(size=32, string='Section', required=False),
            'evaluation_type': fields.selection([('normal','Normal'),('GPA','GPA'),('CWA','CWA'),('CCE','CCE')], string='Evaluation Type', required=False),
            'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
            'subject_ids': fields.many2many('op.subject', 'op_course_subject_rel', 'op_course_id', 'op_subject_id', string='Subject(s)'),
    }

op_course()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
