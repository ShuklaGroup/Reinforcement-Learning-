
import glob
import numpy as np
import mdtraj as md

topFile = 'csrc_inactive.pdb'
top = md.load(topFile).topology

# high RMSF res
select = 'resid 5 to 86 or resid 144 to 170'
protein_highRMSF_atomIndex = top.select(select)
	
#############
for file in glob.glob('*/*.mdcrd'):
	print(file)
	t = md.load(file)

	# High RMSF Dihedral Angles
	t2 = t.atom_slice(protein_highRMSF_atomIndex)
	phi_0 = md.compute_phi(t2)[1]
	psi_0 = md.compute_psi(t2)[1]
	
	phi_sin = np.sin(phi_0)
	phi_cos = np.cos(phi_0)
	psi_sin = np.sin(psi_0)
	psi_cos = np.cos(psi_0)
	n_frames = phi_sin.shape[0]
	n_phi = phi_sin.shape[1]
	n_psi = psi_sin.shape[1]
	
	phi_psi = np.empty([n_frames, 2*(n_phi+n_psi)])
	for i in range(n_frames):
		phi_psi[i,0:n_phi] = phi_sin[i]
		phi_psi[i,n_phi:2*n_phi] = phi_cos[i]
		phi_psi[i,2*n_phi:2*n_phi+n_psi] = psi_sin[i]
		phi_psi[i,2*n_phi+n_psi:2*n_phi+2*n_psi] = psi_cos[i]
	
	np.save(file.replace('.lh5','_highRMSF_phi_psi.npy'), phi_psi)
	
