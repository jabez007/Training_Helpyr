from flask import *
from WebApp import app
from .forms import *
from .controls import *

import Setup
import PowerShell
import Overlord
import Log


@app.before_request
def using():
    if request.endpoint:
        if any(endpoint in request.endpoint for endpoint in ['setup','cleanup','utilities','overlord']):
            if check_in_use():
                flash(Markup('This utility is currently in use by <a href="http://guru/Tools.aspx">%s</a>' % get_in_use_ip()))
                return redirect(url_for("current"))
            else:
                set_in_use()
        else:
            remove_in_use()


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html",
                           title='Home')


####
# Current Environments
####
@app.route('/current')
def current():
    envs = PowerShell.get_webapplications()
    return render_template("current.html",
                           title='Current',
                           environments=envs)


####
# Setup new environments
####
@app.route('/setup', methods=['GET', 'POST'])
def choose_setup():
    choose = SetupChoiceForm()
    
    if choose.validate_on_submit():
        if choose.ce.data:
            return redirect(url_for('setup_ce'))
        elif choose.funds.data:
            return redirect(url_for('setup_funds'))
    
    return render_template('choose_setup.html', 
                           title='Setup',
                           form=choose)


@app.route('/setup/ce', methods=['GET', 'POST'])
def setup_ce():    
    setup = SetupForm()
    
    if setup.validate_on_submit():
        flash('Setup requested for Trainer: "%s" and Caches: "%s"' %
              (setup.trainer.data, setup.caches.data))
        return redirect(url_for('current'))
    
    return render_template('setup.html', 
                           title='CE Setup',
                           form=setup)


@app.route('/setup/funds', methods=['GET', 'POST'])
def setup_funds():
    setup = SetupForm()
    
    if setup.validate_on_submit():
        flash('Setup requested for Caches: "%s"' %
              setup.caches.data)
        return redirect(url_for('current'))
    
    return render_template('setup.html', 
                           title='Funds Setup',
                           form=setup)


####
# Cleanup Existing environments
####
@app.route('/cleanup', methods=['GET', 'POST'])
def choose_cleanup():    
    choose = SetupChoiceForm()
    
    if choose.validate_on_submit():
        if choose.ce.data:
            return redirect(url_for('cleanup_ce'))
        elif choose.funds.data:
            return redirect(url_for('cleanup_funds'))
    
    return render_template('choose_setup.html', 
                           title='Cleanup',
                           form=choose)


@app.route('/cleanup/ce', methods=['GET', 'POST'])
def cleanup_ce():    
    cleanup = CleanupForm()
    
    if cleanup.is_submitted():
        flash('Cleaning up CE class')
        return redirect(url_for('current'))
    
    return render_template('cleanup.html', 
                           title='CE Cleanup',
                           form=cleanup)


@app.route('/cleanup/funds', methods=['GET', 'POST'])
def cleanup_funds():    
    cleanup = CleanupForm()
    
    if cleanup.validate_on_submit():
        if cleanup.clean_one.data:
            flash('Cleaning up epic-trn%s' %
                  cleanup.caches.data)
        elif cleanup.clean_all.data:
            flash('Cleaning up all Cache environments')
        return redirect(url_for('current'))
    
    return render_template('cleanup.html', 
                           title='Funds Cleanup',
                           form=cleanup)


####
# Utilities
####
@app.route('/utilities', methods=['GET', 'POST'])
def utilities():    
    form = UtilityForm()
    
    if form.validate_on_submit():
        if form.restart_services.data:
            flash('Restarted Services')
            PowerShell.restart_services()

        elif form.stop_services.data:
            flash('Stopped Services')
            PowerShell.stop_services()

        elif form.overlord.data:
            return redirect(url_for('overlord'))
        
        return redirect(url_for('current'))
    
    return render_template('utilities.html', 
                           title='Utilities',
                           form=form)


@app.route('/utilities/overlord', methods=['GET', 'POST'])
def overlord():    
    form = OverlordForm()
    
    if form.validate_on_submit():
        environments = form.envs.data

        # if form.ce_diags.data:
            # Overlord.ce_diags()

        flash('Overlord executed in %s' % environments)

        return redirect(url_for('current'))
    
    return render_template('overlord.html', 
                           title='Overlord',
                           form=form)


####
# Logs
####
@app.route('/logs')
def logs():
    messages = {'Setup': Log.MyReader(name='Setup').read(),
                'PowerShell': Log.MyReader(name='PowerShell').read(),
                'Overlord': Log.MyReader(name='Overlord').read(),
                'Phonebook': Log.MyReader(name='Phonebook').read(),
                'Cleanup': Log.MyReader(name='Cleanup')}
    return render_template('logs.html',
                           title='Logs',
                           messages=messages)
