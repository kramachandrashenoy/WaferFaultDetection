from sklearn.model_selection import train_test_split
from data_ingestion import data_loader
from data_preprocessing import preprocessing
from data_preprocessing import clustering
from best_model_finder import tuner
from file_operations import file_methods
from application_logging import logger
import os
import numpy as np

class trainModel:
    def __init__(self):
        self.log_writer = logger.App_Logger()
        self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')

    def trainingModel(self):
        try:
            print("Starting trainingModel")
            self.log_writer.log(self.file_object, 'Start of Training')

            print("Loading data")
            data_getter = data_loader.Data_Getter(self.file_object, self.log_writer)
            data = data_getter.get_data()
            print("Data loaded successfully")
            self.log_writer.log(self.file_object, 'Data loaded successfully')

            preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
            print("Removing column 'Wafer'")
            data = preprocessor.remove_columns(data, ['Wafer'])

            print("Separating features and labels")
            X, Y = preprocessor.separate_label_feature(data, label_column_name='Output')
            print("Encoding labels from [-1, 1] to [0, 1]")
            Y = np.where(Y == -1, 0, 1)
            self.log_writer.log(self.file_object, 'Feature and label separation completed')

            print("Checking for null values")
            is_null_present = preprocessor.is_null_present(X)
            self.log_writer.log(self.file_object, f'Null values present: {is_null_present}')

            if is_null_present:
                print("Imputing missing values")
                X = preprocessor.impute_missing_values(X)
                self.log_writer.log(self.file_object, 'Missing values imputed')

            print("Checking for zero standard deviation columns")
            cols_to_drop = preprocessor.get_columns_with_zero_std_deviation(X)
            self.log_writer.log(self.file_object, f'Columns with zero std dev: {cols_to_drop}')

            if cols_to_drop:
                print(f"Dropping columns: {cols_to_drop}")
                X = preprocessor.remove_columns(X, cols_to_drop)
                self.log_writer.log(self.file_object, 'Zero std dev columns dropped')

            print("Applying PCA")
            X = preprocessor.reduce_dimensions(X, n_components=50)
            print(f"Data shape after PCA: {X.shape}")
            self.log_writer.log(self.file_object, f'Data shape after PCA: {X.shape}')

            print(f"Data shape before clustering: {X.shape}")
            self.log_writer.log(self.file_object, f'Data shape before clustering: {X.shape}')

            print("Starting clustering")
            kmeans = clustering.KMeansClustering(self.file_object, self.log_writer)
            print("Running elbow_plot")
            number_of_clusters = kmeans.elbow_plot(X)
            print(f"Optimal number of clusters: {number_of_clusters}")
            self.log_writer.log(self.file_object, f'Optimal number of clusters: {number_of_clusters}')

            print(f"Creating {number_of_clusters} clusters")
            X = kmeans.create_clusters(X, number_of_clusters)
            self.log_writer.log(self.file_object, 'Clusters created')

            X['Labels'] = Y
            list_of_clusters = X['Cluster'].unique()
            print(f"Clusters found: {list_of_clusters}")
            self.log_writer.log(self.file_object, f'Clusters: {list_of_clusters}')

            for i in list_of_clusters:
                print(f"Processing cluster {i}")
                cluster_data = X[X['Cluster'] == i]
                cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
                cluster_label = cluster_data['Labels']
                self.log_writer.log(self.file_object, f'Cluster {i} data prepared')

                print(f"Splitting data for cluster {i}")
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1/3, random_state=355)
                self.log_writer.log(self.file_object, f'Cluster {i} data split')

                print(f"Finding best model for cluster {i}")
                model_finder = tuner.Model_Finder(self.file_object, self.log_writer)
                best_model_name, best_model = model_finder.get_best_model(x_train, y_train, x_test, y_test)
                self.log_writer.log(self.file_object, f'Best model for cluster {i}: {best_model_name}')

                print(f"Saving model {best_model_name} for cluster {i}")
                file_op = file_methods.File_Operation(self.file_object, self.log_writer)
                file_op.save_model(best_model, best_model_name + str(i))
                self.log_writer.log(self.file_object, f'Model {best_model_name} saved for cluster {i}')

            print("Training completed successfully")
            self.log_writer.log(self.file_object, 'Successful End of Training')
            self.file_object.close()
        except Exception as e:
            print(f"Error in trainingModel: {e}")
            self.log_writer.log(self.file_object, f'Unsuccessful End of Training: {str(e)}')
            self.file_object.close()
            raise
