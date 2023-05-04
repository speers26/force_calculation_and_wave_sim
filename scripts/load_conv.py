import numpy as np
import pandas as pd
import wavesim.distest as dist
import wavesim.spectrum as spctr
import matplotlib.pyplot as plt

env_probs = pd.read_csv('scripts/env_probs.csv')
env_probs[env_probs.p != 0]

num_sea_states = 20
z_values = np.linspace(-100, 50, 50)

x_num = 100
X = np.linspace(0, 2, num=x_num)

np.random.seed(1)

results = np.empty((env_probs.shape[0], x_num))

for i_s in range(env_probs.shape[0]):
    print(i_s)
    row = env_probs.loc[i_s]
    hs = np.tile(row['hs'], num_sea_states)
    s2 = np.tile(row['s2'], num_sea_states)
    tp = np.sqrt((hs*2*np.pi)/(s2*9.81))
    ss = spctr.SeaState(hs=hs, tp=tp, spctr_type=spctr.Jonswap)

    loadEst = dist.LoadDistEst(sea_state=ss, z_values=z_values)
    loadEst.compute_cond_crests()
    loadEst.compute_kinematics()
    loadEst.compute_load()
    loadEst.compute_sea_state_max()
    loadEst.compute_is_distribution(X=X)

    results[i_s, :] = loadEst.cdf

np.savetxt("scripts/results.csv", results, delimiter=",")
p_array = np.array(env_probs['p'])
f_cdf = np.sum(results * p_array[:, np.newaxis], axis=0)

plt.figure()
plt.subplot(2, 1, 1)
plt.plot(X, f_cdf)
plt.subplot(2, 1, 2)
plt.plot(X, np.log10(1-f_cdf))
plt.show()
