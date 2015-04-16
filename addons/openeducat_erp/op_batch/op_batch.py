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
import logging
import time
from datetime import timedelta

from dateutil.parser import parse

import openerp.tools as tools
from openerp import api
from openerp.osv import osv, fields


_logger = logging.getLogger(__name__)


class op_batch(osv.osv):
    _name = 'op.batch'

    _columns = {
        'code': fields.char(size=8, string='Code', required=False),
        'name': fields.char(size=255, string='Name', required=True),
        'start_date': fields.date(string='Start Date', required=False),
        'end_date': fields.date(string='End Date', required=False),
        'course_id': fields.many2one('op.course', string='Course', required=True),
        'fees': fields.float(string='Fees', required=False, default=0.0),
        'state': fields.selection([('d','En constitution'),('r','En cours'),('done','Terminée') ,('c','Annulée')],select=True, string='State'),
        'student_ids': fields.many2many('op.student', 'op_batch_student_rel', 'op_student_id', 'op_batch_id',
                                        string='Students'),
        'batch_invoiced_ids': fields.one2many('op.batch.invoiced', 'batch_id', String='Students', readonly=True),
        'customer_id': fields.many2one('res.partner', 'Partner', required=False, ondelete="cascade"),
        'invoice_id': fields.many2one('account.invoice', string='Invoice', required=False, readonly=True),


    }

    def onchange_student_ids(self, cr, uid, ids, student_ids, context=None):
        inv_batch_pool = self.pool.get('op.batch.invoiced')
        resolved_students = self.resolve_2many_commands(cr, uid, 'student_ids', student_ids, ['student_id'], context)
        # args = [('batch_id', '=', ids[0])]
        # inv_batches = inv_batch_pool.search(cr, uid,args, context=context)
        # for inv_batch_id in inv_batches:
        #     inv_batch =  inv_batch_pool.browse(cr, uid, inv_batch_id, context=context)[0]
        #     if inv_batch.invoice_id.id is False:
        #        inv_batch_pool.unlink(cr, uid, inv_batch_id, context=context)

        for student_id in resolved_students:
            args = [('student_id', '=', student_id['id']), ('batch_id', '=', ids[0])]
            inv_batch = inv_batch_pool.search(cr, uid, args, context=context)
            if (inv_batch is None or len(inv_batch) == 0):
                inv_batch_data = {
                    'student_id': student_id['id'],
                    'batch_id': ids[0]
                }

                inv_batch_pool.create(cr, uid, inv_batch_data, context=context)


    def create_invoice(self, cr, uid, ids, context={}):
        invoice_pool = self.pool.get('account.invoice')

        default_fields = invoice_pool.fields_get(cr, uid, context=context)
        invoice_default = invoice_pool.default_get(cr, uid, default_fields, context=context)
        for batch in self.browse(cr, uid, ids, context=context):
            onchange_partner = invoice_pool.onchange_partner_id(cr, uid, [], type='out_invoice', \
                                                                partner_id=batch.customer_id.id)
            invoice_default.update(onchange_partner['value'])
            due_date = batch.start_date
            due_date = parse(due_date) - timedelta(days=15)
            invoice_data = {
                'partner_id': batch.customer_id.id,
                'date_invoice': time.strftime('%Y-%m-%d'),
                'type': 'out_invoice',
                'date_due': due_date.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            }

            invoice_default.update(invoice_data)
            invoice_id = invoice_pool.create(cr, uid, invoice_default, context=context)
            invoice_line_pool = self.pool.get('account.invoice.line')
            tax_id = \
                self.pool.get('account.tax').search(cr, uid, [('type_tax_use', '=', 'sale'), ('sequence', '=', 2)])[
                    0]
            inv_line = {
                'price_unit': batch.fees * len(batch.student_ids),
                'quantity': 1,
                'name': 'Session ' + batch.name,
                'partner_id': batch.customer_id.id,
                'account_id': self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ',
                                                               'product.category', context=context).id,
                'invoice_id': invoice_id,
                'invoice_line_tax_id': [(6, 0, [tax_id])]
            }
            invoice_line_pool.create(cr, uid, inv_line, context=context)

            self.write(cr, uid, batch.id, {'invoice_id': invoice_id}, context=context)
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        tree_view = models_data.get_object_reference(cr, uid, 'account', 'invoice_tree')
        value = {
            'domain': str([('id', '=', invoice_id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': False,
            'views': [(form_view and form_view[1] or False, 'form'),
                      (tree_view and tree_view[1] or False, 'tree')],
            'type': 'ir.actions.act_window',
            'res_id': invoice_id,
            'target': 'current',
            'nodestroy': True
        }
        return value


op_batch()


class op_batch_invoiced(osv.osv):
    _name = 'op.batch.invoiced'
    _order = 'invoice_state'

    @api.depends('student_id.name', 'student_id.last_name')
    def _get_student_full_name(self):
        for record in self:
            record.student_full_name = record.student_id.name + ' ' + record.student_id.last_name

    @api.depends('invoice_id.date_due')
    def _get_invoice_due_date(self):
        for record in self:
            record.invoice_due_date = record.invoice_id.date_due

    @api.depends('invoice_id.state')
    def _get_invoice_state(self):
        for record in self:
            _logger.info("invoice is %s", record.invoice_id)
            if (record.invoice_id.id > 0):
                if record.invoice_id.state != 'paid':
                    record.invoice_state = 'Non payé'
                else:
                    record.invoice_state = 'Payé'
            else:
                record.invoice_state = 'Non facturé'

    _columns = {
        'batch_id': fields.many2one('op.batch', string='Batch', required=True, ondelete='restrict'),
        'student_id': fields.many2one('op.student', string='Student', required=True, ondelete='restrict'),
        'invoice_id': fields.many2one('account.invoice', string='Invoice', required=False),
        'student_full_name': fields.char(compute='_get_student_full_name',
                                         string='Nom complet',
                                         size=100),
        'invoice_due_date': fields.date(compute='_get_invoice_due_date', string='Date d\'échéance'),
        'invoice_state': fields.char(compute='_get_invoice_state', string='Etat de paiment', size=20)

    }


op_batch_invoiced()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
