from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

import MyTrack


class SetupForm(Form):  # only one field can have validators?
    trainer = StringField('trainer')
    caches = TextAreaField('caches', validators=[DataRequired()])
    code = StringField('code')


class SetupChoiceForm(Form):
    ce = SubmitField('Care Everywhere')
    funds = SubmitField('AMB/IP Funds')


class CleanupForm(Form):
    envs = [pairs for pairs in MyTrack.get_assigned("AMB_IP")]
    caches = SelectField(choices=envs)
    clean_one = SubmitField('Cleanup')
    clean_all = SubmitField('Cleanup All')


class UtilityForm(Form):
    stop_services = SubmitField('Stop Services')
    restart_services = SubmitField('Restart Services')
    overlord = SubmitField('Overlord')


class OverlordForm(Form):
    tag = StringField('tag')  # , validators=[DataRequired()])
    opt_vars = StringField('opt_vars')
    envs = TextAreaField('caches', validators=[DataRequired()])

    # Pre-set tags
    ce_diags = SubmitField("CE Diags")
    ce_gateway_config = SubmitField("CE GatewayConfig")

# # # #
