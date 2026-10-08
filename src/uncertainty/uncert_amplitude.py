from .uncertainty import Uncertainty, SpectralAnalizerConfig, spectral_analyzer_power_uncertainty, DSG800_UNCERT, A_type_uncertainty
import pandas as pd

def uncert_amplitude(power: list, SA_config : SpectralAnalizerConfig) -> Uncertainty:
    # A type
    power = A_type_uncertainty(power, "Power")

    # A + B type 
    sa_power_med = spectral_analyzer_power_uncertainty(power, SA_config, 
                                                          DSG800_UNCERT['e_abs'],
                                                          0,							# FR not used. Freq range very low.
                                                          DSG800_UNCERT['e_rl'],        # TODO chequear si se uso el RL de calibracion o no.
                                                          DSG800_UNCERT['e_att_sw'],
                                                          DSG800_UNCERT['e_rbw_sw'],
                                                          0,                            # RBW doesnt apply. Measurment in a specific point in frequency.
                                                          DSG800_UNCERT['e_log'],
                                                          DSG800_UNCERT['e_log_max'])   # Resolution doesnt apply. Measurment in a specific point in frequency.

    return sa_power_med

if __name__ == "__main__":
    df = pd.read_csv("test_amplitud.csv") # TODO. check Path.

    SA_config = SpectralAnalizerConfig(rbw=100, vbw=100, span=10e3, ref_level=0, atte=10)   # TODO. check

    measure_groups = df.groupby("Reference Value (dBm)")
    real_P = []
    measure_P = []
    
    for ref_P, group in measure_groups:
        p = group['Measurement Value A3'].tolist()
        p_med= uncert_amplitude(p, SA_config)

        real_P.append(ref_P)
        measure_P.append(p_med)

    for ref_P, p_med in zip(real_P, measure_P):
        print(f"Power Setting: {ref_P}dB | Measured Power: {p_med.val:.2f} dB | Uncertainty: {p_med.uncert:.2f} dB")    


