import sys
import math
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import numpy as np
from sklearn import linear_model, preprocessing

kNeighbors = 7

data = pd.read_csv('car.data');
#print(data.head)


# we need to convert our non-numeric input features to numbers
# i.e: low => 0, med => 1, high => 2
# etc
#buying,maint,door,persons,lug_boot,safety,class
labelEncoder = preprocessing.LabelEncoder()
buying   = labelEncoder.fit_transform(list(data['buying']))
maint    = labelEncoder.fit_transform(list(data['maint']))
door     = labelEncoder.fit_transform(list(data['door']))
persons  = labelEncoder.fit_transform(list(data['persons']))
lug_boot = labelEncoder.fit_transform(list(data['lug_boot']))
safety   = labelEncoder.fit_transform(list(data['safety']))
clazz    = labelEncoder.fit_transform(list(data['class']))


x = list(zip(buying, maint, door, persons, lug_boot, safety))
y = list(clazz)

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.1)

knnModel = KNeighborsClassifier(n_neighbors = kNeighbors)

knnModel.fit(x_train, y_train)
    
accuracy = knnModel.score(x_test, y_test)*100


classLabels   = ['Unacceptable', 'Acceptable', 'Good', 'Very Good'];
buyLabels   = ['vhigh', 'high', 'med', 'low'];
maintLabels   = ['vhigh', 'high', 'med', 'low'];
doorsLabels  = ['2', '3', '4', '5+'];
personsLabels   = ['2', '4', 'more'];
lugBootLabels   = ['small', 'med', 'big'];
safetyLabels   = ['low', 'med', 'high'];

predictions = knnModel.predict(x_test)

for x in range(len(predictions)):
    if predictions[x] != y_test[x]:
        print(x, 'pred: ', classLabels[predictions[x]], ' actual: ', classLabels[y_test[x]], ' buying: ', buyLabels[x_test[x][0]], ' maint: ', maintLabels[x_test[x][1]])

