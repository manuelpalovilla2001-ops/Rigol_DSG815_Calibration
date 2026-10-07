import numpy as np
from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSG800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_am(pcarrier: list, pside_band : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    pcarrier = A_type_uncertainty(pcarrier, "Pcarrier")
    pside_band = A_type_uncertainty(pside_band, "PSide Band")

    # A + B type 
    sa_pcarrier_med = spectral_analyzer_power_uncertainty(pcarrier, SA_config, 
                                                          DSG800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSG800_UNCERT['e_rl'],        # TODO chequear si se uso el RL de calibracion o no.
                                                          0,							# Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'],
                                                          0)                            # Resolution doesnt apply. Measurment in a specific point in frequency.

    sa_pside_band_med = spectral_analyzer_power_uncertainty(pside_band, SA_config, 
                                                          DSG800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSG800_UNCERT['e_rl'],        # TODO chequear si se uso el RL de calibracion o no.
                                                          0,							# Att SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW SW doesnt apply. Relative Measurement.
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'],
                                                          0)                            # Resolution doesnt apply. Measurment in a specific point in frequency.

    # Uncertainty of AM measurement
    m_db = sa_pcarrier_med.val - sa_pside_band_med.val + 20 * np.log10(2)
    u_m_db = np.sqrt(sa_pcarrier_med.uncert**2 + sa_pside_band_med.uncert**2)
    m_med = Uncertainty(m_db, u_m_db, "AM Measurement Uncertainty")

    # TODO Convert uncertainty from dB to % using propagation of uncertainty.

    return m_med

if __name__ == "__main__":
    df = pd.read_csv("test_am.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. check

    measure_groups = df.groupby("AM Depth Setting (%)")

    real_m = []
    measure_m = []
    
    for am_index, group in measure_groups:
        pcarrier = group['Carrier Power (dBm)'].tolist()
        pside_band = group['Sideband Power (dBm)'].tolist()
        m_med= uncert_am(pcarrier, pside_band, SA_config)

        real_m.append(am_index)
        measure_m.append(m_med)

    for am_index, m_med in zip(real_m, measure_m):
        print(f"AM Depth Setting: {am_index}% | Measured AM Depth: {m_med.val:.2f} dB | Uncertainty: {m_med.uncert:.2f} dB")    


