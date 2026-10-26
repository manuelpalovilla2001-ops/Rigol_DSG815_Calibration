from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_frequency_uncertainty, DSA800_UNCERT, A_type_uncertainty
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
    measure_groups = df.groupby("Amplitud Referencia")  # TODO. Check names
    
    check_config = measure_groups[['RBW (Hz)', 'VBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")

    real_amplitud = []
    measure_f = []
    
    for ampl, group in measure_groups:  
        rbw = group['RBW (Hz)'].iloc[0]
        vbw = group['VBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=vbw, span=span, ref_level=ref_level, atte=atte)

        f = group['F'].tolist()
        f_med = uncert_10mhz_ref(f, SA_config)

        real_amplitud.append(ampl)
        measure_f.append(f_med)

    for ampl, f_med in zip(real_amplitud, measure_f):
        print(f"Signal Amplitude: {ampl} dB | Measured Frequency: {f_med.val:.2f} Hz | Uncertainty: {f_med.uncert:.2f} Hz")    


