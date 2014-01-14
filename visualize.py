
import string
import subprocess
import stat
import os

BASEPATH = os.path.realpath("cgi-bin") 
R_PATH = os.path.join(BASEPATH,"Rscripts")
GRAPHS_PATH = os.path.join(R_PATH,"graphs")

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
		splitData = string.split(row[2],',D,')
		null_data = string.lstrip(splitData[0],'N,')
		read_data = splitData[1]
		# Write to file
		temp_file.write( str(row[1]) + ',1,' + null_data + '\n' ) 
		temp_file.write( str(row[1]) + ',0,' + read_data + '\n' )
	
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
	r_script_path = os.path.join(R_PATH,"completePlateProcess.R")
	
	if not os.path.exists(plotStoreDir):
		os.makedirs(plotStoreDir)
		os.chmod(plotStoreDir, stat.S_IWRITE)
		os.chmod(plotStoreDir, stat.S_IRWXO)
		os.chmod(plotStoreDir, stat.S_IRWXU)
		retcode = subprocess.call(["Rscript",r_script_path,temp_data_file_path,plotStoreDir])
		if retcode != 0:
			os.rmdir(plotStoreDir)
	return plotStoreDir
	
	