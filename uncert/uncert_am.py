import numpy as np
from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_am(pcarrier: list, pside_band : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    pcarrier = A_type_uncertainty(pcarrier, "Pcarrier")
    pside_band = A_type_uncertainty(pside_band, "PSide Band")

    # A + B type 
    sa_pcarrier_med = spectral_analyzer_power_uncertainty(pcarrier, 1e9, SA_config,     # Measure for 1GHz
                                                          DSA800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])
    
    sa_pside_band_med = spectral_analyzer_power_uncertainty(pside_band, 1e9, SA_config, # Measure for 1GHz
                                                          DSA800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSA800_UNCERT['e_rl'],
                                                          0,                            # Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    # Uncertainty of AM measurement
    # In dB
    m_db = sa_pside_band_med.val - sa_pcarrier_med.val + 20 * np.log10(2)
    u_m_db = np.sqrt(sa_pside_band_med.uncert**2 + sa_pcarrier_med.uncert**2)

    # Linear value
    m_med = 10**(m_db/20)
    u_m_med = m_med * (np.log(10)/20) * u_m_db

    return Uncertainty(m_med, u_m_med, "AM Measurement Uncertainty")

if __name__ == "__main__":
    df = pd.read_csv("./data/test_am.csv")
    measure_groups = df.groupby("Modulation Depth Set")

    check_config = measure_groups[['RBW (Hz)', 'VBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")
    
    real_m = []
    measure_m : list[Uncertainty] = []
    
    for am_index, group in measure_groups:
        rbw = group['RBW (Hz)'].iloc[0]
        vbw = group['VBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=vbw, span=span, ref_level=ref_level, atte=atte)

        pcarrier = -10
        pside_band = group['P_carrier - P_sideband'].tolist()
        pside_band = [pcarrier - i for i in pside_band]
        m_med= uncert_am(pcarrier, pside_band, SA_config)

        real_m.append(am_index)
        measure_m.append(m_med)

    for am_index, m_med in zip(real_m, measure_m):
        k = 2
        u_expanded = m_med.uncert * k
        print(f"Modulation Depth Set: {am_index/100} | Measured AM: {m_med.val:.2f} | Uncertainty: {u_expanded:>6.2g} | K: {k} | Confianza: 95%")    
