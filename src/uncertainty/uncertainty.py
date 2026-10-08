import numpy as np

YEARS = 2   # TODO. Check.

DSA800_UNCERT = {
    "e_abs": 0.4,       # In dB. # 0.3 if DSA832.
    "e_fr": 0.7,        # In dB. # PA off, DSA815. Check page 9.
    "e_rl": 0,          # Doesn't tell in the datasheet. In dB.
    "e_att_sw": 0.5,    # In dB. # 0.3 if DSA832.
    "e_rbw_sw": 0.1,    # In dB.
    "e_rbw_P": 0.1,     # ??? (Not used)
    "e_log": 0.0,       # Doesn't tell in the datasheet.
    "e_log_max": 0.5,   # Doesn't tell in the datasheet.
    
    "er_rbw_f": 0.1,    # 10% error.
    "er_span": 0.01,    # 1% error.
    "er_fref": 2e-6 * YEARS + 2e-6 + 1e-6,   # Aging rate * Years + Temperature variation + Initial tolerance. In ppm.
}

class Uncertainty:
    def __init__(self, val, uncert, name = ''):
        self.val = val
        self.uncert = uncert
        self.name = name

class SpectralAnalizerConfig():
    def __init__(self, rbw, vbw, span, ref_level, atte, N = 601, cal_atte = 10, cal_rbw = 1e3, cal_fc=50e6):
        self.rbw = rbw
        self.vbw = vbw
        self.span = span
        self.ref_level = ref_level
        self.atte = atte
        self.N = N

        self.cal_rbw = cal_rbw
        self.cal_atte = cal_atte
        self.cal_fc = cal_fc

class DSA800Config(SpectralAnalizerConfig):
    def __init__(self, rbw, vbw, span, ref_level, atte, N=601,):
        super().__init__(rbw, vbw, span, ref_level, atte, N, cal_atte = 10, cal_rbw = 1e3, cal_fc = 50e6)

def A_type_uncertainty(values: list, name: str) -> Uncertainty:
    values = np.mean(values)
    ui = np.std(values, ddof=1) / np.sqrt(len(values))
    return Uncertainty(values, ui, name)

def roe_to_gamma(roe):
    """
    Convert Return on Equity (ROE) to gamma value.
    
    Parameters:
    roe (float): Return on Equity value.
    
    Returns:
    float: Corresponding gamma value.
    """
    return (roe - 1) / (roe + 1)

def gamma_to_roe(gamma):
    """
    Convert gamma value to Return on Equity (ROE).
    
    Parameters:
    gamma (float): Gamma value.
    
    Returns:
    float: Corresponding Return on Equity value.
    """
    return (1 + gamma) / (1 - gamma)

def get_missmatch_uncertainity(gamma_g, gamma_l, type='ring-ring'):
    k = 1.0
    if type == 'ring-ring':
        k = np.sqrt(2) * abs(gamma_g) * abs(gamma_l)
    elif type == 'ring-disk':
        k = 1 
    elif type == 'disk-disk':
        k = 1/np.sqrt(2)
    else: 
        raise ValueError("Invalid type. Must be 'ring-ring', 'ring-disk', or 'disk-disk'.")
    return k * abs(gamma_g) / abs(gamma_l)


def power_meter_uncertainty(pmed: Uncertainty,
                            pcal : Uncertainty,
                            kb : Uncertainty,
                            kc : Uncertainty,
                            mu : Uncertainty,
                            muc : Uncertainty,
                            lineality: Uncertainty,
                            d : Uncertainty,
                            zs : Uncertainty,
                            zc : Uncertainty,
                            n : Uncertainty) -> Uncertainty:
    """
    Returns the combined uncertainty of a power meter measurement based on various contributing uncertainties.
    
    Parameters:
    pmed (Uncertainty): Power meter measurement uncertainty.
    pcal (Uncertainty): Calibration power meter uncertainty.
    kb (Uncertainty): Calibration factor.
    kc (Uncertainty): Calibration factor (calibration process).
    mu (Uncertainty): Mismatch uncertainty.
    muc (Uncertainty): Mismatch uncertainty (calibration process).
    lineality (Uncertainty): Linearity uncertainty.
    d (Uncertainty): Uncertainty of drift.
    zs (Uncertainty): Uncertainty of the zero setting.
    zc (Uncertainty): Uncertainty of zero carryover.
    n (Uncertainty): Uncertainty of zero noise.

    Returns:
    Uncertainty: Combined uncertainty of the power meter measurement.
    """
    uu_mu = mu.uncert**2
    uu_pm = pmed.uncert**2 / pmed.val**2
    uu_d = d.uncert**2 / pmed.val**2
    uu_kb = kb.uncert**2 / kb.val**2
    uu_muc = muc.uncert**2
    uu_pcal = pcal.uncert**2 / pcal.val**2
    uu_kc = kc.uncert**2 / kc.val**2
    uu_lineality = lineality.uncert**2 / lineality.val**2
    uu_zero = (1/pmed.val - 1/pcal.val)**2 * (zs.uncert**2 + zc.uncert**2 + n.uncert**2)

    t = zs.val + zc.val + n.val

    pgzo = (mu.val/kb.val) * ((pmed.val-t-d.val) * kc.val * pcal.val)/(muc.val*(pcal.val - t))
    u_pgzo = pgzo * np.sqrt(uu_mu + uu_pm + uu_d + uu_kb + uu_muc + uu_pcal + uu_kc + uu_lineality + uu_zero)

    return Uncertainty(pgzo, u_pgzo, "Power Meter Measurement Uncertainty")

