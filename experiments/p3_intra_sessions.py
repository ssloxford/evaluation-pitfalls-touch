import statistics
import argparse
import utils as utils

from sklearn import svm
from sklearn.preprocessing import StandardScaler

parser = argparse.ArgumentParser()
parser.add_argument('-dataset', default="../data/data.csv")
parser.add_argument('-random_state', default=42, type=int) # random state for reproducability
args = parser.parse_args()

users, user_touches, user_touches_shuffled, session_user_touches = utils.preprocessing(dataset_path=args.dataset, game="swipe", direction="left", random_state=args.random_state)

EERS = []
user_eer_map = {}

for user in users:
    session_eer = []

    if len(session_user_touches[user]) < 2:
        continue


    # Split into 2 equal user groups
    users_copy = list(users.copy())
    users_copy.remove(user)
    user_groups = utils.partition_list(users_copy)


    for i in range(len(session_user_touches[user])):
        X_train, X_test, y_train, y_test = utils.intra_session(session_user_touches, user_touches_shuffled, user, train_users=user_groups[0], test_users=user_groups[1], session=i)

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        clf = svm.SVC(gamma='scale')
        clf.fit(X_train, y_train)
        y_pred = clf.decision_function(X_test)
        
        eer = utils.calculate_eer(y_test, y_pred)
        session_eer.append(eer)

    EERS.append(statistics.mean(session_eer))


utils.export_csv('../results/p3_training_selection/intra_session.csv', EERS)