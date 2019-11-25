from odoo import api, fields, models, _
import time

SESSION_STATES =[('draft','Draft'),('confirmed','Confirmed'),
                ('done','Done')]

class session(models.Model):
        _name = 'academic.session'
        
        name = fields.Char("Name", required=True,
                                readonly=True, states={'draft': [('readonly', False)]} 
        )

        course_id = fields.Many2one(comodel_name="academic.course",string="Course", required=True, 
                                readonly=True, states={'draft': [('readonly', False)]} )

        instructor_id = fields.Many2one(comodel_name="res.partner",string="Instructor", required=True, 
                                readonly=True, states={'draft': [('readonly', False)]} )

        start_date = fields.Date(string="Start Date", required=False, 
                        default=lambda self: time.strftime("%Y-%m-%d"), 
                        readonly=True, states={'draft': [('readonly', False)]} )

        duration = fields.Integer(string="Duration", required=False, 
                                readonly=True, states={'draft': [('readonly', False)]} )

        seats = fields.Integer(string="Seats", required=False, 
                                readonly=True, states={'draft': [('readonly', False)]} )

        active = fields.Boolean(string="Active", default=True, 
                                readonly=True, states={'draft': [('readonly', False)]} )

        attendee_ids = fields.One2many(comodel_name="academic.attendee",
                                        inverse_name="session_id",
                                        string="Attendees",
                                        required=False, 
                                        readonly=True, states={'draft': [('readonly', False)]} )

        taken_seats = fields.Float(compute="_calc_taken_seats",
                                        string="Taken Seat", required=False, 
                                        readonly=True, states={'draft': [('readonly', False)]} )
        
        image_small = fields.Binary("Image", attachment=True,
                                readonly=True, states={'draft': [('readonly', False)]} )

        state = fields.Selection(string="State", selection=SESSION_STATES,
                                        required=True,
                                        readonly=True,
                                        default=SESSION_STATES[0][0])


        @api.multi
        def action_draft(self):
                self.state = SESSION_STATES[0][0]
        
        @api.multi
        def action_confirm(self):
                self.state = SESSION_STATES[1][0]
        @api.multi
        def action_done(self):
                self.state = SESSION_STATES[2][0]

        @api.depends('attendee_ids','seats')
        def _calc_taken_seats(self):
                for x in self:
                        if x.seats > 0:
                                x.taken_seats = 100.0 * len(x.attendee_ids) / x.seats
                        else:
                                x.taken_seats = 0.0


        @api.onchange('seats')
        def onchange_seats(self):
                if self.seats>0:
                        self.taken_seats = 100.0 * len(self.attendee_ids)/self.seats
                else:
                        self.taken_seats = 0.0

        @api.multi
        def _cek_instruktur(self):
                for session in self:

                        # for attende in session.attendee_ids:
                        #         x.append( attendee.partner_id.id)

                        x=[attendee.partner_id.id for attendee in session.attendee_ids]
                        if session.instructor_id.id in x:
                                return False

                return True     

        _constraints = [(_cek_instruktur, 
                        'instruktur tidak bisa jadi attende(peserta)',
                        ['instructor_id', 'attendee_ids'])]

        @api.multi
        def copy(self, default=None):
                self.ensure_one()
                default = dict(default or {},
                               name=_('Copy of %s') % self.name)
                return super(session, self).copy(default=default)

        
       
        


                