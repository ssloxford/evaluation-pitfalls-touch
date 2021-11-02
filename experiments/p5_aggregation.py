import statistics
import argparse
import utils as utils
import numpy as np

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-aggregation_length_max", default=20, type=int)
parser.add_argument(
    "-random_state", default=1, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game=args.game,
    direction=args.direction,
    random_state=args.random_state,
)
EERS = []
aggregation_length_column = []

for aggregation_length in range(2, args.aggregation_length_max + 1):

    def user_eer(user, aggregation_length_user):

        if len(user_touches[user]) < aggregation_length_user * 5:
            return

        # Split into 2 equal user groups
        users_copy = list(users.copy())
        users_copy.remove(user)
        user_groups = utils.partition_list(users_copy)

        X_train, y_train, X_test, y_test = utils.combined_sessions_aggregation(
            user_touches,
            user_touches_shuffled,
            user,
            train_users=user_groups[0],
            test_users=user_groups[1],
            aggregation_length=aggregation_length,
        )

        X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
        X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)

        if args.classifier == "svm":
            pass
        elif args.classifier == "random_forest":
            pass
        elif args.classifier == "neural_network":
            pass
        clf = svm.SVC(gamma="scale")
        clf.fit(X_train, y_train)

        y_pred = []

        for i in range(len(X_test)):
            y_pred_aggregation = clf.decision_function(scaler.transform(X_test[i]))

            y_pred.append(statistics.mean(y_pred_aggregation))

        eer = utils.calculate_eer(y_test, y_pred)
        return eer

    EERS.extend(
        Parallel(n_jobs=args.jobs)(
            [delayed(user_eer)(user, aggregation_length) for user in users]
        )
    )
    aggregation_length_column.extend([aggregation_length] * len(users))

utils.export_csv_two_columns(
    "../results/" + args.classifier + "/p5_aggregations/aggregation_2-"
    + str(args.aggregation_length_max)
    + "_"
    + str(args.random_state)
    + ".csv",
    "aggregation_length",
    "eer",
    aggregation_length_column,
    EERS,
)
