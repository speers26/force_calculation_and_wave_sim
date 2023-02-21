import numpy as np
import matplotlib.pyplot as plt
import wavesim_functions as wave


if __name__ == "__main__":

    np.random.seed(12345)
    write = False
    write_con = False

    # set up wave conditions
    hs = 25
    tp = 12
    depth = 100
    cond = False
    a = 0

    # set up arrays
    z_num = 150
    z_range = np.linspace(-depth, 50, z_num)
    dz = z_range[1] - z_range[0]

    num_sea_states = 2000
    sea_state_hours = 1
    full_period = 60**2 * sea_state_hours  # total time range in seconds
    waves_per_sea_state = full_period/tp

    freq = 4.00  # number of sample points per second
    nT = np.floor(full_period*freq)  # number of time points to evaluate
    t_num = int(nT)  # to work with rest of the code

    dt = 1/freq  # time step is determined by frequency
    t_range = np.linspace(-nT/2, nT/2 - 1, int(nT)) * dt  # centering time around 0

    f_range = np.linspace(1e-3, nT - 1, int(nT)) / (nT / freq)  # selecting frequency range from 0 to freq
    om_range = f_range * (2*np.pi)

    # get jonswap density
    jnswp_dens = wave.djonswap(f_range, hs, tp)

    # if we want new wave data
    if write:
        # set up arrays (don't actually need to do this for all)
        eta = np.empty([num_sea_states, t_num])

        # populate arrays
        for i in range(num_sea_states):
            print(i)
            eta[i, :], _, _, _, _ = wave.fft_random_wave_sim(z_range, depth, a, om_range, jnswp_dens, cond)

        np.savetxt('eta.txt', eta, delimiter=' ')

    # if we want to use the old wave data
    else:
        # read data from the text files
        eta = np.loadtxt('eta.txt')

    # get max crest from each sea state
    two_hour_max_crests = np.empty(num_sea_states)
    for i_s in range(num_sea_states):
        slice = eta[i_s, :]
        two_hour_max_crests[i_s] = max(slice)

    # now do for conditional sim
    cond = True

    # get proposal sample and density of crest
    CoHmin = 0
    CoHmax = 2
    CoHnum = num_sea_states
    CoH = np.random.uniform(low=CoHmin, high=CoHmax, size=CoHnum)
    g = 1/((CoHmax-CoHmin)*hs)  # density for crest heights not CoH
    r_crests = np.sort(CoH * hs)

    # will simulate sea states of 2 minutes
    cond_state_min = 2
    cond_period = 60*cond_state_min
    waves_per_cond_state = cond_period/tp
    cond_per_full_state = sea_state_hours * 60 / cond_state_min

    # redo arrays
    freq = 4.00  # number of sample points per second
    nT = np.floor(cond_period*freq)  # number of time points to evaluate
    t_num = int(nT)  # to work with rest of the code

    dt = 1/freq  # time step is determined by frequency
    t_range = np.linspace(-nT/2, nT/2 - 1, int(nT)) * dt  # centering time around 0

    f_range = np.linspace(1e-3, nT - 1, int(nT)) / (nT / freq)  # selecting frequency range from 0 to freq
    om_range = f_range * (2*np.pi)

    # redo jonswap density
    jnswp_dens = wave.djonswap(f_range, hs, tp)

    if write_con:
        # generate wave data and write to text files
        eta = np.empty([num_sea_states, t_num])
        for i in range(num_sea_states):
            print(i)
            a = CoH[i] * hs
            eta[i, :], _, _, _, _ = wave.fft_random_wave_sim(z_range, depth, a, om_range, jnswp_dens, cond)

        np.savetxt('eta_con.txt', eta, delimiter=' ')
        # np.savetxt('h_v_con.txt', u_x, delimiter=' ')

    else:
        # read wave date from txt files
        eta = np.loadtxt('eta_con.txt')

    # get cond max crests
    cond_max_crests = np.empty(num_sea_states)
    for i_s in range(num_sea_states):
        slice = eta[i_s, :]
        cond_max_crests[i_s] = max(slice)

    # evaluated the 3 distributions at these points
    x = np.linspace(0, 2*hs, num=100)

    # get weights
    f = wave.rayleigh_pdf(r_crests, hs)
    fog = f/g

    # get simple IS dist
    sim_is_crest_cdf = np.empty(x.shape)
    for i_x, c in enumerate(x):
        sim_is_crest_cdf[i_x] = np.sum((r_crests<c) * fog)/np.sum(fog)

    # get true dist
    rayleigh_cdf = wave.rayleigh_cdf(x, hs)

    # get IS crest distribution
    crest_cdf_is_two_min_max = np.empty(x.shape)
    for i_c, c in enumerate(x):
        crest_cdf_is_two_min_max[i_c] = np.sum((cond_max_crests < c) * fog)/np.sum(fog)

    crest_cdf_is_sea_st_max = crest_cdf_is_two_min_max**cond_per_full_state

    crest_cdf_two_min_max = sim_is_crest_cdf**waves_per_cond_state
    rayleigh_cdf_two_min_max = rayleigh_cdf**waves_per_cond_state

    crest_cdf_sea_st_max = sim_is_crest_cdf**waves_per_sea_state
    rayleigh_cdf_sea_st_max = rayleigh_cdf**waves_per_sea_state

    plt.figure()
    plt.plot(r_crests, np.sort(cond_max_crests), '.')
    plt.plot([0, 50], [0, 50], 'k')
    plt.show()

    plt.figure()
    plt.plot(t_range, eta[np.argmax(cond_max_crests), :])
    plt.show()

    print(CoH[np.argmax(cond_max_crests)] * hs)

    plt.figure()
    plt.subplot(1, 3, 1)
    plt.plot(x/hs, np.log10(1-sim_is_crest_cdf), '-k')
    plt.plot(x/hs, np.log10(1-rayleigh_cdf), '-r')

    plt.subplot(1, 3, 2)
    plt.plot(x/hs, np.log10(1-crest_cdf_sea_st_max), '-k')
    plt.plot(x/hs, np.log10(1-rayleigh_cdf_sea_st_max), '-r')
    plt.plot(x/hs, np.log10(1-crest_cdf_is_two_min_max), '--g')

    plt.subplot(1, 3, 3)
    plt.plot(x/hs, np.log10(1-crest_cdf_sea_st_max), '-k')
    plt.plot(x/hs, np.log10(1-rayleigh_cdf_sea_st_max), '-r')
    plt.plot(x/hs, np.log10(1-crest_cdf_is_sea_st_max), '--g')
    plt.show()