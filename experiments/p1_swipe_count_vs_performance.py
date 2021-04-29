import statistics
import argparse
import utils as utils
import csv

from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle
from joblib import Parallel, delayed
from collections import defaultdict
from datetime import date,datetime

parser = argparse.ArgumentParser()
parser.add_argument('-dataset', default="../data/data.csv")
parser.add_argument('-random_state', default=42, type=int) # random state for reproducability
parser.add_argument('-jobs', default=6, type=int) # parallelization parameter
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(dataset_path=args.dataset, game="swipe", direction="left", random_state=args.random_state)

EERS = []
user_eer_map = {}

users_batch = defaultdict(list)
with open('../data/tables/measurements.csv') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    next(csvreader)
    for row in csvreader:
        users_batch[row[1]].append(int(datetime.fromtimestamp(int(row[3])).strftime('%m%d')))

long_batch = []
short_batch = []
for user in users_batch:
    if users_batch[user][0] <= 521:
        long_batch.append(user)
    else:
        short_batch.append(user)

def user_eer(user):
    if len(user_touches[user]) < 10:
        return

    # Split into 2 equal user groups
    users_copy = list(users.copy())
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

    return [eer, len(user_touches[user]), user] 

eer_swipes_pairs = Parallel(n_jobs=args.jobs)([delayed(user_eer)(user) for user in users])
eers = []
swipes = []
batch = []

for i in range(len(eer_swipes_pairs)):
    eers.append(eer_swipes_pairs[i][0])
    swipes.append(eer_swipes_pairs[i][1])

    if eer_swipes_pairs[i][2] in short_batch:
        batch.append(0)
    else:
        batch.append(1)

utils.export_csv_three_columns('../results/general/swipes_count_vs_performance.csv', 'eer', 'swipes', 'batch', eers, swipes, batch)