def spectral_analyzer_power_uncertainty(pmed: Uncertainty,
                                        fmed: float,
                                        SA_config: SpectralAnalizerConfig,
                                        e_abs : float,
                                        e_fr : float,
                                        e_rl : float,
                                        e_att_sw : float,
                                        e_rbw_sw : float,
                                        e_rbw_P : float,
                                        e_log : float,
                                        e_log_max : float) -> Uncertainty:
    """
    Returns the combined uncertainty of a spectral analyzer power measurement based on various contributing uncertainties.
    
    Params:
    ---
        pmed (Uncertainty):
            Power meter measurement uncertainty. In dB.
        SA_config (SpectralAnalizerConfig): 
            Spectral analyzer configuration. 
        e_abs (float): 
            Absolute error. In dB.
        e_fr (float): 
            Frequency Response error. In dB.
        e_rl (float): 
            Reference Level error. In dB.
        e_att_sw (float): 
            Attenuator switch error. In dB.
        e_rbw_sw (float): 
            RBW switch error. In dB.
        e_rbw_P (float):
            Error of the RBW filter. In %. Internaly converted to dB as: 10log(1 + e_rbw_P/100)
        e_log (float): 
            Logarithmic error. In dB. Defined as how many dB of error for any dB below RL.
        e_log_max (float):
            Maximum possible logarithmic error. In dB.

    Returns:
    Uncertainty: Combined uncertainty of the spectral analyzer power measurement.
    """
    u_abs = e_abs / np.sqrt(3)
    u_fr = e_fr / np.sqrt(3) if SA_config.cal_fc != fmed else 0
    u_rl = e_rl / np.sqrt(3)
    u_att_sw = e_att_sw / np.sqrt(3) if SA_config.atte != SA_config.cal_atte else 0
    u_rbw_sw = e_rbw_sw / np.sqrt(3) if SA_config.rbw != SA_config.cal_rbw else 0

    u_rbw = 10 * np.log10(1 + e_rbw_P/100) / np.sqrt(3)
    e_log_db = min(e_log * (SA_config.ref_level - pmed.val), e_log_max)
    u_log = e_log_db / np.sqrt(3)

    u_total = np.sqrt(u_abs**2 + u_fr**2 + u_rl**2 + u_att_sw**2 + u_rbw_sw**2 + u_rbw**2 + u_log**2 + pmed.uncert**2)

    return Uncertainty(pmed.val, u_total, "Spectral Analyzer Power Measurement Uncertainty")

def spectral_analyzer_frequency_uncertainty(fmed: Uncertainty,
                                            SA_config: SpectralAnalizerConfig,
                                            er_fref : float,
                                            er_span : float,
                                            er_rbw : float) -> Uncertainty:
    """
    Returns the combined uncertainty of a spectral analyzer frequency measurement based on various contributing uncertainties.

    Params:
    ---
        fmed (Uncertainty):
            Frequency measurement uncertainty. In Hz.
        SA_config (SpectralAnalizerConfig): 
            Spectral analyzer configuration. 
        er_fref (float): 
            Reference Frequency relative error. 
        er_span (float): 
            Span error relative error.
        er_rbw (float):
            RBW error relative error.
    Returns:
    ---
    Uncertainty: Combined uncertainty of the spectral analyzer frequency measurement.
    """

    e_fref = er_fref * fmed.val
    e_span = er_span * SA_config.span
    e_rbw = er_rbw * SA_config.rbw
    e_marker = SA_config.span / (SA_config.N - 1)

    u_f = (e_fref + e_span + e_rbw + e_marker) / np.sqrt(3)

    return Uncertainty(fmed.val, u_f, "Spectral Analyzer Frequency Measurement Uncertainty")

    