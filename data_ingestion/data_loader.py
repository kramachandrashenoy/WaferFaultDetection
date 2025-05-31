import pandas as pd
import os

class Data_Getter:
    """
    This class shall be used for obtaining the data from the source for training.
    Written By: iNeuron Intelligence
    Version: 1.0
    Revisions: Added directory creation and debug logging
    """
    def __init__(self, file_object, logger_object):
        self.training_file = 'Training_FileFromDB/InputFile.csv'
        self.file_object = file_object
        self.logger_object = logger_object

    def get_data(self):
        """
        Method Name: get_data
        Description: This method reads the data from source.
        Output: A pandas DataFrame.
        On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object, 'Entered get_data')
        try:
            input_dir = 'Training_FileFromDB'
            os.makedirs(input_dir, exist_ok=True)
            print(f"Reading data from {self.training_file}")
            self.data = pd.read_csv(self.training_file)
            print("Data loaded successfully")
            self.logger_object.log(self.file_object, 'Data Load Successful')
            return self.data
        except Exception as e:
            self.logger_object.log(self.file_object, f'Error in get_data: {str(e)}')
            raise
# import pandas as pd

# class Data_Getter:
#     """
#     This class shall  be used for obtaining the data from the source for training.

#     Written By: iNeuron Intelligence
#     Version: 1.0
#     Revisions: None

#     """
#     def __init__(self, file_object, logger_object):
#         self.training_file='Training_FileFromDB/InputFile.csv'
#         self.file_object=file_object
#         self.logger_object=logger_object

#     def get_data(self):
#         """
#         Method Name: get_data
#         Description: This method reads the data from source.
#         Output: A pandas DataFrame.
#         On Failure: Raise Exception

#          Written By: iNeuron Intelligence
#         Version: 1.0
#         Revisions: None

#         """
#         self.logger_object.log(self.file_object,'Entered the get_data method of the Data_Getter class')
#         try:
#             self.data= pd.read_csv(self.training_file) # reading the data file
#             self.logger_object.log(self.file_object,'Data Load Successful.Exited the get_data method of the Data_Getter class')
#             return self.data
#         except Exception as e:
#             self.logger_object.log(self.file_object,'Exception occured in get_data method of the Data_Getter class. Exception message: '+str(e))
#             self.logger_object.log(self.file_object,
#                                    'Data Load Unsuccessful.Exited the get_data method of the Data_Getter class')
#             raise Exception()


