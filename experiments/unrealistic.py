import argparse
import random
import statistics

import utils as utils
from joblib import Parallel, delayed
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument("-sample_size", default=40, type=int)
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument(
    "-classifier", default="svm"
)  # classifier svm, random_forest, neural_network, knn
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
    )

    random.Random(random_state).shuffle(users)
    subsampled_users = users[: args.sample_size]

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
                randomized=True,
            )

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            y_pred = utils.classify(
                X_train, y_train, X_test, classifier=args.classifier
            )

            eer = utils.calculate_eer(y_test, y_pred)
            eers.append(eer)  # EER for one of the two groups

        return statistics.mean(
            eers
        )  # Average of the two group-split EERS for this user

    EERS.append(
        statistics.mean(
            Parallel(n_jobs=args.jobs)(
                [delayed(user_include_eer)(user) for user in subsampled_users]
            )
        )
    )

utils.export_csv("../results/" + args.classifier + "/general/unrealistic.csv", EERS)
