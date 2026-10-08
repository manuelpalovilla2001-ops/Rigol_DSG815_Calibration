from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_frequency_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_10mhz_ref(f1: list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    f1 = A_type_uncertainty(f1, "P1")

    # A + B type 
    sa_f1_med = spectral_analyzer_frequency_uncertainty(f1, SA_config,
                                                        DSA800_UNCERT['er_fref'],
                                                        DSA800_UNCERT['er_span'],
                                                        DSA800_UNCERT['er_rbw_f'])

    return sa_f1_med

if __name__ == "__main__":
    df = pd.read_csv("reporte_10mhz_reference.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. Check

    measure_groups = df.groupby("Amplitud Referencia")  # TODO. Check names
    real_amplitud = []
    measure_f = []
    
    for ampl, group in measure_groups:  
        f = group['F'].tolist()
        f_med = uncert_10mhz_ref(f, SA_config)

        real_amplitud.append(ampl)
        measure_f.append(f_med)

    for ampl, f_med in zip(real_amplitud, measure_f):
        print(f"Signal Amplitude: {ampl} dB | Measured Frequency: {f_med.val:.2f} Hz | Uncertainty: {f_med.uncert:.2f} Hz")    


