import statistics
import argparse
import utils as utils

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-sanitize_length_min", default=3, type=int)
parser.add_argument("-sanitize_length_max", default=15, type=int)
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
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

EERS_early = []
EERS_late = []
sanitize_length_column = []

for sanitize_length in range(args.sanitize_length_min, args.sanitize_length_max + 1):
    lusers = 0
    for user in users:
        if len(user_touches[user]) < 10:
            continue

        is_long = len(session_user_touches[user]) == 31

        if not is_long:
            continue

        lusers += 1

        # Split into 2 equal user groups
        users_copy = list(users.copy())
        users_copy.remove(user)
        user_groups = utils.partition_list(users_copy)

        # Analyse last 31 - sanitize_length sessions
        X_train, y_train, X_test, y_test = utils.combined_sessions_sanitize(
            user_touches,
            user_touches_shuffled,
            session_user_touches,
            user,
            train_users=user_groups[0],
            test_users=user_groups[1],
            early=False,
            sanitize_length=sanitize_length,
        )

        X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
        X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

        eer = utils.calculate_eer(y_test, y_pred)
        EERS_late.append(eer)

        # Analyse first sanitize_length sessions

        X_train, y_train, X_test, y_test = utils.combined_sessions_sanitize(
            user_touches,
            user_touches_shuffled,
            session_user_touches,
            user,
            train_users=user_groups[0],
            test_users=user_groups[1],
            early=True,
            sanitize_length=sanitize_length,
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

        EERS_early.append(eer)

    sanitize_length_column.extend([sanitize_length] * lusers)

utils.export_csv_three_columns(
    "../results/"
    + args.classifier
    + "/p1_sessions/early_late_sessions_"
    + str(args.sanitize_length_min)
    + "_"
    + str(args.sanitize_length_max)
    + ".csv",
    "sanitize_length",
    "early_eer",
    "late_eer",
    sanitize_length_column,
    EERS_early,
    EERS_late,
)
