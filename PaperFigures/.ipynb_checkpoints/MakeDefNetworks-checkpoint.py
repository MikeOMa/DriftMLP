import os
import pickle
from multiprocessing import Pool

import DriftMLP
from DriftMLP.rotations import random_ll_rot

file = os.environ['DRIFTFILE']

drogue_setting= [True, False, None]
def make_default(drogue):
    drift_kwargs = {'variables': ['position', 'drogue', 'datetime'],
                        'drop_na': False,
                        'drogue': drogue}
    net = DriftMLP.network_from_file(fname=file, drift_kwargs=drift_kwargs, store_story=True)

p = Pool(3)
to_store = list(p.map(make_default, drogue_setting))
dict_of_networks = {drogue: net for net in to_store}
pickle.dump(dict_of_networks, open(f'default_networks.p', 'wb'))
p.close()