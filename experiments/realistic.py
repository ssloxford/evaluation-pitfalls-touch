import statistics
import argparse
import utils as utils
import random

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-sample_size", default=40)
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

EERS = []

for random_state in range(100):
    (
        users,
        user_touches,
        user_touches_shuffled,
        session_user_touches,
    ) = utils.preprocessing(
        dataset_path=args.dataset,
        game="swipe",
        direction="left",
        random_state=random_state,
        phone="iPhone 7",
    )

    random.Random(random_state).shuffle(users)
    subsampled_users = users[: args.sample_size]

    def user_exclude_eer(user):
        if len(session_user_touches[user]) < 2:
            return

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
        )

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

        eer = utils.calculate_eer(y_test, y_pred)
        return eer

    EERS.append(
        statistics.mean(
            [
                x
                for x in Parallel(n_jobs=args.jobs)(
                    [delayed(user_exclude_eer)(user) for user in subsampled_users]
                )
                if x is not None
            ]
        )
    )

utils.export_csv("../results/general/realistic.csv", EERS)
