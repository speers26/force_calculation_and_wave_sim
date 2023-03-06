'''
Code for generating Wave Spectra and associated functionality

'''
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np


@dataclass
class Spectrum(ABC):
    """ Wave spectrum class
    """
    frequency: np.array
    g = 9.81
    density = np.ndarray = None

    @abstractmethod
    def compute_density(self):
        """returns density for given frequency range

        output sotre in density
        """

    @property
    def omega(self):
        """ Get angular frequecy"""
        return self.frequency * 2 * np.pi  # TODO CHECK THIS

    @property
    def df(self):
        return self.frequency[1] - self.frequency[0]

    def kth_moment(self, k: int):
        """function to return the kth moment of the given spectrum evaulated at given frequencies

        Args:
            k (int): moment

        Returns:
            k_integral (_type_): integral equal to the kth moment
        """

        k_integral = np.sum(self.density * (self.frequency ** k) * self.df)

        return k_integral

    def random_waves_acf(self, tau: np.ndarray):
        """find acf function of the gaussian random wave surface with given spectrum

        Args:
            tau (np.ndarray): lags []

        Returns:
            acf (np.ndarray): auto correlation
        """

        spctrl_area = self.kth_moment(0)

        outer_ft = np.outer(self.frequency, tau)    # (n_freq x tau_length)

        acf_mat = np.cos(2 * np.pi * outer_ft) * self.density[:, np.newaxis] * self.df / spctrl_area    # (n_freq x tau_length)
        acf_vec = np.sum(acf_mat, axis=0)   # sum over columns to give (1 x tau_length)

        return acf_vec


@dataclass
class Jonswap(Spectrum):
    """ JONSWAP specific functions
    """
    hs: np.array
    tp: np.array
    gamma: np.array = 2
    sigma_a: np.array = 0.07
    sigma_b: np.array = 0.09

    def compute_density(self):

        fp = 1. / self.tp

        df = self.frequency[1] - self.frequency[0]

        sigma = (self.frequency < fp) * self.sigma_a + (self.frequency >= fp) * self.sigma_b

        gamma_coeff = self.gamma ** np.exp(-0.5 * (((self.frequency / fp - 1)/sigma) ** 2))
        self.density = self.g ** 2 * (2 * np.pi) ** -4 * self.frequency ** -5 \
            * np.exp(-1.25 * (self.tp*self.frequency) ** -4) * gamma_coeff

        area = sum(self.density *df)

        self.density *= self.hs ** 2 / (16 * area)

        return self


@dataclass
class AltJonswap(Jonswap):
    """ JONSWAP specific functions using formulation used in Jake's paper

    TODO: maybe create unscaled_density and then commmon density
    """
    r

    @property
    def omega_p(self):
        """ Get angular frequecy"""
        return self.tp * 2 * np.pi  # TODO CHECK THIS


    def density(alpha: float, gamma: float, r: float):
        """jonswap density using formulation used in Jake's paper

        Args:
            omega (float): angular frequency
            alpha (float): scaling parameter TODO: maybe create unscaled_density and then commmon density
            om_p (float): peak ang freq
            gamma (float): peak enhancement factor
            r (float): spectral tail decay index

        Returns:
            dens (float): JONSWAP density for given omega
        """

        delta = np.exp(-(2 * (0.07 + 0.02 * (om_p > np.abs(omega)))) ** -2 * (np.abs(omega) / om_p - 1) ** 2)

        dens = alpha * self.omega ** -r * np.exp(-r / 4 * (np.abs(omega) / self.omega_p) ** -4) * gamma ** delta

        return dens


def djonswap(f: np.ndarray, hs: float, tp: float):
    """
    returns JONSWAP density for given frequency range

    Args:
        f (np.ndarray): frequency [s^-1]
        hs (float): significant wave height [m]
        tp (float): significant wave period [s]

    Returns:
        dens (np.ndarray): JONSWAP density for given frequencies []
    """
    g = 9.81
    fp = 1. / tp
    df = f[1] - f[0]

    # example constants from https://wikiwaves.org/Ocean-Wave_Spectra
    gamma = 2  # 3.3
    sigma_a = 0.07
    sigma_b = 0.09

    sigma = (f < fp) * sigma_a + (f >= fp) * sigma_b

    gamma_coeff = gamma ** np.exp(-0.5 * (((f / fp - 1)/sigma) ** 2))
    dens = g ** 2 * (2 * np.pi) ** -4 * f ** -5 * np.exp(-1.25 * (tp*f) ** -4) * gamma_coeff

    area = sum(dens*df)

    dens *= hs ** 2 / (16 * area)

    return dens


