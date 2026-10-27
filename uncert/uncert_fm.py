import numpy as np
from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_frequency_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_fm(f1: list, f2 : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    f1 = A_type_uncertainty(f1, "P1")
    f2 = A_type_uncertainty(f2, "Pnoise")

    # A + B type 
    sa_f1_med = spectral_analyzer_frequency_uncertainty(f1, SA_config,
                                                        DSA800_UNCERT['er_fref'],
                                                        DSA800_UNCERT['er_span'],
                                                        DSA800_UNCERT['er_rbw_f'])

    sa_f2_med = spectral_analyzer_frequency_uncertainty(f2, SA_config, 
                                                        DSA800_UNCERT['er_fref'],
                                                        DSA800_UNCERT['er_span'],
                                                        DSA800_UNCERT['er_rbw_f'])

    # Calculation
    fm = sa_f1_med.val - sa_f2_med.val
    u_fm_db = np.sqrt(sa_f1_med.uncert**2 + sa_f2_med.uncert**2)

    J0   = 2.40482555772
    u_J0 = 0.00000000001 / np.sqrt(3)   # Round error

    delta_f = J0 * fm
    u_delta_f = np.sqrt( (J0 * u_fm_db)**2 + (delta_f * u_J0)**2 )

    return Uncertainty(delta_f, u_delta_f, "FM Measurement Uncertainty")

if __name__ == "__main__":
    df = pd.read_csv("./data/test_fm.csv")
    measure_groups = df.groupby("Delta F")

    check_config = measure_groups[['RBW (Hz)', 'VBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")

    real_incf = []
    measure_incf = []
    
    for incf, group in measure_groups:  
        rbw = group['RBW (Hz)'].iloc[0]
        vbw = group['VBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=vbw, span=span, ref_level=ref_level, atte=atte)

        f1 = group['F1'].tolist()
        f2 =  group['F2'].tolist()
        incf_med = uncert_fm(f1, f2, SA_config)

        real_incf.append(incf)
        measure_incf.append(incf_med)

    for incf, incf_med in zip(real_incf, measure_incf):
        print(f"Incremental Frequency Setting: {incf} Hz | Measured Incremental Frequency: {incf_med.val:.2f} Hz | Uncertainty: {incf_med.uncert:.2f} Hz")    


