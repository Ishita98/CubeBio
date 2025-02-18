# Import necessary libraries
from cmapPy.pandasGEXpress.parse import parse
import numpy as np
import json
from collections import Counter
import sys


def get_target_labels(working_data, mydict):
    print("Creating target labels")
    target = []
    cnt = 0
    for i in working_data.columns:
        for pert, collist in mydict.items():
            if i in collist:
                if (cnt % 1000 == 0):
                    print(cnt, end=' ')
                target.append(pert)
                cnt += 1
    return target


# Create 2 dictionaries
# pert2profile: perturbagen: number of profiles for that particular perturbagen
# location_pert: perturbagen: location of 1st profile of perturbagen

def create_pert2profile(data):
    print("Creating pert2profile")
    return Counter(data.target)


def create_location_pert(data):
    print("creating location_pert")
    location_pert = dict()
    cnt = 0
    for i in set(np.unique(data.target.values)):
        loc = np.where(data['target'] == i)[0][0]
        location_pert[i] = loc
        if (cnt % 100 == 0):
            print(cnt, end=' ')
        cnt += 1
    return location_pert


def gctx2pd(gctxfile, jsonfile):
    obj = parse(gctxfile)
    data = obj.data_df
    with open(jsonfile, 'r') as fp:
        metadata = json.load(fp)
    return data, metadata


# Split list of all perturbagens into (train-80%) and (test-20%)
def train_and_test_perturbagens(list_of_perturbagens):
    rng = np.random
    train = rng.choice(list_of_perturbagens, size=(len(list_of_perturbagens) * 4 // 5,), replace=False)

    def Diff(li1, li2):
        li_dif = [i for i in li1 if i not in li1 or i not in li2]
        return li_dif

    test = Diff(list_of_perturbagens, train)
    return train, test


def generate_triplets(data, pert):
    same = data[data.target == pert].iloc[:, 0:978].sample(2)
    diff = data[data.target != pert].iloc[:, 0:978].sample(1)
    return np.asarray(same.iloc[0, :]), np.asarray(same.iloc[1, :]), np.asarray(diff.iloc[0, :])


def generate_data(data, test_pert, lenperpert, dim=978):
    batch_size = len(test_pert) * lenperpert
    print("batch_size: ", batch_size)
    triplets = [np.zeros((batch_size, dim)) for i in range(3)]
    i = 0
    for pert in test_pert:
        for num in range(lenperpert):
            if (i >= batch_size):
                break
            # anchor, same, different
            triplets[0][i, :], triplets[1][i, :], triplets[2][i, :] = generate_triplets(data, pert)
            i += 1
            sys.stdout.write("\r%d/%d" % (i, batch_size))

    return np.asarray(triplets)
