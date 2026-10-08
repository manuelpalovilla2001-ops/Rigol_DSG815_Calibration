from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSG800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_amplitude(power: list, freq : float, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    power = A_type_uncertainty(power, "Power")

    # A + B type 
    sa_power_med = spectral_analyzer_power_uncertainty(power, freq, SA_config,
                                                          DSG800_UNCERT['e_abs'],
                                                          DSG800_UNCERT['e_fr'],
                                                          DSG800_UNCERT['e_rl'],
                                                          DSG800_UNCERT['e_att_sw'],
                                                          DSG800_UNCERT['e_rbw_sw'],
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'])

    return sa_power_med

if __name__ == "__main__":
    df = pd.read_csv("test_amplitud.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. check

    measure_groups = df.groupby(['Reference Value (dBm)', 'Output Frequency (Hz)'])
    real_P = []
    real_freq = []
    measure_P = []

    
    for (ref_P, freq), group in measure_groups:
        p = group['Measurement Value A3'].tolist()
        p_med= uncert_amplitude(p, freq, SA_config)

        real_P.append(ref_P)
        real_freq.append(freq)
        measure_P.append(p_med)

    for ref_P, freq, p_med in zip(real_P, real_freq, measure_P):
        print(f"Power Setting: {ref_P}dB | Frequency: {freq} Hz | Measured Power: {p_med.val:.2f} dB | Uncertainty: {p_med.uncert:.2f} dB")    


