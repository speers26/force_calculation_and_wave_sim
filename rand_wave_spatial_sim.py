import numpy as np
import matplotlib.pyplot as plt

def random_wave_surface(omega_range:np.ndarray, phi_range:np.ndarray, t:np.ndarray, x_range:np.ndarray, y_range:np.ndarray):
    """returns random wave surface with frequency direction spectrum defined below

    Args:
        omega_range (np.ndarray): values of angular frequency to include
        phi_range (np.ndarray): values of direction to include
        t (np.ndarray): time (scalar)
        x_range (np.ndarray): range of x to evaluate over (forms a grid with y_range)
        y_range (np.ndarray): range of y to evaluate over (forms a grid with x_range)
    """
    np.random.seed(1)

    A = np.multiply(np.random(0, 1, size = (phi_num, om_num)), np.sqrt(Dr_spctrm * d_om * d_phi)) 
    B = np.multiply(np.random(0, 1, size = (phi_num, om_num)), np.sqrt(Dr_spctrm * d_om * d_phi)) 

    X, Y = np.meshgrid(x_range, y_range)

    eta = np.empty(y_range, x_range)

    # for i_x, x in enumerate(x_range):
    #     for i_y, y in enumerate(y_range):
    #         eta[i_y, i_x] = ##TODO finish this


def frq_dr_spctrm(omega:np.ndarray, phi:np.ndarray, alpha:np.ndarray, om_p:np.ndarray, gamma:np.ndarray,
                    r:np.ndarray, phi_m:np.ndarray, beta:np.ndarray, nu:np.ndarray, sig_l:np.ndarray, sig_r:np.ndarray):
    """returns frequency direction spectrum

    Args:
        omega (np.ndarray): angular frequency
        phi (np.ndarray): direction (from)
        alpha (np.ndarray): scaling parameter
        om_p (np.ndarray): peak ang freq
        gamma (np.ndarray): peak enhancement factor
        r (np.ndarray): spectral tail decay index
        phi_m (np.ndarray): mean direction
        beta (np.ndarray): limiting peak separation
        nu (np.ndarray): peak separation shape
        sig_l (np.ndarray): limiting angular width
        sig_r (np.ndarray): angular width shape
    """
    dens = sprd_fnc(omega, phi, om_p, phi_m, beta, nu, sig_l, sig_r) * d_jonswap(omega, alpha, om_p, gamma, r)

    return dens

def sprd_fnc(omega:np.ndarray, phi:np.ndarray, om_p:np.ndarray, phi_m:np.ndarray, beta:np.ndarray, nu:np.ndarray, sig_l:np.ndarray, sig_r:np.ndarray):
    """returns bimodal wrapped Gaussian spreading function D(omega, phi)

    Args:
        omega (np.ndarray): angular frequency
        phi (np.ndarray): direction (from)
        om_p (np.ndarray): peak ang freq
        phi_m (np.ndarray): mean direction
        beta (np.ndarray): limiting peak separation
        nu (np.ndarray): peak separation shape
        sig_l (np.ndarray): limiting angular width
        sig_r (np.ndarray): angular width shape
    """
    k_num = 200
    k_range = np.linspace(start = -k_num/2, stop = k_num/2, num = k_num + 1)

    phi_m1 = phi_m + beta * np.exp(-nu * min(om_p / np.abs(omega), 1)) / 2
    phi_m2 = phi_m - beta * np.exp(-nu * min(om_p / np.abs(omega), 1)) / 2
    phi_arr = np.array([phi_m1, phi_m2])

    sigma = sig_l - sig_r / 3 * (4 * (om_p / np.abs(omega)) ** 2 - (om_p / np.abs(omega)) ** 8)

    nrm_cnst = (2 * sigma * np.sqrt(2 * np.pi)) ** -1
    dens_k = np.empty(k_num + 1)

    for i_k, k in enumerate(k_range):
        exp_term = np.exp( -0.5 * ((phi - phi_arr - 2 * np.pi * k) / sigma) ** 2)
        dens_k[i_k] = np.sum(exp_term)

    dens = nrm_cnst * np.sum(dens_k)

    return dens

def d_jonswap(omega:np.ndarray, alpha:np.ndarray, om_p:np.ndarray, gamma:np.ndarray, r:np.ndarray):
    """jonswap density using formulation used in Jake's paper

    Args:
        omega (np.ndarray): angular frequency
        alpha (np.ndarray): scaling parameter
        om_p (np.ndarray): peak ang freq
        gamma (np.ndarray): peak enhancement factor
        r (np.ndarray): spectral tail decay index
    """

    delta = np.exp( -(2 * (0.07 + 0.02 * (om_p > np.abs(omega)) )) ** -2 * (np.abs(omega) / om_p - 1) ** 2)

    dens = alpha * omega ** -r * np.exp( -r / 4 * (np.abs(omega) / om_p ) ** -4) * gamma ** delta

    return dens


if __name__ == '__main__':

    ### pars set accoring to 'classic example' given in 
    # https://www.mendeley.com/reference-manager/reader/6c295827-d975-39e4-ad43-c73f0f51b060/21c9456c-b9ef-e1bb-1d36-7c1780658222
    alpha = 0.7
    om_p = 0.8
    gamma = 3.3
    r = 5
    phi_m = np.pi
    beta = 4
    nu = 2.7
    sig_l = 0.55
    sig_r = 0.26

    om_num = 50
    om_range = np.linspace(start = 1e-3, stop = 3, num = om_num)

    phi_num = 100
    phi_range = np.linspace(start = 0, stop = 2 * np.pi, num = phi_num)

    # ### plotting contours

    D_sprd = np.empty((phi_num, om_num))
    for i_o, om in enumerate(om_range):
        for i_p, phi in enumerate(phi_range):
            D_sprd[i_p, i_o] = sprd_fnc(om, phi, om_p, phi_m, beta, nu, sig_l, sig_r)

    d_om = om_range[1] - om_range[0]
    d_phi = phi_range[1] - phi_range[0]

    sprd_areas = np.sum(d_om * d_phi * D_sprd, axis=1)
    print(sum(sprd_areas)) ## should this integrate to 1?

    jnswp_dns = np.empty(om_num)
    for i_o, om in enumerate(om_range):
        jnswp_dns[i_o] = d_jonswap(om, alpha, om_p, gamma, r)

    jnswp_area = sum(d_om * jnswp_dns)
    print(jnswp_area)

    Dr_spctrm = np.empty((phi_num, om_num))
    for i_o, om in enumerate(om_range):
        for i_p, phi in enumerate(phi_range):
            Dr_spctrm[i_p, i_o] = frq_dr_spctrm(om, phi, alpha, om_p, gamma, r, phi_m, beta, nu, sig_l, sig_r)

    spctrm_vol = sum(sum(d_om * d_phi * Dr_spctrm))
    print(spctrm_vol)

    X, Y = np.meshgrid(om_range, phi_range)

    plt.figure()

    plt.subplot(1,3,1)
    plt.contour(X, Y, Dr_spctrm, levels = 20)

    plt.subplot(1,3,2)
    plt.plot(om_range, jnswp_dns)

    plt.subplot(1,3,3)
    plt.contour(X, Y,  D_sprd, levels = 20)

    plt.show()

