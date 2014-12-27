
import string
import subprocess
import stat
import os

BASEPATH = os.path.realpath("/home/pi") 
R_PATH = os.path.join(BASEPATH,"Rscripts")
GRAPHS_PATH = os.path.join(R_PATH,"graphs")

import numpy
from numpy import genfromtxt

# set HOME environment variable to a directory the httpd sever can write to
os.environ['MPLCONFIGDIR'] = '/home/pi/matplotlib'
import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt

#############################################
#
#		SUBROUTINES FOR FILE CREATION
#
#############################################

# Create temporary CSV file with data in correct format for the R script
def createTempCSV(data,database_name,experiment,plate):
	# Create new file
	file_name = 'd' + database_name + 'e' + experiment + 'p' + plate + '.csv'
	file_path_name = os.path.join(R_PATH,"tempData",file_name)
        temp_file = open(file_path_name,'w+')
	
	# Read from database and format for file
	for row in data:
                plateID = row[0]
                time = row[1]
                resistance = row[2]
                data = row[3]
		# Write to file
		temp_file.write(plateID+','+time+','+resistance+data+'\n')
	
	# Close file
	temp_file.close()
	return file_path_name
	
	
#############################################
#
#	   METHODS FOR VISUALIZING DATA 
#
#############################################

# Run R script to generate plots
def generatePlots(database_name,experiment,plate,temp_data_file_path):
	plotStoreDir = os.path.join(GRAPHS_PATH, "d" + database_name + "e" + experiment + "p" + plate)
	#r_script_path = os.path.join(R_PATH,"completePlateProcess.R")
	
	if not os.path.exists(plotStoreDir):
		os.makedirs(plotStoreDir)
		os.chmod(plotStoreDir, stat.S_IWRITE)
		os.chmod(plotStoreDir, stat.S_IRWXO)
		os.chmod(plotStoreDir, stat.S_IRWXU)
	#	retcode = subprocess.call(["Rscript",r_script_path,temp_data_file_path,plotStoreDir])
	#	if retcode != 0:
	#		os.rmdir(plotStoreDir)
	
	my_data = genfromtxt(temp_data_file_path,delimiter=',')
	
	# Generate 96 figures, one figure for each well
	# HARD TO SEE ALL PLOTS, LOOK AT INCREASING LINE THICKNESS
	#for well in range(96):
	#	f,ax = plt.subplots()
	#	ax.plot(my_data[:,1],my_data[:,3],'k*-')
	#	save_file = os.path.join(plotStoreDir,"well"+str(well))
	#	plt.savefig(save_file+".png")
	#	plt.close(f)

	# Generate 1 figure, with 96 subplots
	#font = {'family':'normal', 'weight':'bold','size':10}
	#matplotlib.rc('font',**font)
	matplotlib.rc('xtick',labelsize=2)
	matplotlib.rc('ytick',labelsize=2)
	plt.figure(1)
	plt.subplot(8,12,1)
	upper = numpy.amax(my_data[:,3:])
	lower = numpy.amin(my_data[:,3:])
	
	# Correct for time
	my_data[:,1] = my_data[:,1] - my_data[1,1]
	for j in range(8):
		for i in range(12):
			plt.subplot(8,12,12*j+i+1)
			plt.plot(my_data[:,1],my_data[:,12*j+i+3],'k-')
	save_file = os.path.join(plotStoreDir,"plate")
	plt.savefig(save_file+".png")
	plt.close()
	return plotStoreDir
	
	
