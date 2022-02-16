import argparse
import statistics

import utils as utils
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
)

EERS = []
user_eer_map = {}

for user in users:
    temp_eer_map = []
    temp_eer = []

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

    y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

    eer = utils.calculate_eer(y_test, y_pred)
    EERS.append(eer)

utils.export_csv("../results/" + args.classifier + "/general/per_user_eer.csv", EERS)
