##############################################################
# any KNN stuff here is just to do a comparison between using
# KNN vs using SVM
##############################################################
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


kNeighbors = 9

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


##############################################################
#if you ran svm.without.any.params.to.svm.model.py, you noticed
# that svm accuracy was horrible. so let's add some params here
# param :  kernel='linear'
#           wow, with the above param added, SVM almost always
#           is better than KNN, AND it has less of a swing.
#           Sometimes, KNN swings into the high 80s, but SVM
#           has not gotten below 91 for any run so far.
##############################################################
#svmModel = svm.SVC(kernel='linear')

#
##############################################################
# kernel='poly' takes WWWAAAAAAAY too long, I didnt let it
# finish even one run
#svmModel = svm.SVC(kernel='poly',degree=2)

#
##############################################################
# kernel='sigmoid' returns very quick, and result is TERRIBLE
#svmModel = svm.SVC(kernel='sigmoid')

##############################################################
# so we know kernel='linear' is best.
# let's add another param:
# C=1
svmModel = svm.SVC(kernel='linear',C=2)

knnModel = KNeighborsClassifier(n_neighbors = kNeighbors)

svmModel.fit(x_train, y_train)
knnModel.fit(x_train, y_train)

svmAccuracy = svmModel.score(x_test, y_test)*100
knnAccuracy = knnModel.score(x_test, y_test)*100

print('svm:',math.trunc(svmAccuracy),' knn:',math.trunc(knnAccuracy))

svmPredictions = svmModel.predict(x_test)
knnPredictions = knnModel.predict(x_test)


##############################################################
# a different way to check accuracy , instead of 'model.score()'
# I dont see a benefit. getting the same results..
# seems like more code... more complicated?
#metricsSvmAccuracy = metrics.accuracy_score(y_test, svmPredictions)
#metricsKnnAccuracy = metrics.accuracy_score(y_test, knnPredictions)
#print(metricsSvmAccuracy, ' ', metricsKnnAccuracy)



#print(len(features))
#print(len(features[0]))
#print(features[0])
#print('----------')
#print(len(classes))
#print(classes)
#print('----------')
print(featureNames)
#print(tumorLabels)

#for x in range(len(svmPredictions)):
#    if svmPredictions[x] != y_test[x]:
#        print(x,'p:',tumorLabels[svmPredictions[x]],' 