# from sklearn.model_selection import train_test_split
# from data_ingestion import data_loader
# from data_preprocessing import preprocessing
# from data_preprocessing import clustering
# from best_model_finder import tuner
# from file_operations import file_methods
# from application_logging import logger
# import os

# class trainModel:
#     """
#     This class shall be used to train the model on the dataset.

#     Written By: iNeuron Intelligence
#     Version: 1.0
#     Revisions: Added debug logging and ensured file paths for Render
#     """
#     def __init__(self):
#         self.log_writer = logger.App_Logger()
#         self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')

#     def trainingModel(self):
#         try:
#             print("Starting trainingModel")  # Debug log
#             self.log_writer.log(self.file_object, 'Start of Training')

#             # Getting the data from the source
#             print("Loading data")
#             data_getter = data_loader.Data_Getter(self.file_object, self.log_writer)
#             data = data_getter.get_data()
#             print("Data loaded successfully")
#             self.log_writer.log(self.file_object, 'Data loaded successfully')

#             """Doing the data preprocessing"""
#             preprocessor = preprocessing.Preprocessor(self.file_object, self.log_writer)
#             print("Removing column 'Wafer'")
#             data = preprocessor.remove_columns(data, ['Wafer'])

#             # Create separate features and labels
#             print("Separating features and labels")
#             X, Y = preprocessor.separate_label_feature(data, label_column_name='Output')
#             self.log_writer.log(self.file_object, 'Feature and label separation completed')

#             # Check if missing values are present
#             print("Checking for null values")
#             is_null_present = preprocessor.is_null_present(X)
#             self.log_writer.log(self.file_object, f'Null values present: {is_null_present}')

#             # If missing values are present, impute them
#             if is_null_present:
#                 print("Imputing missing values")
#                 X = preprocessor.impute_missing_values(X)
#                 self.log_writer.log(self.file_object, 'Missing values imputed')

#             # Check for columns with zero standard deviation
#             print("Checking for zero standard deviation columns")
#             cols_to_drop = preprocessor.get_columns_with_zero_std_deviation(X)
#             self.log_writer.log(self.file_object, f'Columns with zero std dev: {cols_to_drop}')

#             # Drop the columns with zero standard deviation
#             if cols_to_drop:
#                 print(f"Dropping columns: {cols_to_drop}")
#                 X = preprocessor.remove_columns(X, cols_to_drop)
#                 self.log_writer.log(self.file_object, 'Zero std dev columns dropped')

#             """Applying the clustering approach"""
#             print("Starting clustering")
#             kmeans = clustering.KMeansClustering(self.file_object, self.log_writer)
#             number_of_clusters = kmeans.elbow_plot(X)
#             self.log_writer.log(self.file_object, f'Optimal number of clusters: {number_of_clusters}')

#             # Divide the data into clusters
#             print(f"Creating {number_of_clusters} clusters")
#             X = kmeans.create_clusters(X, number_of_clusters)
#             self.log_writer.log(self.file_object, 'Clusters created')

#             # Create a new column for cluster assignments
#             X['Labels'] = Y
#             list_of_clusters = X['Cluster'].unique()
#             print(f"Clusters found: {list_of_clusters}")
#             self.log_writer.log(self.file_object, f'Clusters: {list_of_clusters}')

#             """Training models for each cluster"""
#             for i in list_of_clusters:
#                 print(f"Processing cluster {i}")
#                 cluster_data = X[X['Cluster'] == i]
#                 cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
#                 cluster_label = cluster_data['Labels']
#                 self.log_writer.log(self.file_object, f'Cluster {i} data prepared')

#                 # Split data into training and test sets
#                 print(f"Splitting data for cluster {i}")
#                 x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1/3, random_state=355)
#                 self.log_writer.log(self.file_object, f'Cluster {i} data split')

#                 # Find the best model
#                 print(f"Finding best model for cluster {i}")
#                 model_finder = tuner.Model_Finder(self.file_object, self.log_writer)
#                 best_model_name, best_model = model_finder.get_best_model(x_train, y_train, x_test, y_test)
#                 self.log_writer.log(self.file_object, f'Best model for cluster {i}: {best_model_name}')

#                 # Save the best model
#                 print(f"Saving model {best_model_name} for cluster {i}")
#                 file_op = file_methods.File_Operation(self.file_object, self.log_writer)
#                 file_op.save_model(best_model, best_model_name + str(i))
#                 self.log_writer.log(self.file_object, f'Model {best_model_name} saved for cluster {i}')

