from uncert_lib.uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSA800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_amplitude(power: list, freq : float, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    power = A_type_uncertainty(power, "Power")

    # A + B type 
    sa_power_med = spectral_analyzer_power_uncertainty(power, freq, SA_config,
                                                          DSA800_UNCERT['e_abs'],
                                                          DSA800_UNCERT['e_fr'],
                                                          DSA800_UNCERT['e_rl'],
                                                          DSA800_UNCERT['e_att_sw'],
                                                          DSA800_UNCERT['e_rbw_sw'],
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSA800_UNCERT['e_log'],
                                                          DSA800_UNCERT['e_log_max'])

    return sa_power_med

if __name__ == "__main__":
    df = pd.read_csv("./data/test_amplitud.csv")
    measure_groups = df.groupby(['Reference Value (dBm)', 'Output Frequency (Hz)'])

    check_config = measure_groups[['RBW (Hz)', 'SPAN (Hz)', 'Attenuator (dB)', 'Reference Level (dBm)']].nunique(dropna=False)
    if not check_config.eq(1).all().all():
        raise ValueError("No todas las configuraciones son iguales")

    real_P = []
    real_freq = []
    measure_P = []

    
    for (ref_P, freq), group in measure_groups:
        rbw = group['RBW (Hz)'].iloc[0]
        span = group['SPAN (Hz)'].iloc[0] 
        ref_level = group['Reference Level (dBm)'].iloc[0]
        atte = group['Attenuator (dB)'].iloc[0]
        SA_config = SpectralAnalizerConfig(rbw=rbw, vbw=rbw, span=span, ref_level=ref_level, atte=atte)

        p = group['Measurement Value (dBm)'].tolist()
        p_med= uncert_amplitude(p, freq, SA_config)

        real_P.append(ref_P)
        real_freq.append(freq)
        measure_P.append(p_med)

    for ref_P, freq, p_med in zip(real_P, real_freq, measure_P):
        k = 2
        u_expanded = p_med.uncert * k
        print(f"Power Setting: {ref_P}dBm | Frequency: {freq/1e6:>6} MHz | Measured Power: {p_med.val:>6.2f} dBm | Uncertainty: {u_expanded:>6.3g} dB | K: {k} | Confianza: 95%")    