def random_waves_acf(tau: np.ndarray, f: np.ndarray, spctrl_dens: np.ndarray):
    """find acf function of the gaussian random wave surface with given spectrum

    Args:
        tau (np.ndarray): lags []
        f (np.ndarray): contributing frequencies [hertz]
        spctrl_dens (np.ndarray): spectral densities for given frequencies []

    Returns:
        acf (np.ndarray): auto correlation
    """

    df = f[1] - f[0]
    spctrl_area = np.sum(spctrl_dens * df)

    outer_ft = np.outer(f, tau)    # (n_freq x tau_length)

    acf_mat = np.cos(2 * np.pi * outer_ft) * spctrl_dens[:, np.newaxis] * df / spctrl_area    # (n_freq x tau_length)
    acf_vec = np.sum(acf_mat, axis=0)   # sum over columns to give (1 x tau_length)

    return acf_vec


def kth_moment(k: int, f: np.ndarray, spctrl_dens: np.ndarray):
    """function to return the kth moment of the given spectrum evaulated at given frequencies

    Args:
        k (int): moment
        f_seq (np.ndarray): frequencies [hertz]

    Returns:
        k_integral (_type_): integral equal to the kth moment
    """

    df = f[1] - f[0]

    k_integral = np.sum(spctrl_dens * f ** k * df)

    return k_integral


def frq_dr_spctrm(omega: np.ndarray, phi: np.ndarray, alpha: float, om_p: float, gamma: float,
                  r: float, phi_m: float, beta: float, nu: float, sig_l: float,
                  sig_r: float):
    """returns frequency direction spectrum for a single angular frequency and direction.

    Args:
        omega (np.ndarray): angular frequency
        phi (np.ndarray): direction (from)
        alpha (float): scaling parameter
        om_p (float): peak ang freq
        gamma (float): peak enhancement factor
        r (float): spectral tail decay index
        phi_m (float): mean direction
        beta (float): limiting peak separation
        nu (float): peak separation shape
        sig_l (float): limiting angular width
        sig_r (float): angular width shape

    Returns:
        dens (np.ndarray): freq direction spectrum [] (??, ??)
    """
    dens = sprd_fnc(omega, phi, om_p, phi_m, beta, nu, sig_l, sig_r) * alt_djonswap(omega, alpha, om_p, gamma, r)

    return dens


def sprd_fnc(omega: float, phi: float, om_p: float, phi_m: float, beta: float, nu: float,
             sig_l: float, sig_r: float):
    """returns bimodal wrapped Gaussian spreading function D(omega, phi) at a single point

    Args:
        omega (float): angular frequency
        phi (float): direction (from)
        om_p (float): peak ang freq
        phi_m (float): mean direction
        beta (float): limiting peak separation
        nu (float): peak separation shape
        sig_l (float): limiting angular width
        sig_r (float): angular width shape

    Returns:
        dens (float): D(omega, phi) for given omega and phi
    """
    k_num = 200
    k_range = np.linspace(start=-k_num/2, stop=k_num/2, num=k_num + 1)

    phi_m1 = phi_m + beta * np.exp(-nu * min(om_p / np.abs(omega), 1)) / 2
    phi_m2 = phi_m - beta * np.exp(-nu * min(om_p / np.abs(omega), 1)) / 2
    phi_arr = np.array([phi_m1, phi_m2])

    sigma = sig_l - sig_r / 3 * (4 * (om_p / np.abs(omega)) ** 2 - (om_p / np.abs(omega)) ** 8)

    nrm_cnst = (2 * sigma * np.sqrt(2 * np.pi)) ** -1
    dens_k = np.empty(k_num + 1)

    for i_k, k in enumerate(k_range):
        exp_term = np.exp(-0.5 * ((phi - phi_arr - 2 * np.pi * k) / sigma) ** 2)
        dens_k[i_k] = np.sum(exp_term)

    dens = nrm_cnst * np.sum(dens_k)

    return dens


def alt_djonswap(omega: float, alpha: float, om_p: float, gamma: float, r: float):
    """jonswap density using formulation used in Jake's paper

    Args:
        omega (float): angular frequency
        alpha (float): scaling parameter
        om_p (float): peak ang freq
        gamma (float): peak enhancement factor
        r (float): spectral tail decay index

    Returns:
        dens (float): JONSWAP density for given omega
    """

    delta = np.exp(-(2 * (0.07 + 0.02 * (om_p > np.abs(omega)))) ** -2 * (np.abs(omega) / om_p - 1) ** 2)

    dens = alpha * omega ** -r * np.exp(-r / 4 * (np.abs(omega) / om_p) ** -4) * gamma ** delta

    return dens
