#!/usr/bin/env python
# This new "shebang" line works better on Matt's machine

#############################################
#
#	METHODS FOR ENTERING DATA INTO 
#	DATABASES VIA URL"GET" PAMETERS	
#
#############################################

import cgi
import cgitb
cgitb.enable()

from Database import Database

print "Content-Type: text/html\n\n"

form = cgi.FieldStorage()

db = Database(form.getvalue("db"))
db.add_data(experiment=form.getvalue("experiment"),
	plate=form.getvalue("plate"),
	time=form.getvalue("time"),     
	data=form.getvalue("data"))  	

db.close()

# "time" refers to the number of milliseconds from the experiment start
# that the data was gathered

print """
<pre><b>Insert complete:</b>
     Database: {0}
   Experiment: {1}
        Plate: {2}
	 Time: {3}
         Data: {4}</pre>
""".format(form.getvalue("db"),form.getvalue("experiment"),
       form.getvalue("plate"),
	   form.getvalue("time"),
       form.getvalue("data"))

cgi.print_form(form)

