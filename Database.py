#############################################
#
#	METHODS FOR INTERFACING WITH 
#	SQLITE DATABASES
#
#############################################

import sqlite3 as sqlite
import os
import glob
# The glob module finds all pathnames matching a specified pattern

BASE_CGI_PATH = os.path.realpath("/media/usbhdd")
DB_PATH = os.path.join(BASE_CGI_PATH,"databases")

CREATE_EXPERIMENTS_TABLE = """
    CREATE TABLE experiments(
        id INTEGER PRIMARY KEY,
        name TEXT,
        start TEXT,
        experimenter TEXT )
"""

CREATE_PLATES_TABLE = """
    CREATE TABLE {0}(
        id TEXT,
        name TEXT )
"""

CREATE_DATA_TABLE = """
    CREATE TABLE {0}(
        plate TEXT,
	time TEXT,
        resistance TEXT,
        data TEXT )
"""

def plate_table_name(experiment):
    return "PLATE__" + str(experiment)

def data_table_name(experiment):
    return "DATA__" + str(experiment)

def to_string(tup):
    return [str(x) for x in tup]

# Class is inheriting from the object class
class Database(object):
    # Class instantiation automatically invokes this function, takes one argument
    # Self is an instance of the class
    def __init__(self,dbname): # Can include dbname as input 
        # self.dbname = dbname
        # specify the database name - create a connection object that represents the database
        #os.path.join() joins the database path between the web server and plate reader aspects
        self.connection = sqlite.connect(os.path.join(DB_PATH,dbname + ".db"))
        #self.connection = sqlite.connect('PlateReader.db')
        # Creates a cursor to navigate the dictionary.
        # Call cursor methods to perform SQL commands. 
        self.cursor = self.connection.cursor()
        
    def close(self):
        # release resources
        self.cursor.close()
    
    def execute(self,command,*args): 
        # include error checking
        # Execute commands with *args as values, commands must have ?
        vals = self.cursor.execute(command,*args)
        # Commits the current transaction
        self.connection.commit()
        return vals

    # Keyvals must be a dictionary
    def insert_keyvals(self,table,keyvals):
        # Create a string of values seperated by ,
        names = ", ".join(keyvals.keys())
        qmarks = ", ".join(["?"] * len(keyvals))
        cmd = "INSERT INTO {0} ({1}) VALUES (?)".format(names,qmarks)
        self.execute(cmd,keyvals.values())

    # For examples, Database.create_new(x) is the same as x.create_new (assuming that x = Database().)
    # For a classmethod, the class of the object instance is passed rather than then object instance.
    # You can also call classmethods using the class rather than a class object. 
    @classmethod
    # Create new database
    def create_new(cls,dbname): 
        self = cls(dbname)
        self.execute(CREATE_EXPERIMENTS_TABLE)
        return self
    
    @classmethod
    def get_databases(cls):
        # Return list of pathnames that match the given pathname
        # Pathnames can either be absolute or relative
        dbs = glob.glob(os.path.join(DB_PATH,'*.db'))
        # Returns names of databases
        return [os.path.splitext(os.path.basename(x))[0] for x in dbs]

    # Insert a new experiment into the database
    # **kwargs allows your function to take an arbitrary number of keyword arguments
    # **kwargs is a dictionary: {'a':'1'}
    def add_experiment(self,**kwargs):
        self.execute("""
            INSERT INTO experiments (name, start, experimenter)
            VALUES (?, DateTime('now'), ?)
        """, (kwargs.get("name",""),kwargs.get("experimenter","")))
        # read-only attribute provides the row ID of the last modified row - ID of last entry into experiments table
        exp_id = self.cursor.lastrowid
        # Plate table will store all plates in the experiment
        self.execute(CREATE_PLATES_TABLE.format(plate_table_name(exp_id)))
        # Data table stores all data (including plate number)
        # Consider including resistance as an entry
        self.execute(CREATE_DATA_TABLE.format(data_table_name(exp_id)))
        return exp_id

    # Retrieve self-given names of experiments
    def get_experiment_ids(self):
        cmd = "SELECT name FROM experiments"
        return [x[0] for x in self.execute(cmd)]

    # default of experiment is None if not given.
    # Experiment identified by ID (primary key)
    def get_experiments(self,experiment=None):
        if experiment:
            cmd = "SELECT * FROM experiments WHERE id = ?"
            self.execute(cmd,(experiment,))
            # Places cursor by experiment
            return self.cursor.fetchone()
        else:
            # returns all experiments
            current = self.execute("SELECT * FROM experiments")
            return current.fetchall()

    # Retrieve plate information specified by plate and experiment
    def get_plates(self,experiment,plate=None,resistance=None):
        # Plate table name based off experiment ID
        plate_table = plate_table_name(experiment)
        if plate:
            cmd = "SELECT * FROM {0} WHERE plate = ?".format(plate_table)
            current =  self.execute(cmd,(plate,))
            return current.fetchall()
        else:
            # returns entire plate table
            cmd = "SELECT * FROM {0}".format(plate_table)
            current = self.execute(cmd)
            return current.fetchall()
    
    def get_data(self,experiment,plate=None):
        # Data table name based off experiment
        data_table = data_table_name(experiment)
        if plate:
            cmd = "SELECT * FROM {0} WHERE plate = ? ORDER BY time ASC".format(data_table)
            current=self.execute(cmd,(plate,))
            return current.fetchall()
        else:
            # produces all plates rather than just one selected
            cmd = "SELECT * FROM {0} ORDER BY time ASC".format(data_table)
            current = self.execute(cmd)
            return current.fetchall()

    # insert entry into data table
    def add_data(self,experiment,plate,time,resistance,data):
        table_name = data_table_name(experiment)
        cmd = "INSERT INTO {0} VALUES (?, ?, ?, ?)".format(table_name)
        self.execute(cmd,(plate,time,resistance,data,))
        
    # insert entry into plate table
    def add_plate(self,experiment,plate_id,name):
        table_name = plate_table_name(experiment)
        cmd = "INSERT INTO {0} VALUES (?, ?)".format(table_name)
        self.execute(cmd,(plate_id,name,))
    
    
if __name__ == '__main__':
    Database.create_new('Testing')
    # Add experiment to the database
    #exp_id = db.add_experiment(name = 'testfile',experimenter = 'Bonnie')
    #print type(db.get_experiment_ids())
    #print type(db.get_experiments())
    #print (db.get_plates(experiment=exp_id))
    #print (db.get_data(exp_id))
    #db.close()
        
    
