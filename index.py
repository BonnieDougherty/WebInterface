#!/usr/bin/env python
# This new "shebang" line works better on Matt's machine

#############################################
#
#	METHODS FOR:
#	Opening/Creating Databases
#	Creating New Experiments
#	Viewing plates within experiments
#
#############################################

SCRIPT_NAME = "index.py"
N_PLATES = 8

import cgi
import cgitb
cgitb.enable()

from Database import Database
from HtmlTemplate import *

print "Content-Type: text/html\n\n"

inform = cgi.FieldStorage()
action = inform.getvalue("action",None)

# DONE show databases / new creation field
# DONE commit database
# DONE show experiments
# DONE new experiment field
# DONE commit experiment
# DONE display plates

# show plate

def link(action,text,**kwargs):
    addr = "index.py?action=" + action + "&"
    addr += "&".join([k+'='+cgi.escape(v) for k,v in kwargs.items()])
    return '<a href="{0}">{1}</a>'.format(addr,text)

def show_databases(): #Working
    print h2("Select a database:")
    
    dbs = Database.get_databases()
    print "<pre>"
    for db in dbs:
        print link("show_experiments",db,db=db)
    print "</pre>"
        
    form = Form(action=SCRIPT_NAME)
    form.add_hidden("action","create_db")
    form.add_text_field(name="name",caption="Database name:  ")
    form.add_submit("Create")
    print "<br><br>"
    print h2("Create a new database:")
    print form

def create_database():
    Database.create_new(inform.getvalue("name"))
    show_databases()

def show_experiments():
    dbname = inform.getvalue("db")
    print h2("Database:  " + dbname)
    print h2("Experiments")
    db = Database(dbname)
    exprs = db.get_experiments()
    headings = ("ID","Name","Date","Experimenter")
    link_f = lambda x: link("show_plates","[ {0} ]".format(str(x)),
                            db=dbname,experiment=str(x))
    display = (link_f,None,None,None)
    print table_from_tuples(exprs,headings,display=display)
    
    print h2("Create New Experiment")
    form = Form(action=SCRIPT_NAME,method="get")
    form.add_hidden("action","create_experiment")
    form.add_hidden("db",dbname)
    form.add_text_field("name","Name")
    form.add_return()
    form.add_text_field("experimenter","Experimenter")
    form.add_return()
    for i in range(1,N_PLATES+1):
        form.add_text_field("plateid","Plate ID  ")
        form.add_text_field("platename","  Plate Name  ")
        form.add_return()
    form.add_submit("Create")
    print form

def create_experiment():
    dbname = inform.getvalue("db")
    db = Database(dbname)
    exp_name = inform.getvalue("name","")
    experimenter = inform.getvalue("experimenter","")
    exp_id = db.add_experiment(name=exp_name,experimenter=experimenter)
    
    ids = inform.getlist("plateid")
    names = inform.getlist("platename")
    for pid,name in zip(ids,names):
        db.add_plate(exp_id,pid,name)
    
    show_experiments()
        
def show_plates():
    dbname = inform.getvalue("db")
    exp_id = inform.getvalue("experiment")
    db = Database(dbname)
    (exp_id,exp_name,exp_time,experimenter) = db.get_experiments(exp_id)
    plates = db.get_plates(exp_id)
    
    print h2("Experiment Summary")
    
    print """<pre>
    Experiment ID:  {0}
    Experiment Name:  {1}
    Start Time:  {2}
    Experimenter:  {3}
    </pre>""".format(exp_id,exp_name,exp_time,experimenter)
    
    print h2("Plates")
    headings = ("ID","Name")
    link_f = lambda x: ("<a href=show.py?db={0}&experiment={1}&plate={2}>" + 
                        "[ {2} ]</a>").format(dbname,exp_id,str(x))
    display = (link_f,None)
    print table_from_tuples(plates,headings,display=display)
    

if not action:
    show_databases()
elif action == "create_db":
    create_database()
elif action == "show_experiments":
    show_experiments()
elif action == "create_experiment":
    create_experiment()
elif action == "show_plates":
    show_plates()

if __name__ == '__main__':
    pass
