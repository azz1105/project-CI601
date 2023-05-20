import numpy as np
import feature_extraction
from sklearn.ensemble import RandomForestClassifier as rfc
from sklearn.svm import SVC as SVM
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression as lr
#import secure_filename
import phishing_detection
from flask import jsonify

#Get result
def getResult(URL):

    #Importing dataset
    data = np.loadtxt("dataset.csv", delimiter = ",")

    #Seperating features and labels
    A = data[: , :-1]
    B = data[: , -1]

    #Seperating training features, testing features, training labels & testing labels
    A_train, A_test, B_train, B_test = train_test_split(A, B, test_size = 0.2)
    clf = rfc()
    clf = SVM()
    clf = lr()
    
    clf.fit(A_train, B_train)
    score = clf.score(A_test, B_test)
    print(score*100)

    A_new = []

    A_input = URL
    A_new=feature_extraction.generate_data_set(A_input)
    A_new = np.array(A_new).reshape(1,-1)

    try:
        prediction = clf.predict(A_new)
        if prediction == -1:
            return "Phishing URL"
        else:
            return "Legitimate URL"
    except:
        return "Phishing URL"
