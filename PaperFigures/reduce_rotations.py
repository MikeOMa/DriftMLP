import pickle

nets = pickle.load(open('rotations_500.p', 'rb'))[:100]
pickle.dump(nets[:100],open('rotations_100.p', 'wb'))
