import statistics
import argparse
import utils as utils
import random
import numpy as np, scipy.stats as st

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed

parser = argparse.ArgumentParser()
parser.add_argument('-dataset', default="../data/data.csv")
parser.add_argument('-random_state', default=42, type=int) # random state for reproducability
parser.add_argument('-jobs', default=6, type=int) # parallelization parameter
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(dataset_path=args.dataset, game="swipe", direction="left", random_state=args.random_state)

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

        X_train, y_train, X_test, y_test = utils.combined_sessions(user_touches, user_touches_shuffled, user, train_users=user_groups[0], test_users=user_groups[1])

        X_train, y_train = shuffle(X_train, y_train, random_state=args.random_state)
        X_test, y_test = shuffle(X_test, y_test, random_state=args.random_state)

        scaler = StandardScaler()
        X_train = scaler.fit_transform( X_train )
        X_test = scaler.transform( X_test )

        clf = svm.SVC(gamma='scale')
        clf.fit(X_train, y_train)
        y_pred = clf.decision_function(X_test)

        eer = utils.calculate_eer(y_test, y_pred)
        EERS.append(eer)

    EERS = np.array(EERS)*100
    return [statistics.mean(EERS), statistics.stdev(EERS), statistics.mean(EERS)-st.t.interval(0.95, len(EERS)-1, loc=np.mean(EERS), scale=st.sem(EERS))[0]]

for sample_size in [70,19,73,50,68,55,71,34,30]: 
    results = Parallel(n_jobs=args.jobs)([delayed(user_eer)(sample_size)])

    print(sample_size)
    print(results)
    print("")