"""Route declaration."""
from flask import current_app as app
from flask import render_template, request, flash
from flask import Flask
from webplay import get_programs, play_program
import os
app = Flask(__name__, template_folder='templates', static_folder='static')
LINK="https://www.webplay.com"
app.secret_key = os.urandom(20)

##
## HOME
##

@app.route('/', defaults={'tid': 0},methods = ['POST', 'GET'])
@app.route('/<int:tid>', methods = ['POST', 'GET'])
def home(tid):
    ##
    ## GET ARGS
    ##
    video_link=False
    search=False
    search=request.form.get('search',False)
    livestream=request.form.get('livestream',False)
    if 'search' in request.args:
        search=request.args.get('search', False)
    if 'livestream' in request.args:
        livestream=request.args.get('livestream',False)
    if '/video?id' in request.args:
        video_link='/video?id='+request.args.get('/video?id')+'&lang='+request.args.get('lang')
    ##
    ## GET PROGRAMS
    ##
    programs=get_programs(tid, search)
    if len(programs['programs'])==0:
        if search:
            flash(u'No programs found in your search', 'info')
    ##
    ## Play Video
    ##
    if video_link:
        status, message=play_program(video_link)
        if status==False:
            flash(message, 'warning')
        else:
            flash(message, 'success')

    ##
    ## Play Livestream
    ##
    if livestream:
        print("LIVESTREAM=", programs['live'])
        status, message=play_program(programs['live'])
        if status==False:
            flash(message, 'warning')
        else:
            flash(message, 'success')

    ##
    ## Render Page
    ##
    nav=[]
    cnt=0
    for theme in programs['themes']:
        cnt+=1
        ACTIVE=""
        if cnt==tid:
            ACTIVE="active"
        nav.append({'name': theme, 'url': '/'+str(cnt), 'active': ACTIVE})

    if programs['live']:
        ACTIVE=""
        if livestream:
           ACTIVE="active"
        nav.append({'name': 'Live stream now', 'url': '/?livestream=1', 'active': ACTIVE})
        if not livestream:
            flash(u'live stream is active!', 'primary')

    return render_template('home.html',
                           nav=nav,
                           title="Webplay Web App",
                           description="Smarter page templates with Flask.", programs=programs['programs'], 
                           tid=tid, link=LINK, search=search)

##
## MAIN
##
if __name__ == "__main__":
    app.run(host="0.0.0.0")

##
## EOF
##
