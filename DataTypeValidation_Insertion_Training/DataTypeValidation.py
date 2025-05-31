import shutil
import sqlite3
from datetime import datetime
from os import listdir
import os
import csv
from application_logging.logger import App_Logger


class dBOperation:
    """
    This class shall be used for handling all the SQL operations.

    Written By: iNeuron Intelligence
    Version: 1.0
    Revisions: Modified to handle Render filesystem and fix conn error
    """
    def __init__(self):
        self.path = '/tmp/Training_Database/'  # Use /tmp for Render
        self.badFilePath = "Training_Raw_files_validated/Bad_Raw"
        self.goodFilePath = "Training_Raw_files_validated/Good_Raw"
        self.logger = App_Logger()

    def dataBaseConnection(self, DatabaseName):
        """
        Method Name: dataBaseConnection
        Description: Creates the database with the given name or opens connection if it exists.
        Output: Connection to the DB
        On Failure: Raise Exception

        Written By: iNeuron Intelligence
        Version: 1.0
        Revisions: Added directory creation and better error handling
        """
        conn = None
        try:
            db_path = os.path.join(self.path, f"{DatabaseName}.db")
            print(f"Attempting to connect to database: {db_path}")  # Debug log
            if not os.path.exists(self.path):
                print(f"Creating directory: {self.path}")
                os.makedirs(self.path, exist_ok=True)
            conn = sqlite3.connect(db_path)
            print(f"Successfully connected to {db_path}")
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, f"Opened {DatabaseName} database successfully")
            file.close()
            return conn
        except Exception as e:
            file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
            self.logger.log(file, f"Error while connecting to database {db_path}: {e}")
            file.close()
            raise
        return conn

    def createTableDb(self, DatabaseName, column_names):
        """
        Method Name: createTableDb
        Description: Creates a table in the given database to store validated Good data.
        Output: None
        On Failure: Raise Exception

        Written By: iNeuron Intelligence
        Version: 1.0
        Revisions: Fixed conn.close() error and added debug logs
        """
        conn = None
        try:
            conn = self.dataBaseConnection(DatabaseName)
            c = conn.cursor()
            c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Good_Raw_Data'")
            if c.fetchone()[0] == 1:
                print("Table Good_Raw_Data already exists")
                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()
            else:
                for key, data_type in column_names.items():
                    try:
                        c.execute('ALTER TABLE Good_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key, dataType=data_type))
                        print(f"Added column {key} to Good_Raw_Data")
                    except:
                        c.execute('CREATE TABLE Good_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=data_type))
                        print(f"Created table Good_Raw_Data with column {key}")
                conn.commit()
                file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
                self.logger.log(file, "Tables created successfully!!")
                file.close()
        except Exception as e:
            file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
            self.logger.log(file, f"Error while creating table: {e}")
            file.close()
            raise
        finally:
            if conn is not None:
                print(f"Closing database connection for {DatabaseName}")
                conn.close()
                file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
                self.logger.log(file, f"Closed {DatabaseName} database successfully")
                file.close()

    def insertIntoTableGoodData(self, Database):
        """
        Method Name: insertIntoTableGoodData
        Description: Inserts Good data files from Good_Raw folder into the table.
        Output: None
        On Failure: Raise Exception

        Written By: iNeuron Intelligence
        Version: 1.0
        Revisions: None
        """
        conn = None
        log_file = None
        try:
            conn = self.dataBaseConnection(Database)
            goodFilePath = self.goodFilePath
            badFilePath = self.badFilePath
            onlyfiles = [f for f in listdir(goodFilePath)]
            log_file = open("Training_Logs/DbInsertLog.txt", 'a+')

            for file in onlyfiles:
                try:
                    with open(os.path.join(goodFilePath, file), "r") as f:
                        next(f)
                        reader = csv.reader(f, delimiter="\n")
                        for line in enumerate(reader):
                            for list_ in line[1]:
                                try:
                                    conn.execute('INSERT INTO Good_Raw_Data values ({values})'.format(values=list_))
                                    self.logger.log(log_file, f"{file}: File loaded successfully!!")
                                    conn.commit()
                                except Exception as e:
                                    raise
                except Exception as e:
                    conn.rollback()
                    self.logger.log(log_file, f"Error while inserting {file}: {e}")
                    shutil.move(os.path.join(goodFilePath, file), badFilePath)
                    self.logger.log(log_file, f"File Moved Successfully {file}")
            log_file.close()
        except Exception as e:
            if log_file is not None:
                self.logger.log(log_file, f"Error in insertIntoTableGoodData: {e}")
                log_file.close()
            raise
        finally:
            if conn is not None:
                conn.close()

    def selectingDatafromtableintocsv(self, Database):
        """
        Method Name: selectingDatafromtableintocsv
        Description: Exports data from Good_Raw_Data table to a CSV file.
        Output: None
        On Failure: Raise Exception

        Written By: iNeuron Intelligence
        Version: 1.0
        Revisions: None
        """
        self.fileFromDb = 'Training_FileFromDB/'
        self.fileName = 'InputFile.csv'
        log_file = None
        conn = None
        try:
            conn = self.dataBaseConnection(Database)
            sqlSelect = "SELECT * FROM Good_Raw_Data"
            cursor = conn.cursor()
            cursor.execute(sqlSelect)
            results = cursor.fetchall()
            headers = [i[0] for i in cursor.description]

            if not os.path.isdir(self.fileFromDb):
                os.makedirs(self.fileFromDb, exist_ok=True)

            csvFile = csv.writer(
                open(os.path.join(self.fileFromDb, self.fileName), 'w', newline=''),
                delimiter=',',
                lineterminator='\r\n',
                quoting=csv.QUOTE_ALL,
                escapechar='\\'
            )
            csvFile.writerow(headers)
            csvFile.writerows(results)

            log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
            self.logger.log(log_file, "File exported successfully!!!")
            log_file.close()
        except Exception as e:
            if log_file is not None:
                self.logger.log(log_file, f"File exporting failed. Error: {e}")
                log_file.close()
            raise
        finally:
            if conn is not None:
                conn.close()

# import shutil
# import sqlite3
# from datetime import datetime
# from os import listdir
# import os
# import csv
# from application_logging.logger import App_Logger


# class dBOperation:
#     """
#       This class shall be used for handling all the SQL operations.

#       Written By: iNeuron Intelligence
#       Version: 1.0
#       Revisions: None

#       """
#     def __init__(self):
#         self.path = 'Training_Database/'
#         self.badFilePath = "Training_Raw_files_validated/Bad_Raw"
#         self.goodFilePath = "Training_Raw_files_validated/Good_Raw"
#         self.logger = App_Logger()


#     def dataBaseConnection(self,DatabaseName):

#         """
#                 Method Name: dataBaseConnection
#                 Description: This method creates the database with the given name and if Database already exists then opens the connection to the DB.
#                 Output: Connection to the DB
#                 On Failure: Raise ConnectionError

#                  Written By: iNeuron Intelligence
#                 Version: 1.0
#                 Revisions: None

#                 """
#         try:
#             conn = sqlite3.connect(self.path+DatabaseName+'.db')

#             file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
#             self.logger.log(file, "Opened %s database successfully" % DatabaseName)
#             file.close()
#         except ConnectionError:
#             file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
#             self.logger.log(file, "Error while connecting to database: %s" %ConnectionError)
#             file.close()
#             raise ConnectionError
#         return conn

#     def createTableDb(self,DatabaseName,column_names):
#         """
#                         Method Name: createTableDb
#                         Description: This method creates a table in the given database which will be used to insert the Good data after raw data validation.
#                         Output: None
#                         On Failure: Raise Exception

#                          Written By: iNeuron Intelligence
#                         Version: 1.0
#                         Revisions: None

#                         """
#         try:
#             conn = self.dataBaseConnection(DatabaseName)
#             c=conn.cursor()
#             c.execute("SELECT count(name)  FROM sqlite_master WHERE type = 'table'AND name = 'Good_Raw_Data'")
#             if c.fetchone()[0] ==1:
#                 conn.close()
#                 file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
#                 self.logger.log(file, "Tables created successfully!!")
#                 file.close()

#                 file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
#                 self.logger.log(file, "Closed %s database successfully" % DatabaseName)
#                 file.close()

#             else:

#                 for key in column_names.keys():
#                     type = column_names[key]

#                     #in try block we check if the table exists, if yes then add columns to the table
#                     # else in catch block we will create the table
#                     try:
#                         #cur = cur.execute("SELECT name FROM {dbName} WHERE type='table' AND name='Good_Raw_Data'".format(dbName=DatabaseName))
#                         conn.execute('ALTER TABLE Good_Raw_Data ADD COLUMN "{column_name}" {dataType}'.format(column_name=key,dataType=type))
#                     except:
#                         conn.execute('CREATE TABLE  Good_Raw_Data ({column_name} {dataType})'.format(column_name=key, dataType=type))


#                 conn.close()

#                 file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
#                 self.logger.log(file, "Tables created successfully!!")
#                 file.close()

#                 file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
#                 self.logger.log(file, "Closed %s database successfully" % DatabaseName)
#                 file.close()

#         except Exception as e:
#             file = open("Training_Logs/DbTableCreateLog.txt", 'a+')
#             self.logger.log(file, "Error while creating table: %s " % e)
#             file.close()
#             conn.close()
#             file = open("Training_Logs/DataBaseConnectionLog.txt", 'a+')
#             self.logger.log(file, "Closed %s database successfully" % DatabaseName)
#             file.close()
#             raise e


#     def insertIntoTableGoodData(self,Database):

#         """
#                                Method Name: insertIntoTableGoodData
#                                Description: This method inserts the Good data files from the Good_Raw folder into the
#                                             above created table.
#                                Output: None
#                                On Failure: Raise Exception

#                                 Written By: iNeuron Intelligence
#                                Version: 1.0
#                                Revisions: None

#         """

#         conn = self.dataBaseConnection(Database)
#         goodFilePath= self.goodFilePath
#         badFilePath = self.badFilePath
#         onlyfiles = [f for f in listdir(goodFilePath)]
#         log_file = open("Training_Logs/DbInsertLog.txt", 'a+')

#         for file in onlyfiles:
#             try:
#                 with open(goodFilePath+'/'+file, "r") as f:
#                     next(f)
#                     reader = csv.reader(f, delimiter="\n")
#                     for line in enumerate(reader):
#                         for list_ in (line[1]):
#                             try:
#                                 conn.execute('INSERT INTO Good_Raw_Data values ({values})'.format(values=(list_)))
#                                 self.logger.log(log_file," %s: File loaded successfully!!" % file)
#                                 conn.commit()
#                             except Exception as e:
#                                 raise e

#             except Exception as e:

#                 conn.rollback()
#                 self.logger.log(log_file,"Error while creating table: %s " % e)
#                 shutil.move(goodFilePath+'/' + file, badFilePath)
#                 self.logger.log(log_file, "File Moved Successfully %s" % file)
#                 log_file.close()
#                 conn.close()

#         conn.close()
#         log_file.close()


#     def selectingDatafromtableintocsv(self,Database):

#         """
#                                Method Name: selectingDatafromtableintocsv
#                                Description: This method exports the data in GoodData table as a CSV file. in a given location.
#                                             above created .
#                                Output: None
#                                On Failure: Raise Exception

#                                 Written By: iNeuron Intelligence
#                                Version: 1.0
#                                Revisions: None

#         """

#         self.fileFromDb = 'Training_FileFromDB/'
#         self.fileName = 'InputFile.csv'
#         log_file = open("Training_Logs/ExportToCsv.txt", 'a+')
#         try:
#             conn = self.dataBaseConnection(Database)
#             sqlSelect = "SELECT *  FROM Good_Raw_Data"
#             cursor = conn.cursor()

#             cursor.execute(sqlSelect)

#             results = cursor.fetchall()
#             # Get the headers of the csv file
#             headers = [i[0] for i in cursor.description]

#             #Make the CSV ouput directory
#             if not os.path.isdir(self.fileFromDb):
#                 os.makedirs(self.fileFromDb)

#             # Open CSV file for writing.
#             csvFile = csv.writer(open(self.fileFromDb + self.fileName, 'w', newline=''),delimiter=',', lineterminator='\r\n',quoting=csv.QUOTE_ALL, escapechar='\\')

#             # Add the headers and data to the CSV file.
#             csvFile.writerow(headers)
#             csvFile.writerows(results)

#             self.logger.log(log_file, "File exported successfully!!!")
#             log_file.close()

#         except Exception as e:
#             self.logger.log(log_file, "File exporting failed. Error : %s" %e)
#             log_file.close()





