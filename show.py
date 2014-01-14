#!/usr/bin/env python

#############################################
#
#	METHODS FOR VIEWING DATA FROM
# 	EXISTING EXPERIMENTS
#
#############################################

SCRIPT_NAME = "show.py"

import cgi
import cgitb
cgitb.enable()

from Database import Database
from HtmlTemplate import *
from visualize import *

print "Content-Type: text/html\n\n"

# Retreive info about experiment/plate from URL (GET statement)
form = cgi.FieldStorage()
# Create link to the correct database and retrieve info
db = Database(form.getvalue("db"))

try:
	data_from_db = db.get_data(experiment=form.getvalue("experiment"),plate=form.getvalue("plate") )  
	#data_rows = data_from_db.fetchall()
	
	#plotStorageDir = ""
	#temp_data_file = ""

        """
	try:
		# Create temp data file
		temp_data_file = createTempCSV(data_rows,form.getvalue("db"),form.getvalue("experiment"),form.getvalue("plate"))

		# Run R script to create graphs/plots if they don't already exist
		#plotStorageDir = generatePlots(form.getvalue("db"),form.getvalue("experiment"),form.getvalue("plate"),temp_data_file)

		# Delete temp data file
		#os.remove(temp_data_file)
	except:
		print "<b>There was a problem with the data format</b></br>\n"
        """	
     
	print h2("Data Retrieval complete:")
	print """
	<pre>
		Database: {0}
		Experiment: {1}
		Plate: {2}
		Data:</pre>\n
	""".format(form.getvalue("db"),
		form.getvalue("experiment"),
			form.getvalue("plate") )

	print "<center>"
	plateImage = os.path.join(plotStorageDir,"plate.jpg")
	if os.path.exists(plateImage):
		print image(plateImage,600)
		print tableFromImageDir(plotStorageDir)
	else:
		print "<b>Plots not available</b>"
	print "</center>\n"

	#data_from_db = db.get_data(experiment=form.getvalue("experiment"),plate=form.getvalue("plate") )  
	#headings = ("Plate","Time","Data")
	#print table_from_tuples(data_from_db,headings)

	#cgi.print_form(form)

	db.close()
	
except:
	print "<b>There was a problem with the database</b></br>\n"
