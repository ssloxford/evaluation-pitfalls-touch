import random
import pandas as pd
import math

from sklearn.metrics import accuracy_score, roc_curve
from scipy.optimize import brentq
from scipy.interpolate import interp1d
from sklearn.utils import shuffle

def preprocessing(dataset_path, game, direction, random_state=42, randomize_sessions=False, phone="all", session_length=-1):
    state = random_state
    game = game  
    direction = direction 

    features = pd.read_csv(dataset_path)
    if phone == "all":
        if game == "all":
            features = features
        else:
            features = features.loc[(features['gametype'] == game) & (features['direction'] == direction)]
    else:
        features = features.loc[(features['gametype'] == game) & (features['direction'] == direction) & (features['phone_model'] == phone)]
    features = features.dropna()

    users = features.uuid.unique()
    user_touches = {}
    user_touches_shuffled = {}
    session_user_touches = {}

    for user in users:
        user_data = features.loc[features['uuid'] == user]
        sessions = user_data.measurement_id.unique()
        
        # Is order of sessions kept linear
        if randomize_sessions:
            random.Random(state).shuffle(sessions)
        
        # Skip users for session_length experiment
        if session_length != -1 and len(sessions) != session_length:
            continue

        session_user_touches[user] = []
        
        for session in sessions:
            session_user_touches[user].append(user_data.loc[user_data['measurement_id'] == session, 'duration':'midCover'].values.tolist())
        
        user_touches[user] = user_data.loc[:, 'duration':'midCover'].values.tolist()
        
    for user in users:
        if user in session_user_touches:
            user_touches_shuffled[user] = user_touches[user].copy()
            random.Random(state).shuffle(user_touches_shuffled[user])

    return users, user_touches, user_touches_shuffled, session_user_touches


def export_csv(storage_path, eers):
    f = open(storage_path, "w")
    f.write("eer\n")

    for i in range(len(eers)):
        if not eers[i] == None: 
            f.write(str(eers[i]) + '\n')

    f.close()


def export_csv_two_columns(storage_path, column_1, column_2, eers_1, eers_2):
    f = open(storage_path, "w")
    f.write(column_1 + ',' + column_2 + '\n')

    for i in range(len(eers_1)):
        if (not eers_1[i] == None) and (not eers_2[i] == None): 
            f.write(str(eers_1[i]) + "," + str(eers_2[i]) + '\n')

    f.close()

def export_csv_three_columns(storage_path, column_1, column_2, column_3, eers_1, eers_2, eers_3):
    f = open(storage_path, "w")
    f.write(column_1 + ',' + column_2 + ',' + column_3 + '\n')

    for i in range(len(eers_1)):
        if (not eers_1[i] == None) and (not eers_2[i] == None) and (not eers_3[i] == None): 
            f.write(str(eers_1[i]) + "," + str(eers_2[i]) + "," + str(eers_3[i]) + '\n')

    f.close()



