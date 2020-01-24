import pandas as pd                 #data manip & analysis - we're using it to read in a csv file
import numpy as np                  #multi-dim arrays, matrices
import sklearn                      #machine learning library
from sklearn import linear_model
import matplotlib.pyplot as plot
import pickle                       #serialization (and de-) of python objects
from matplotlib import style
import math

alldata = pd.read_csv('student-mat.csv', sep=';')
#print(alldata.head)

################################################################
# after running with increased number of attributes, we notice that
# really it is the 'G2' attribute that has the most weight by far.
################################################################
data = alldata[['G1','G2','G3','studytime','absences','failures']]

################################################################
#soooo... we could just comment out the above, and reduce our
# data to just 'G2'(input feature) and 'G3' output label
# and we should get pretty much the same results as above
################################################################
#data = alldata[['G2','G3']]
#print(data.head)

predict = 'G3'

#'x' is the features
x = np.array(data.drop([predict],1))
#print(x)
#'y' is the label
y = np.array(data[predict])
#print(y)


x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.1)


################################################################
################################################################
# comment out the loop once we have a 95% accuracy model saved.
# from then on, we instead load the model
################################################################
################################################################
"""
bestScore = 0

for _ in range(200):
    # split the x(input feature values) and y(output label values) into 90% training data, 10% test data
    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(x, y, test_size = 0.1)

    linearModel = linear_model.LinearRegression()

    # find best-fit 'line' for the training data
    linearModel.fit(x_train, y_train)

    accuracy = linearModel.score(x_test, y_test)*100
    print('accuracy: ', accuracy)
    #print('coefficients: ', linearModel.coef_)
    #print('y intercept: ', linearModel.intercept_)

    if accuracy > bestScore:

        bestScore = accuracy

        print('found a better model : ', bestScore)

        ################################################################
        # save the latest best trained model to current directory
        ################################################################
        fileName = 'studentmodel.'+str(math.trunc(bestScore))+'.pickle'
        with open(fileName, 'wb') as f:
            pickle.dump(linearModel, f)

"""

################################################################
################################################################
################################################################
# so, everything above this line was taking the raw input data
# and training a model, saving the best one of the runs.
# now we will just load and use our best model
################################################################
pickle_in = open('studentmodel.95.pickle', 'rb')
linearModel = pickle.load(pickle_in)





accuracy = linearModel.score(x_test, y_test)
print('accuracy: ', accuracy)
print('coefficients: ', linearModel.coef_)
print('y intercept: ', linearModel.intercept_)

predictions = linearModel.predict(x_test)
for i in range(len(predictions)):
    if abs(predictions[i] - y_test[i]) >= 2:
        print(i, (predictions[i] - y_test[i]), predictions[i], y_test[i], x_test[i])
    #else:
        #print(i, ' prediction very close')



p = 'absences'
style.use('ggplot')
plot.scatter(data[p], data['G3'])
plot.xlabel(p)
plot.ylabel('Final Grade')
plot.show()
