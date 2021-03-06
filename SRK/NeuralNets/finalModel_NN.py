import sys
import csv
import numpy as np
import pandas as pd
from sklearn import preprocessing, cross_validation, metrics
from sklearn import ensemble
sys.path.append("/home/sudalai/Softwares/xgboost-master/wrapper/")
import xgboost as xgb

np.random.seed(2015)
from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers.core import Dense, Activation, Dropout
from keras.constraints import maxnorm
from keras.utils import np_utils

from config import *

if __name__ == "__main__":
	train_file = "train_idvs.csv"
	test_file = "test_idvs.csv"
	user_file = "../../Data/user_list.csv"
	test_pred_file = "test_predictions_NN_trainseed1234.csv"

	train = pd.read_csv(train_file)
	users_list = np.array(pd.read_csv(user_file)["USER_ID_hash"]).astype('str')
	print train.shape

	print "Label encomding.."
	#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
	#train = train.drop(col_names, axis=1)

	#le_UserIDHash = preprocessing.LabelEncoder()
	#le_UserIDHash.fit(users_list)
        #train["USER_ID_hash"] = le_UserIDHash.transform(train["USER_ID_hash"].astype("str"))

	le_UserPrefName = preprocessing.LabelEncoder()
        temp = le_UserPrefName.fit_transform(unique_pref_name)
        train["UserPrefName"] = le_UserPrefName.transform(train["UserPrefName"])
        ohe_UserPrefName = preprocessing.OneHotEncoder(sparse=False)
        ohe_UserPrefName.fit(temp.reshape(-1,1))
        train_UserPrefName = ohe_UserPrefName.transform(train["UserPrefName"].reshape(-1,1))

        le_CouponCapsuleText = preprocessing.LabelEncoder()
        temp = le_CouponCapsuleText.fit_transform(unique_capsule_text)
        train["CouponCapsuleText"] = le_CouponCapsuleText.transform(train["CouponCapsuleText"])
        ohe_CouponCapsuleText = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponCapsuleText.fit(temp.reshape(-1,1))
        train_CouponCapsuleText = ohe_CouponCapsuleText.transform(train["CouponCapsuleText"].reshape(-1,1))

        le_CouponGenreName = preprocessing.LabelEncoder()
        temp = le_CouponGenreName.fit_transform(unique_genre_name)
        train["CouponGenreName"] = le_CouponGenreName.transform(train["CouponGenreName"])
        ohe_CouponGenreName = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponGenreName.fit(temp.reshape(-1,1))
        train_CouponGenreName = ohe_CouponGenreName.transform(train["CouponGenreName"].reshape(-1,1))

        le_CouponLargeAreaName = preprocessing.LabelEncoder()
        temp = le_CouponLargeAreaName.fit_transform(unique_large_area_name)
        train["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(train["CouponLargeAreaName"])
        ohe_CouponLargeAreaName = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponLargeAreaName.fit(temp.reshape(-1,1))
        train_CouponLargeAreaName = ohe_CouponLargeAreaName.transform(train["CouponLargeAreaName"].reshape(-1,1))

        le_CouponSmallAreaName = preprocessing.LabelEncoder()
        temp = le_CouponSmallAreaName.fit_transform(unique_small_area_name)
        train["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(train["CouponSmallAreaName"])
        ohe_CouponSmallAreaName = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponSmallAreaName.fit(temp.reshape(-1,1))
        train_CouponSmallAreaName = ohe_CouponSmallAreaName.transform(train["CouponSmallAreaName"].reshape(-1,1))

        le_CouponKenName = preprocessing.LabelEncoder()
        temp = le_CouponKenName.fit_transform(unique_ken_name)
        train["CouponKenName"] = le_CouponKenName.transform(train["CouponKenName"])
        ohe_CouponKenName = preprocessing.OneHotEncoder(sparse=False)
        ohe_CouponKenName.fit(temp.reshape(-1,1))
        train_CouponKenName = ohe_CouponKenName.transform(train["CouponKenName"].reshape(-1,1))

	print "Filling NAs.."
	train['CouponValidPeriod'].fillna(-999, inplace=True)

	train_y = np.array( train["DV"] )
	train_X = np.array( train.drop(["COUPON_ID_hash", "USER_ID_hash", "UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName", "DV"],axis=1))
        print train_X.shape, train_y.shape
        del train
        import gc
        gc.collect()

	train_X = np.hstack([train_X, train_UserPrefName, train_CouponCapsuleText, train_CouponGenreName, train_CouponLargeAreaName, train_CouponSmallAreaName, train_CouponKenName])
        del train_CouponCapsuleText
        del train_CouponGenreName
        del train_CouponLargeAreaName
        del train_UserPrefName
        del train_CouponSmallAreaName
        del train_CouponKenName
        gc.collect()

        print train_X.shape, train_y.shape

	################## XGBoost ###############
	sc = preprocessing.StandardScaler()
        train_X = sc.fit_transform(train_X)
	train_y = np_utils.to_categorical(train_y, 2)

        model = Sequential()
        model.add(Dense(train_X.shape[1], 64, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.2))
        model.add(Dense(64, 32, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.3))
        model.add(Dense(32, 16, init='he_uniform'))
        model.add(Activation('relu'))
        model.add(Dropout(0.3))
        model.add(Dense(16, 2, init='he_uniform'))
        model.add(Activation('softmax'))

        model.compile(loss='binary_crossentropy', optimizer='adam')
        model.fit(train_X, train_y, batch_size=128, nb_epoch=50, validation_split=0.05, verbose=2)

	del train_X
	del train_y
	gc.collect()
	train_X = 0
	train_y = 0

	print "Preparing test.."
	test_writer = csv.writer(open(test_pred_file, "w"))
	test_writer.writerow(["USER_ID_hash", "COUPON_ID_hash", "Prediction"])
	full_test = pd.read_csv(test_file, chunksize=354532)
	for test in full_test:
		print "Reading new chunk..."
		#col_names = ["UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName"]
		#test = test.drop(col_names, axis=1)
		test_userid = test["USER_ID_hash"].copy()
		#test["USER_ID_hash"] = le_UserIDHash.transform(test["USER_ID_hash"].astype("str"))

		test["UserPrefName"] = le_UserPrefName.transform(test["UserPrefName"].astype('str'))
		test_UserPrefName = ohe_UserPrefName.transform(test["UserPrefName"].reshape(-1,1))

                test["CouponCapsuleText"] = le_CouponCapsuleText.transform(test["CouponCapsuleText"].astype('str'))
		test_CouponCapsuleText = ohe_CouponCapsuleText.transform(test["CouponCapsuleText"].reshape(-1,1))

                test["CouponGenreName"] = le_CouponGenreName.transform(test["CouponGenreName"].astype('str'))
		test_CouponGenreName = ohe_CouponGenreName.transform(test["CouponGenreName"].reshape(-1,1))

                test["CouponLargeAreaName"] = le_CouponLargeAreaName.transform(test["CouponLargeAreaName"].astype('str'))
		test_CouponLargeAreaName = ohe_CouponLargeAreaName.transform(test["CouponLargeAreaName"].reshape(-1,1))

                test["CouponSmallAreaName"] = le_CouponSmallAreaName.transform(test["CouponSmallAreaName"].astype('str'))
		test_CouponSmallAreaName = ohe_CouponSmallAreaName.transform(test["CouponSmallAreaName"].reshape(-1,1))

                test["CouponKenName"] = le_CouponKenName.transform(test["CouponKenName"].astype('str'))
		test_CouponKenName = ohe_CouponKenName.transform(test["CouponKenName"].reshape(-1,1))

		test['CouponValidPeriod'].fillna(-999, inplace=True)
		#test_X = np.array(test.iloc[:,2:-1])
		#test_X = np.array( test.drop(["COUPON_ID_hash","USER_ID_hash","DV"],axis=1))
		test_X = np.array( test.drop(["COUPON_ID_hash", "USER_ID_hash", "UserPrefName", "CouponCapsuleText", "CouponGenreName", "CouponLargeAreaName", "CouponSmallAreaName", "CouponKenName", "DV"],axis=1))
		#del test
		gc.collect()

		test_X = np.hstack([test_X, test_UserPrefName, test_CouponCapsuleText, test_CouponGenreName, test_CouponLargeAreaName, test_CouponSmallAreaName, test_CouponKenName])
		del test_CouponCapsuleText
		del test_CouponGenreName
		del test_CouponLargeAreaName
		del test_UserPrefName
		del test_CouponSmallAreaName
		del test_CouponKenName

		test_X = sc.transform(test_X)
		preds = model.predict(test_X, verbose=0)[:,1]

		for row_no in xrange(test.shape[0]):
			test_writer.writerow([test_userid[row_no], test["COUPON_ID_hash"][row_no], preds[row_no]])
			
	
