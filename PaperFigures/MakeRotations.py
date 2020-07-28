import os
import pickle
from multiprocessing import Pool

import DriftMLP
from DriftMLP.rotations import random_ll_rot

rotations = [random_ll_rot() for i in range(10)]  #
file = os.environ['DRIFTFILE']


def get_network(rot):
    drift_kwargs = {'variables': ['position', 'drogue', 'datetime'],
                    'drop_na': False,
                    'drogue': True,
                    'lon_lat_transform': rot}
    net = DriftMLP.network_from_file(fname=file, drift_kwargs=drift_kwargs)
    return net


p = Pool(19)
to_store = list(p.map(get_network, rotations))
pickle.dump(to_store, open(f'rotations_{len(rotations)}.p', 'wb'))
p.close()
