from flask import *
from WebApp import app, app_logger
from .forms import *
from .controls import *

import Setup
import PowerShell
import Overlord
import Cleanup
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
        trainer = setup.trainer.data
        trainees = setup.caches.data

        if Setup.ce500(trainer, trainees):
            app_logger.info("%s setup %s (trainer) and (trainees) %s" % (get_current_session_ip(), trainer, trainees))
            flash('CE setup successful for Trainer: "%s" and Caches: "%s"' %
                  (setup.trainer.data, setup.caches.data))
            return redirect(url_for('current'))
        else:
            flash("CE setup failed")
            return redirect(url_for('logs'))
    
    return render_template('setup.html', 
                           title='CE Setup',
                           form=setup)


@app.route('/setup/funds', methods=['GET', 'POST'])
def setup_funds():
    setup = SetupForm()
    
    if setup.validate_on_submit():
        cache_envs = setup.caches.data
        overlord_tag = setup.code.data

        if Setup.funds(cache_envs):
            app_logger.info("%s setup %s using Overlord tag %s" %
                            (get_current_session_ip(), cache_envs, overlord_tag))
            flash('Setup successful for: "%s"' %
                  cache_envs)
            return redirect(url_for('current'))
        else:
            flash('Setup failed for: "%s"' %
                  cache_envs)
            return redirect(url_for('logs'))
    
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
            interconnect = cleanup.caches.data
            for pair in cleanup.envs:
                if interconnect in pair:
                    cache = pair[1]

            if Cleanup.funds([(interconnect, cache)]):
                app_logger.info("%s cleaned up %s" % (get_current_session_ip(), cache))
                flash('Cleaned up %s' %
                      cache)
            else:
                flash("Failed to clean up %s" %
                      cache)
                return redirect(url_for('logs'))

        elif cleanup.clean_all.data:
            if Cleanup.funds(cleanup.envs):
                app_logger("%s cleaned up all cache environments for funds" % get_current_session_ip())
                flash('Cleaned up all Cache environments')
            else:
                flash('Failed to clean up all Cache environments')
                return redirect(url_for('logs'))

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
            app_logger.info("%s restarting Interconnect services" % get_current_session_ip())
            success = PowerShell.restart_services()

        elif form.stop_services.data:
            app_logger.info("%s stopping Interconnect services" % get_current_session_ip())
            success = PowerShell.stop_services()

        elif form.overlord.data:
            return redirect(url_for('overlord'))

        if success:
            flash("PowerShell successfully executed.")
            return redirect(url_for('current'))
        else:
            flash("Error executing PowerShell")
            return redirect(url_for('logs'))

    return render_template('utilities.html', 
                           title='Utilities',
                           form=form)


@app.route('/utilities/overlord', methods=['GET', 'POST'])
def overlord():    
    form = OverlordForm()
    
    if form.validate_on_submit():
        environments = form.envs.data
        tag = form.tag.data
        opt_vars = form.opt_vars.data

        if form.ce_diags.data:
            app_logger.info("%s running CSCDiag in %s" % (get_current_session_ip(), environments))
            success = Overlord.ce_diags(environments)

        else:
            app_logger.info("%s running %s in %s" % (get_current_session_ip(), tag, environments))
            success = Overlord.overlord(environments, tag, opt_vars)

        if success:
            flash('Overlord executed in %s' % environments)
            return redirect(url_for('current'))
        else:
            flash('Error executing Overlord in %s' % environments)
            return redirect(url_for('logs'))
    
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
                'Cleanup': Log.MyReader(name='Cleanup').read()}
    return render_template('logs.html',
                           title='Logs',
                           messages=messages)
