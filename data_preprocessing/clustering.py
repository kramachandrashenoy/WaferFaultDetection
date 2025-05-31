from sklearn.cluster import KMeans
from kneed import KneeLocator
from file_operations import file_methods
import numpy as np
import os

class KMeansClustering:
    """
    This class shall be used to divide the data into clusters before training.
    Written By: iNeuron Intelligence
    Version: 1.0
    Revisions: Optimized elbow_plot for Render, removed plotting
    """
    def __init__(self, file_object, logger_object):
        self.file_object = file_object
        self.logger_object = logger_object

    def elbow_plot(self, data):
        """
        Method Name: elbow_plot
        Description: Determines the optimum number of clusters using the elbow method.
        Output: Number of clusters
        On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object, 'Entered elbow_plot')
        wcss = []
        try:
            max_clusters = min(5, len(data))  # Limit to 5 clusters
            print(f"Testing 1 to {max_clusters} clusters")
            self.logger_object.log(self.file_object, f'Testing 1 to {max_clusters} clusters')
            for i in range(1, max_clusters + 1):
                print(f"Fitting KMeans with {i} clusters")
                kmeans = KMeans(n_clusters=i, init='k-means++', n_init='auto', random_state=42)
                kmeans.fit(data)
                wcss.append(kmeans.inertia_)
                self.logger_object.log(self.file_object, f'WCSS for {i} clusters: {kmeans.inertia_}')
            
            # Ensure preprocessing_data directory exists
            os.makedirs('preprocessing_data', exist_ok=True)
            
            # Find optimal clusters using KneeLocator
            self.kn = KneeLocator(range(1, max_clusters + 1), wcss, curve='convex', direction='decreasing')
            number_of_clusters = self.kn.knee if self.kn.knee else 2  # Default to 2 if no knee
            print(f"Selected {number_of_clusters} clusters")
            self.logger_object.log(self.file_object, f'Optimal clusters: {number_of_clusters}')
            return number_of_clusters
        except Exception as e:
            self.logger_object.log(self.file_object, f'Error in elbow_plot: {str(e)}')
            raise

    def create_clusters(self, data, number_of_clusters):
        """
        Method Name: create_clusters
        Description: Create a new dataframe with cluster information.
        Output: DataFrame with cluster column
        On Failure: Raise Exception
        """
        self.logger_object.log(self.file_object, 'Entered create_clusters')
        self.data = data
        try:
            print(f"Creating {number_of_clusters} clusters")
            self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', n_init='auto', random_state=42)
            self.y_kmeans = self.kmeans.fit_predict(data)
            self.file_op = file_methods.File_Operation(self.file_object, self.logger_object)
            self.save_model = self.file_op.save_model(self.kmeans, 'KMeans')
            self.data['Cluster'] = self.y_kmeans
            self.logger_object.log(self.file_object, f'Successfully created {number_of_clusters} clusters')
            return self.data
        except Exception as e:
            self.logger_object.log(self.file_object, f'Error in create_clusters: {str(e)}')
            raise 
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans
# from kneed import KneeLocator
# from file_operations import file_methods

# class KMeansClustering:
#     """
#             This class shall  be used to divide the data into clusters before training.

#             Written By: iNeuron Intelligence
#             Version: 1.0
#             Revisions: None

#             """

#     def __init__(self, file_object, logger_object):
#         self.file_object = file_object
#         self.logger_object = logger_object

#     def elbow_plot(self,data):
#         """
#                         Method Name: elbow_plot
#                         Description: This method saves the plot to decide the optimum number of clusters to the file.
#                         Output: A picture saved to the directory
#                         On Failure: Raise Exception

#                         Written By: iNeuron Intelligence
#                         Version: 1.0
#                         Revisions: None

#                 """
#         self.logger_object.log(self.file_object, 'Entered the elbow_plot method of the KMeansClustering class')
#         wcss=[] # initializing an empty list
#         try:
#             for i in range (1,11):
#                 kmeans=KMeans(n_clusters=i,init='k-means++',random_state=42) # initializing the KMeans object
#                 kmeans.fit(data) # fitting the data to the KMeans Algorithm
#                 wcss.append(kmeans.inertia_)
#             plt.plot(range(1,11),wcss) # creating the graph between WCSS and the number of clusters
#             plt.title('The Elbow Method')
#             plt.xlabel('Number of clusters')
#             plt.ylabel('WCSS')
#             #plt.show()
#             plt.savefig('preprocessing_data/K-Means_Elbow.PNG') # saving the elbow plot locally
#             # finding the value of the optimum cluster programmatically
#             self.kn = KneeLocator(range(1, 11), wcss, curve='convex', direction='decreasing')
#             self.logger_object.log(self.file_object, 'The optimum number of clusters is: '+str(self.kn.knee)+' . Exited the elbow_plot method of the KMeansClustering class')
#             return self.kn.knee

#         except Exception as e:
#             self.logger_object.log(self.file_object,'Exception occured in elbow_plot method of the KMeansClustering class. Exception message:  ' + str(e))
#             self.logger_object.log(self.file_object,'Finding the number of clusters failed. Exited the elbow_plot method of the KMeansClustering class')
#             raise Exception()

#     def create_clusters(self,data,number_of_clusters):
#         """
#                                 Method Name: create_clusters
#                                 Description: Create a new dataframe consisting of the cluster information.
#                                 Output: A datframe with cluster column
#                                 On Failure: Raise Exception

#                                 Written By: iNeuron Intelligence
#                                 Version: 1.0
#                                 Revisions: None

#                         """
#         self.logger_object.log(self.file_object, 'Entered the create_clusters method of the KMeansClustering class')
#         self.data=data
#         try:
#             self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=42)
#             #self.data = self.data[~self.data.isin([np.nan, np.inf, -np.inf]).any(1)]
#             self.y_kmeans=self.kmeans.fit_predict(data) #  divide data into clusters

#             self.file_op = file_methods.File_Operation(self.file_object,self.logger_object)
#             self.save_model = self.file_op.save_model(self.kmeans, 'KMeans') # saving the KMeans model to directory
#                                                                                     # passing 'Model' as the functions need three parameters

#             self.data['Cluster']=self.y_kmeans  # create a new column in dataset for storing the cluster information
#             self.logger_object.log(self.file_object, 'succesfully created '+str(self.kn.knee)+ 'clusters. Exited the create_clusters method of the KMeansClustering class')
#             return self.data
#         except Exception as e:
#             self.logger_object.log(self.file_object,'Exception occured in create_clusters method of the KMeansClustering class. Exception message:  ' + str(e))
#             self.logger_object.log(self.file_object,'Fitting the data to clusters failed. Exited the create_clusters method of the KMeansClustering class')
#             raise Exception()