def calculate_eer(y_test, y_pred):
    fpr, tpr, thresholds = roc_curve(y_test, y_pred)

    eer = brentq(lambda x : 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
    thresh = interp1d(fpr, thresholds)(eer)

    return eer


# Splits the list in two
def partition_list(list_in):
    random.shuffle(list_in)
    return [list_in[i::2] for i in range(2)]

# Balances positive and negative examples
def balance_examples(X_positive, X_negative):
    
    # Truncate negative or positive class as needed, then combine

    if len(X_negative) > len(X_positive):
        X_negative = X_negative[:len(X_positive)]
    elif len(X_negative) < len(X_positive):
        X_positive = X_positive[:len(X_negative)]

    X = X_negative + X_positive
    y = ([0] * len(X_negative)) + ([1] * len(X_positive))

    return X, y

def intra_session(user_touches, user_touches_shuffled, user, train_users, test_users, session):
    p_strokes = len(user_touches[user][session])
    p_strokes_80 = int(p_strokes*0.8)

    # Generate positive train examples
    X_train_positive = user_touches[user][session][:p_strokes_80]
 
    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate positive test examples
    X_test_positive = user_touches[user][session][p_strokes_80:]
    
    # Generate negative testing examples
    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test =  X_test_negative + X_test_positive
    y_test= ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, X_test, y_train, y_test


def train_session_test_session(user_touches, train_session, test_session, user_touches_shuffled, user, train_users, test_users):
    # Generate positive train examples
    X_train_positive = user_touches[user][train_session].copy()

    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate positive test examples
    X_test_positive = user_touches[user][test_session].copy()

    # Generate negative class testing examples
    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test = X_test_negative + X_test_positive
    y_test= ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, X_test, y_train, y_test


def one_class(user_touches, user_touches_shuffled, user, split=0.8):
    X_train = []
    X_test = []
    y_test = []

    # Generate positive class examples
    X_user = user_touches[user]

    # Generate negative class training examples
    X_attackers = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in user_touches_shuffled:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_attackers.append(user_touches_shuffled[u][depth])
                added = True


        depth += 1

    if len(X_attackers) > len(X_user):
        X_attackers = X_attackers[:len(X_user)]
    elif len(X_attackers) < len(X_user):
        X_user = X_user[:len(X_attackers)]

    strokes = len(user_touches[user])
    strokes_train = int(strokes*split)
    strokes_test = int(strokes-strokes_train)

    X_train = X_user[:strokes_train]

    X_test = X_user[strokes_train:] + X_attackers[strokes_train:]
    y_test = ([1] * strokes_test) + ([-1] * strokes_test)

    return X_train, X_test, y_test
      

def combined_sessions(user_touches, user_touches_shuffled, user, train_users, test_users, randomized=False, split=0.8):
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    if randomized == True:
        user_swipes = user_touches_shuffled
    else:
        user_swipes = user_touches

    strokes = len(user_touches[user])
    strokes_train = int(strokes*split)

    # Generate positive class training examples
    X_train_positive = user_swipes[user][:strokes_train]

    # Generate negative class training examples
    X_train_negative = []
    depth = 0
    added = True
    while added:
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate positive class testing examples
    X_test_positive = user_swipes[user][strokes_train:]

    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test = X_test_negative + X_test_positive 
    y_test= ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, y_train, X_test, y_test


def combined_sessions_subsampled_include_attacker(user_touches, user_touches_shuffled, user, subsampled_users, randomized=False, split=0.8):
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    if randomized == True:
        user_swipes = user_touches_shuffled
    else:
        user_swipes = user_touches

    # Generate positive class examples
    X_user = user_swipes[user].copy()

    # Generate negative class examples
    # Add equal number of samples from each non-target user, up to number of samples for "smallest" user
    X_attackers = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in subsampled_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_attackers.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    # Cut off negative/positive class samples to balance classes
    # This should largely maintain even number of samples for each attacker in negative class
    if len(X_attackers) > len(X_user):
        X_attackers = X_attackers[:len(X_user)]
    elif len(X_attackers) < len(X_user):
        X_user = X_user[:len(X_attackers)]

    strokes = len(X_user)
    strokes_train = int(strokes*split)
    strokes_test = int(strokes-strokes_train)

    X_train = X_user[:strokes_train] + X_attackers[:strokes_train]
    y_train = ([1] * strokes_train) + ([0] * strokes_train)

    X_test = X_user[strokes_train:] + X_attackers[strokes_train:]
    y_test = ([1] * strokes_test) + ([0] * strokes_test)

    return X_train, y_train, X_test, y_test


def combined_sessions_aggregation(user_touches, user_touches_shuffled, user, train_users, test_users, aggregation_length, split=0.8):
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    strokes = len(user_touches[user])
    strokes_train = int(strokes*split)

    # Generate positive class examples
    X_train_positive = user_touches[user][:strokes_train]

    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate testing examples
    for i in range(len(user_touches[user][strokes_train:])-aggregation_length-1):
        X_test.append(user_touches[user][strokes_train+i:strokes_train+i+aggregation_length])
        y_test.append(1)

    X_test_negative = []
    i = 0
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth + aggregation_length:
                X_test_negative.append(user_touches_shuffled[u][depth:depth+aggregation_length])
                y_test.append(0)
                added = True

        depth += aggregation_length

    X_test.extend(X_test_negative)
    
    return X_train, y_train, X_test, y_test


def combined_sessions_sanitize(user_touches, user_touches_shuffled, session_user_touches, user, train_users, test_users, early, sanitize_length, split=0.8):
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    legitimate_user_touches = []

    if early:
        for i in range(sanitize_length):
            legitimate_user_touches.extend(session_user_touches[user][i])
    else:
        for i in range(31-sanitize_length,len(session_user_touches[user])):
            legitimate_user_touches.extend(session_user_touches[user][i])

    strokes = len(legitimate_user_touches)
    strokes_train = int(strokes*split)

    # Generate positive class examples
    X_train_positive = legitimate_user_touches[:strokes_train]

    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate testing examples
    X_test_positive = legitimate_user_touches[strokes_train:]

    # Generate negative class testing examples
    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test = X_test_negative + X_test_positive
    y_test = ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, y_train, X_test, y_test


def combined_sessions_performed(user_touches, user_touches_shuffled, session_user_touches, user, train_users, test_users, sanitize_length, split=0.8):
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    legitimate_user_touches = []

    for i in range(sanitize_length):
        legitimate_user_touches.extend(session_user_touches[user][i])

    strokes = len(legitimate_user_touches)
    strokes_train = int(strokes*split)

    # Generate positive class examples
    X_train_positive = legitimate_user_touches[:strokes_train]

    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    # Generate testing examples
    X_test_positive = legitimate_user_touches[strokes_train:]

    # Generate negative class testing examples
    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test = X_test_negative + X_test_positive
    y_test = ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, y_train, X_test, y_test


def dedicated_sessions(user_touches, user_touches_shuffled, user, train_users, test_users, randomized=False, session_split=0.8):
    n_training_sessions = math.floor(len(user_touches[user])*session_split)

    if randomized == True:
        user_swipes = user_touches[user].copy()
        random.shuffle(user_swipes)
    else:
        user_swipes = user_touches[user]

    X_train_positive = []

    # Generate positive training data
    for i in range(n_training_sessions):
        X_train_positive += user_swipes[i]

    # Generate negative training data
    X_train_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in train_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_train_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_train, y_train = balance_examples(X_train_positive, X_train_negative)

    X_test_positive = []

    # Generate positive testing data
    for i in range(n_training_sessions,len(user_swipes)):
        X_test_positive += user_swipes[i]

    # Generate negative class testing examples
    X_test_negative = []
    depth = 0
    added = True
    while (added):
        added = False
        for u in test_users:
            if u != user and len(user_touches_shuffled[u]) > depth:
                X_test_negative.append(user_touches_shuffled[u][depth])
                added = True

        depth += 1

    X_test = X_test_negative + X_test_positive
    y_test= ([0] * len(X_test_negative)) + ([1] * len(X_test_positive))

    return X_train, X_test, y_train, y_test
