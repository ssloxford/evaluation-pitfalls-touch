import statistics
import argparse
import utils as utils
import pandas as pd
import random
import numpy as np

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
)

results = {
    "eer": [],
    "fpr": [],
    "tpr": [],
    "authorized": [],
    "unauthorized": []
}

for user in users:
    temp_eer_map = []
    temp_eer = []

    if len(session_user_touches[user]) < 2:
        continue

    # Split into 2 equal user groups
    users_copy = list(users.copy())
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

    clf = svm.SVC(gamma="scale")
    clf.fit(X_train, y_train)
    y_pred = clf.decision_function(X_test)

    fpr,tpr,eer = utils.calculate_roc(y_test, y_pred)
    results['eer'].append(eer)
    results['fpr'].append(list(np.around(fpr, 3)))
    results['tpr'].append(list(np.around(tpr, 3)))

    authorized = []
    unauthorized = []
    for i in range(len(y_test)):
      if y_test[i] == 0:
        unauthorized.append(y_pred[i])
      else:
        authorized.append(y_pred[i])

    results['authorized'].append(list(np.around(authorized, 3)))
    results['unauthorized'].append(list(np.around(random.sample(unauthorized,len(authorized)), 3)))

df = pd.DataFrame(results)
df.to_csv("../results/p3_training_selection/contiguous.csv", index=False)