#             print("Training completed successfully")
#             self.log_writer.log(self.file_object, 'Successful End of Training')
#             self.file_object.close()
#         except Exception as e:
#             print(f"Error in trainingModel: {e}")
#             self.log_writer.log(self.file_object, f'Unsuccessful End of Training: {str(e)}')
#             self.file_object.close()
#             raise

# # """
# # This is the Entry point for Training the Machine Learning Model.

# # Written By: iNeuron Intelligence
# # Version: 1.0
# # Revisions: None

# # """


# # # Doing the necessary imports
# # from sklearn.model_selection import train_test_split
# # from data_ingestion import data_loader
# # from data_preprocessing import preprocessing
# # from data_preprocessing import clustering
# # from best_model_finder import tuner
# # from file_operations import file_methods
# # from application_logging import logger

# # #Creating the common Logging object


# # class trainModel:

# #     def __init__(self):
# #         self.log_writer = logger.App_Logger()
# #         self.file_object = open("Training_Logs/ModelTrainingLog.txt", 'a+')

# #     def trainingModel(self):
# #         # Logging the start of Training
# #         self.log_writer.log(self.file_object, 'Start of Training')
# #         try:
# #             # Getting the data from the source
# #             data_getter=data_loader.Data_Getter(self.file_object,self.log_writer)
# #             data=data_getter.get_data()


# #             """doing the data preprocessing"""

# #             preprocessor=preprocessing.Preprocessor(self.file_object,self.log_writer)
# #             data=preprocessor.remove_columns(data,['Wafer']) # remove the unnamed column as it doesn't contribute to prediction.

# #             # create separate features and labels
# #             X,Y=preprocessor.separate_label_feature(data,label_column_name='Output')

# #             # check if missing values are present in the dataset
# #             is_null_present=preprocessor.is_null_present(X)

# #             # if missing values are there, replace them appropriately.
# #             if(is_null_present):
# #                 X=preprocessor.impute_missing_values(X) # missing value imputation

# #             # check further which columns do not contribute to predictions
# #             # if the standard deviation for a column is zero, it means that the column has constant values
# #             # and they are giving the same output both for good and bad sensors
# #             # prepare the list of such columns to drop
# #             cols_to_drop=preprocessor.get_columns_with_zero_std_deviation(X)

# #             # drop the columns obtained above
# #             X=preprocessor.remove_columns(X,cols_to_drop)

# #             """ Applying the clustering approach"""

# #             kmeans=clustering.KMeansClustering(self.file_object,self.log_writer) # object initialization.
# #             number_of_clusters=kmeans.elbow_plot(X)  #  using the elbow plot to find the number of optimum clusters

# #             # Divide the data into clusters
# #             X=kmeans.create_clusters(X,number_of_clusters)

# #             #create a new column in the dataset consisting of the corresponding cluster assignments.
# #             X['Labels']=Y

# #             # getting the unique clusters from our dataset
# #             list_of_clusters=X['Cluster'].unique()

# #             """parsing all the clusters and looking for the best ML algorithm to fit on individual cluster"""

# #             for i in list_of_clusters:
# #                 cluster_data=X[X['Cluster']==i] # filter the data for one cluster

# #                 # Prepare the feature and Label columns
# #                 cluster_features=cluster_data.drop(['Labels','Cluster'],axis=1)
# #                 cluster_label= cluster_data['Labels']

# #                 # splitting the data into training and test set for each cluster one by one
# #                 x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=1 / 3, random_state=355)

# #                 model_finder=tuner.Model_Finder(self.file_object,self.log_writer) # object initialization

# #                 #getting the best model for each of the clusters
# #                 best_model_name,best_model=model_finder.get_best_model(x_train,y_train,x_test,y_test)

# #                 #saving the best model to the directory.
# #                 file_op = file_methods.File_Operation(self.file_object,self.log_writer)
# #                 save_model=file_op.save_model(best_model,best_model_name+str(i))

# #             # logging the successful Training
# #             self.log_writer.log(self.file_object, 'Successful End of Training')
# #             self.file_object.close()

# #         except Exception:
# #             # logging the unsuccessful Training
# #             self.log_writer.log(self.file_object, 'Unsuccessful End of Training')
# #             self.file_object.close()
# #             raise Exception
