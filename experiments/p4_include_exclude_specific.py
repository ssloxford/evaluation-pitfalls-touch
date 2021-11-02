import statistics
import argparse
import utils as utils
import pandas as pd
import random
import numpy as np

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument('-sample_size', default=400, type=int)
parser.add_argument('-random_state', default=42, type=int) # random state for reproducability
parser.add_argument('-jobs', default=6, type=int) # parallelization parameter   
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset, 
    game="swipe", 
    direction="left", 
    random_state=args.random_state
)

random.Random(args.random_state).shuffle(users)
subsampled_users = users[:args.sample_size]

results_include = {
    "eer": [],
    "fpr": [],
    "tpr": [],
    "authorized": [],
    "unauthorized": []
}

results_exclude = {
    "eer": [],
    "fpr": [],
    "tpr": [],
    "authorized": [],
    "unauthorized": []
}

def user_exclude_eer(user):
    if len(user_touches[user]) < 10:
        return

    # Split into 2 equal user groups
    users_copy = list(subsampled_users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, y_train, X_test, y_test = utils.combined_sessions(
        user_touches,
        user_touches_shuffled,
        user,
        train_users=user_groups[0],
        test_users=user_groups[1],
    )

    X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
    X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

    fpr,tpr,eer = utils.calculate_roc(y_test, y_pred)
    results_exclude['eer'].append(eer)
    results_exclude['fpr'].append(list(np.around(fpr, 3)))
    results_exclude['tpr'].append(list(np.around(tpr, 3)))

    authorized = []
    unauthorized = []
    for i in range(len(y_test)):
        if y_test[i] == 0:
            unauthorized.append(y_pred[i])
        else:
            authorized.append(y_pred[i])

    results_exclude['authorized'].append(list(np.around(authorized, 3)))
    results_exclude['unauthorized'].append(list(np.around(random.sample(unauthorized,len(authorized)), 3)))


def user_include_eer(user):

    if len(user_touches[user]) < 10:
        return

     # Split into 2 equal user groups
    users_copy = list(subsampled_users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    eers = []
    for user_group in user_groups:
        (
            X_train,
            y_train,
            X_test,
            y_test,
        ) = utils.combined_sessions_subsampled_include_attacker(
            user_touches,
            user_touches_shuffled,
            user,
            subsampled_users=user_group,
        )

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        clf = svm.SVC(gamma="scale")
        clf.fit(X_train, y_train)
        y_pred = clf.decision_function(X_test)

        fpr,tpr,eer = utils.calculate_roc(y_test, y_pred)
        results_include['eer'].append(eer)
        results_include['fpr'].append(list(np.around(fpr, 3)))
        results_include['tpr'].append(list(np.around(tpr, 3)))

        authorized = []
        unauthorized = []
        for i in range(len(y_test)):
            if y_test[i] == 0:
                unauthorized.append(y_pred[i])
            else:
                authorized.append(y_pred[i])

        results_include['authorized'].append(list(np.around(authorized, 3)))
        results_include['unauthorized'].append(list(np.around(random.sample(unauthorized,len(authorized)), 3)))

for user in subsampled_users:
    user_exclude_eer(user)
    user_include_eer(user)

df = pd.DataFrame(results_include)
df.to_csv("../" + args.classifier + "/results/" + args.classifier + "/p4_include_excludes/include_" + str(args.sample_size) + ".csv", index=False)

df2 = pd.DataFrame(results_exclude)
df2.to_csv("../" + args.classifier + "/results/" + args.classifier + "/p4_include_excludes/exclude_" + str(args.sample_size) + ".csv", index=False)