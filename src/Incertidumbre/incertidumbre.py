import numpy as np

class Uncertainty:
	def __init__(self, val, uncert, name):
		self.val = val
		self.uncert = uncert
		self.name = name


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