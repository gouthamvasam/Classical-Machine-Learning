"""
The following code worked on Python 3.5.6; openCV 3.1.0; Spyder 3.3.1; sklearn 0.20.0; joblib 0.12.5 - created a custom environment of Anaconda - might not be possible on all computers.
All section images resized to 1000 x 1000.
Images used for test are completely different that the ones used for training.
696 and 768 test images for MVM- and MVM+, respectively.
3233 and 3534 train images for MVM- and MVM+, respectively.
"""

import cv2
import numpy as np
import os
import pylab as pl
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.externals import joblib


# Load the classifier, class names, scaler, number of clusters and vocabulary 
#from stored pickle file (generated during training), change file name as required
clf, classes_names, stdSlr, k, voc = joblib.load("PE2_DA_bovw_sift500_km100_XGB200.pkl")

# Get the path of the testing image(s) and store them in a list
#test_path = 'PE2_SVM_Divided_TT_70-30_8DA_1image/test' # Names are MVM- and MVM+
test_path = 'PE2_SVM_Divided_TT_70-30_8DA_1image/test'  # Folder Names are MVM- and MVM+

testing_names = os.listdir(test_path)

# Get path to all images and save them in a list
# image_paths and the corresponding label in image_paths
image_paths = []
image_classes = []
class_id = 0

#To make it easy to list all file names in a directory let us define a function
def imglist(path):
    return [os.path.join(path, f) for f in os.listdir(path)]

#Fill the placeholder empty lists with image path, classes, and add class ID number

for testing_name in testing_names:
    dir = os.path.join(test_path, testing_name)
    class_path = imglist(dir)
    image_paths+=class_path
    image_classes+=[class_id]*len(class_path)
    class_id+=1
    
# Create feature extraction and keypoint detector objects
#SIFT is not available anymore in openCV (patented- need to get a license?) 
# Create List where all the descriptors will be stored
des_list = []

#BRISK is a good replacement to SIFT (patented - license needed). ORB also works - may need to try for this dataset.
#brisk = cv2.BRISK_create(250) #try 250 and 500 features
#orb = cv2.ORB_create(250) #try 250 and 500 features
sift = cv2.xfeatures2d.SIFT_create(500) #use what we used during the training

for image_path in image_paths:
    im = cv2.imread(image_path)
    kpts, des = sift.detectAndCompute(im, None)
    des_list.append((image_path, des))   
    
# Stack all the descriptors vertically in a numpy array
descriptors = des_list[0][1]
for image_path, descriptor in des_list[0:]:
    descriptors = np.vstack((descriptors, descriptor)) 

# Calculate the histogram of features
#vq Assigns codes from a code book to observations.
from scipy.cluster.vq import vq    
test_features = np.zeros((len(image_paths), k), "float32")
for i in range(len(image_paths)):
    words, distance = vq(des_list[i][1],voc)
    for w in words:
        test_features[i][w] += 1

# Perform Tf-Idf vectorization
nbr_occurences = np.sum( (test_features > 0) * 1, axis = 0)
idf = np.array(np.log((1.0*len(image_paths)+1) / (1.0*nbr_occurences + 1)), 'float32')

# Scale the features
#Standardize features by removing the mean and scaling to unit variance
#Scaler (stdSlr comes from the pickled file we imported)
test_features = stdSlr.transform(test_features)

#######Until here most of the above code is similar to Train except for kmeans clustering####
#Once we vectorize the histogram of features kmeans is not needed anymore.

#Report true class names so they can be compared with predicted classes
true_class =  [classes_names[i] for i in image_classes]
# Perform the predictions and report predicted class names. 
predictions =  [classes_names[i] for i in clf.predict(test_features)]


#Print the true class and Predictions 
print ("true_class ="  + str(true_class))
print ("prediction ="  + str(predictions))

###############################################
#To make it easy to understand the accuracy print the confusion matrix

def showconfusionmatrix(cm):
    pl.matshow(cm)
    pl.title('Confusion matrix')
    pl.colorbar()
    pl.show()


accuracy = accuracy_score(true_class, predictions)
print ("accuracy = ", accuracy)
cm = confusion_matrix(true_class, predictions)
print (cm)

showconfusionmatrix(cm)


#For classification of unknown files we can print the predictions
#Print the Predictions 
print ("Image =", image_paths)
print ("prediction ="  + str(predictions))
#np.transpose to save data into columns, otherwise saving as rows
#change file name below as required
np.savetxt ('mydata.csv', np.transpose([image_paths, predictions]),fmt='%s', delimiter=',', newline='\n')