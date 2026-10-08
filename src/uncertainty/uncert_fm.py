import numpy as np
from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_frequency_uncertainty, DSG800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_fm(f1: list, f2 : list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    f1 = A_type_uncertainty(f1, "P1")
    f2 = A_type_uncertainty(f2, "Pnoise")

    # A + B type 
    sa_f1_med = spectral_analyzer_frequency_uncertainty(f1, SA_config,
                                                        DSG800_UNCERT['er_fref'],
                                                        DSG800_UNCERT['er_span'],
                                                        DSG800_UNCERT['er_rbw_f'])

    sa_f2_med = spectral_analyzer_frequency_uncertainty(f2, SA_config, 
                                                        DSG800_UNCERT['er_fref'],
                                                        DSG800_UNCERT['er_span'],
                                                        DSG800_UNCERT['er_rbw_f'])

    # Calculation
    fm = sa_f1_med.val - sa_f2_med.val
    u_fm_db = np.sqrt(sa_f1_med.uncert**2 + sa_f2_med.uncert**2)

    J0   = 2.40482555772
    u_J0 = 0.00000000001 / np.sqrt(3)   # Round error

    delta_f = J0 * fm
    u_delta_f = np.sqrt( (J0 * u_fm_db)**2 + (delta_f * u_J0)**2 )

    return Uncertainty(delta_f, u_delta_f, "FM Measurement Uncertainty")

if __name__ == "__main__":
    df = pd.read_csv("test_fm.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. Check

    measure_groups = df.groupby("Delta F")  # TODO. Check names
    real_incf = []
    measure_incf = []
    
    for incf, group in measure_groups:  
        f1 = group['F1'].tolist()
        f2 =  group['F2'].tolist()
        incf_med = uncert_fm(f1, f2, SA_config)

        real_incf.append(incf)
        measure_incf.append(incf_med)

    for incf, incf_med in zip(real_incf, measure_incf):
        print(f"Incremental Frequency Setting: {incf} Hz | Measured Incremental Frequency: {incf_med.val:.2f} Hz | Uncertainty: {incf_med.uncert:.2f} Hz")    


