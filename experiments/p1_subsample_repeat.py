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
parser.add_argument("-repetitions", default=1000, type=int)
parser.add_argument(
    "-random_state", default=42, type=int
)  # random state for reproducability
parser.add_argument("-jobs", default=6, type=int)  # parallelization parameter
parser.add_argument("-classifier", default="svm")  # classifier svm, random_forest, neural_network, knn
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(
    dataset_path=args.dataset,
    game="swipe",
    direction="left",
    random_state=args.random_state,
)


def user_eer(sample_size):
    random.shuffle(users)
    subsampled_users = users[:sample_size]

    EERS = []
    for user in subsampled_users:
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

        X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
        X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        y_pred = utils.classify(X_train, y_train, X_test, classifier=args.classifier)

        eer = utils.calculate_eer(y_test, y_pred)
        EERS.append(eer)

    return [statistics.mean(EERS), statistics.stdev(EERS)]


for sample_size in [
    10,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
    100,
    150,
    200,
    250,
    300,
    350,
    400,
]:
    results = Parallel(n_jobs=args.jobs)(
        [delayed(user_eer)(sample_size) for i in range(args.repetitions)]
    )

    eers = []
    stds = []
    for res in results:
        eers.append(res[0])
        stds.append(res[1])

    utils.export_csv_two_columns(
        "../results/" + args.classifier + "/p1_subsamples/subsample_" + str(sample_size) + "_users.csv",
        "eer",
        "std",
        eers,
        stds,
    )
