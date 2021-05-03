import statistics
import argparse
import utils as utils

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-phone", default="iPhone 7"
)  # "iPhone 6s Plus", "iPhone 7 Plus", "iPhone 8 Plus","iPhone 6s", "iPhone 7", "iPhone 8","iPhone X", "iPhone XS", "iPhone XS Max"
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
    phone=args.phone,
)
EERS = []


def user_eer(user):
    if len(user_touches[user]) < 10:
        return

    # Split into 2 equal user groups
    users_copy = list(user_touches)
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

    eer = utils.calculate_eer(y_test, y_pred)

    return eer


EERS = Parallel(n_jobs=args.jobs)([delayed(user_eer)(user) for user in users])

utils.export_csv("../results/p2_phone_models/phone_" + args.phone + ".csv", EERS)
