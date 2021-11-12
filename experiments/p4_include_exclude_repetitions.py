import os
import statistics
import argparse
import utils as utils
import random

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument("-dataset", default="../data/features.csv")
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

for random_state in range(1, 11):
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

    excluded_EERS = []
    included_EERS = []
    sample_size_column = []

    storage_path = "../results/" + args.classifier + "/p4_include_excludes/include_exclude_" + str(args.game) + "_" + str(args.direction) + "_" + str(random_state) + ".csv"
    directory = "/".join(storage_path.split("/")[:-1])
    if not os.path.exists(directory):
        os.makedirs(directory)

    f = open(storage_path,"a")
    f.write("sample_size,include_eer,exclude_eer\n")

    for sample_size in range(10, 471, 5):
        random.Random(random_state).shuffle(users)
        subsampled_users = users[:sample_size]

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

            X_train, y_train = shuffle(X_train, y_train, random_state=random_state)
            X_test, y_test = shuffle(X_test, y_test, random_state=random_state)

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_test = scaler.transform(X_test)

            y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

            eer = utils.calculate_eer(y_test, y_pred)

            return eer

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

                y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

                eer = utils.calculate_eer(y_test, y_pred)
                eers.append(eer)  # EER for one of the two groups

            return statistics.mean(
                eers
            )  # Average of the two group-split EERS for this user

        excluded_EERS = Parallel(n_jobs=args.jobs)(
            [delayed(user_exclude_eer)(user) for user in subsampled_users]
        )
        included_EERS = Parallel(n_jobs=args.jobs)(
            [delayed(user_include_eer)(user) for user in subsampled_users]
        )
        sample_size_column = [sample_size] * len(subsampled_users)

        for i in range(len(sample_size_column)):
            if (
                (not sample_size_column[i] == None)
                and (not included_EERS[i] == None)
                and (not excluded_EERS[i] == None)
            ):
                f.write(
                    str(sample_size_column[i])
                    + ","
                    + str(included_EERS[i])
                    + ","
                    + str(excluded_EERS[i])
                    + "\n"
                )

    f.close()
