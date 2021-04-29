import statistics
import argparse
import utils as utils

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument('-dataset', default="../data/data.csv")
parser.add_argument('-random_state', default=42, type=int) # random state for reproducability
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(dataset_path=args.dataset, game="swipe", direction="left", random_state=args.random_state)

EERS = []
user_eer_map = {}

for user in users:

    if len(session_user_touches[user]) < 2:
        continue

    temp_eer_map = []
    temp_eer = []

    # Split into 2 equal user groups
    users_copy = list(users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, y_train, X_test, y_test = utils.combined_sessions(user_touches, user_touches_shuffled, user, train_users=user_groups[0], test_users=user_groups[1])

    X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
    X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    clf = svm.SVC(gamma='scale')
    clf.fit(X_train, y_train)
    y_pred = clf.decision_function(X_test)

    eer = utils.calculate_eer(y_test, y_pred)
    EERS.append(eer)

utils.export_csv('../results/general/per_user_eer.csv', EERS)
