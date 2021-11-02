import statistics
import argparse
import utils as utils

from sklearn import svm
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-randomized", default=False, type=bool
)  # shuffle user swipes or keep in order
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
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
    # At least 2 measurments are needed
    if len(session_user_touches[user]) < 2:
        continue

    # Split into 2 equal user groups
    users_copy = list(users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)

    X_train, X_test, y_train, y_test = utils.dedicated_sessions(
        session_user_touches,
        user_touches_shuffled,
        user,
        train_users=user_groups[0],
        test_users=user_groups[1],
        randomized=args.randomized,
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

    eer = utils.calculate_eer(y_test, y_pred)
    EERS.append(eer)

if args.randomized:
    utils.export_csv(
        "../results/p3_training_selection/dedicated_randomized_sessions.csv", EERS
    )
else:
    utils.export_csv("../results/p3_training_selection/dedicated_sessions.csv", EERS)
