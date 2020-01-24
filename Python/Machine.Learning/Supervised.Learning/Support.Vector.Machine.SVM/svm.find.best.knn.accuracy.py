##############################################################
# any KNN stuff here is just to do a comparison between using
# KNN vs using SVM
##############################################################
import sys
import math
import sklearn
from sklearn import datasets
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import metrics
##############################################################
#we're importing (below) just to be able to compare using KNN
#vs SVM
from sklearn.neighbors import KNeighborsClassifier


kNeighbors = 1
if len(sys.argv) > 1:
    kNeighbors = int(sys.argv[1])

cancer = datasets.load_breast_cancer()
tumorLabels = cancer.target_names
featureNames = cancer.feature_names
features = cancer.data
classes = cancer.target

#print(len(features))
#print(len(features[0]))
#print(features[0])
#print('----------')
#print(len(classes))
#print(classes)
#print('----------')
#print(featureNames)
#print(tumorLabels)

x = features
y = classes

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2)

worstAccuracy = sys.maxsize
bestAccuracy  = 0
runs          = 20
summ          = 0   

for _ in range(runs):
    x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.2)
    knnModel = KNeighborsClassifier(n_neighbors = kNeighbors)
    knnModel.fit(x_train, y_train)
    accuracy = knnModel.score(x_test, y_test)*100
    summ += accuracy
    if accuracy < worstAccuracy:
        worstAccuracy = accuracy
    if accuracy > bestAccuracy:
        bestAccuracy = accuracy

avgAccuracy = (summ/runs)
print('k:',kNeighbors,' avg:',math.trunc(avgAccuracy),' worst:',math.trunc(worstAccuracy),' best:',math.trunc(bestAccuracy))


#svmModel = svm.SVC()
#knnModel = KNeighborsClassifier(n_neighbors = 3)

#svmModel.fit(x_train, y_train)
#knnModel.fit(x_train, y_train)

#svmAccuracy = svmModel.score(x_test, y_test)
#knnAccuracy = knnModel.score(x_test, y_test)


#print(svmAccuracy, ' ', knnAccuracy)
