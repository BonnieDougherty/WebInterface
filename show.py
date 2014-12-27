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
from numpy import genfromtxt

# set HOME environment variable to a directory the httpd server can write to
os.environ['MPLCONFIGDIR'] = '/home/pi/matplotlib'
import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt

print "Content-Type: text/html\n\n"

# Retreive info about experiment/plate from URL (GET statement)
form = cgi.FieldStorage()
# Create link to the correct database and retrieve info
db = Database(form.getvalue("db"))

try:
	data_from_db = db.get_data(experiment=form.getvalue("experiment"),plate=form.getvalue("plate"),resistance="01") 
	
	try:
		# Create temp data file
		temp_data_file = createTempCSV(data_from_db,form.getvalue("db"),form.getvalue("experiment"),form.getvalue("plate"))
		
		# Run script to create graphs
		# 1st line just in case generatePlots throws errors
		#plotStoreDir = os.path.join(GRAPHS_PATH,"d" + form.getvalue("db") + "e" + form.getvalue("experiment") + "p" + form.getvalue("plate"))		
		plotStoreDir = generatePlots(form.getvalue("db"),form.getvalue("experiment"),form.getvalue("plate"),temp_data_file)

		# Delete temp data file
		os.remove(temp_data_file)
	except:
		print "<b>There was a problem with the data format</b></br>\n"
     
	print h2("Data Retrieval complete:")
	print """
	<pre>
		Database: {0}
		Experiment: {1}
		Plate: {2}\n
	""".format(form.getvalue("db"),
		form.getvalue("experiment"),
			form.getvalue("plate") )

	print "<center>"
	plateImage = os.path.join(plotStoreDir,"plate.png")
	if os.path.exists(plateImage):
		print image(plateImage,600)
		#print tableFromImageDir(plotStoreDir)
	else:
		print "<b>Plots not available</b>"
	print "</center>\n"

	#data_from_db = db.get_data(experiment=form.getvalue("experiment"),plate=form.getvalue("plate") )  
	#headings = ("Plate","Time","Resistor","Data")
	#print table_from_tuples(data_from_db,headings)

	db.close()
	
except:
	print "<b>There was a problem with the database</b></br>\n"
