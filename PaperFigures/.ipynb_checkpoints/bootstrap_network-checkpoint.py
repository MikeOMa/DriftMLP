import pickle
import DriftMLP
import numpy as np
import pandas as pd
networks = pickle.load(open('default_networks.p', 'rb'))

### Only use drogued drifters
network = networks[True]
postfix = 'drg'
### Our example locations are in locations.txt
stations = np.loadtxt("locations.txt", delimiter=',')
stations = pd.DataFrame(stations, index=range(1, 8))
stations.columns = ['Longitude', 'Latitude']
stations['h3'] = DriftMLP.helpers.return_h3_inds([i[['Longitude', 'Latitude']].to_list() for _,i in stations.iterrows()])
stations.loc[:,['Longitude', 'Latitude']].to_latex()

origins = stations['h3'].to_list()

def get_boot_res(seed):
    np.random.seed(seed)
    boot_network = DriftMLP.BootstrapNetwork(network)
    all_paths = [DriftMLP.shortest_path.get_all_paths(boot_network, origin, origins) for origin in origins]
    return all_paths

from multiprocessing import Pool
n_boot = 200
seeds = np.random.randint(0,100000, size =n_boot)
p = Pool(4)
res = list(p.map(get_boot_res, seeds))
pickle.dump(res, open(f'bootstrapped_{postfix}_{len(seeds)}.p', 'wb'))
p.close()