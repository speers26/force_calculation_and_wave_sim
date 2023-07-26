from wavesim.distest import LoadDistEst
from wavesim.spectrum import SeaState, Jonswap
import numpy as np

num_sea_states = 100
hs = np.tile(15, num_sea_states)
tp = np.tile(10, num_sea_states)
z_values = np.linspace(-100, 50, 150)

ss = SeaState(hs=hs, tp=tp, spctr_type=Jonswap)

np.random.seed(1)

loadEst = LoadDistEst(sea_state=ss, z_values=z_values)
loadEst.compute_cond_crests()
loadEst.compute_kinematics()
loadEst.compute_load()
loadEst.compute_sea_state_max()
loadEst.compute_is_distribution()
loadEst.compute_density()
loadEst.plot_density()
print(loadEst.eval_pdf(np.array([1, 2])))

print(np.sum(loadEst.dx * loadEst.pdf))