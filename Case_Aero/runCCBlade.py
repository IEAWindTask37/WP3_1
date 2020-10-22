
import os
import numpy as np
import ruamel_yaml as ry
from wisdem.ccblade             import CCAirfoil, CCBlade
from wisdem.commonse.csystem    import DirectionVector


############ File Management ##########
run_dir         = os.path.dirname( os.path.realpath(__file__) ) + os.sep
fname_wt_input  = run_dir + 'WP31_Ex1_Baseline.yaml'
output_folder   = run_dir


########## Load YAML WT Ontology ##########
with open(fname_wt_input, 'r') as f:
    input_yaml  = ry.load(f, Loader=ry.Loader)


########## Inputs to CCBlade ##########
# Hub data
hub_data        = input_yaml['components']['hub']['outer_shape_bem']
hub_r           = 0.5 * hub_data['diameter']
cone            = np.rad2deg(hub_data['cone_angle'])
# Nacelle data
nacelle_data    = input_yaml['components']['nacelle']['outer_shape_bem']
tilt            = np.rad2deg(nacelle_data['uptilt_angle'])
# Blade data
blade_aero_data = input_yaml['components']['blade']['outer_shape_bem']
s               = np.array(blade_aero_data['reference_axis']['z']['grid'])
b               = np.array(blade_aero_data['reference_axis']['z']['values'])
precurve        = np.interp(s, blade_aero_data['reference_axis']['x']['grid'], blade_aero_data['reference_axis']['x']['values'])
presweep        = np.interp(s, blade_aero_data['reference_axis']['y']['grid'], blade_aero_data['reference_axis']['y']['values'])
r               = hub_r + b
Rtip            = r[-1] 
chord           = np.interp(s, blade_aero_data['chord']['grid'], blade_aero_data['chord']['values'])
twist           = np.rad2deg(np.interp(s, blade_aero_data['twist']['grid'], blade_aero_data['twist']['values']))
B               = input_yaml['assembly']['number_of_blades']
# Tower data
hub_height      = input_yaml['components']['foundation']['height'] + input_yaml['components']['tower']['outer_shape_bem']['reference_axis']['z']['values'][-1] + nacelle_data['distance_tt_hub']
# Environmental data
rho             = input_yaml['environment']['air_density']
mu              = input_yaml['environment']['air_dyn_viscosity']
shearExp        = input_yaml['environment']['shear_exp']
# Modeling options
nSector         = 4 # Number of azimuthal angles where CCBlade is run at
tiploss         = True # Flag to activate and deactivate the tip loss model
hubloss         = True # Flag to activate and deactivate the hub loss model
wakerotation    = True # Flag to activate and deactivate the effect of wake rotation (i.e., tangential induction factor is nonzero)
usecd           = True # Flag to activate and deactivate the use of the drag coefficient in computing induction factors
# Operating conditions
tsr             = input_yaml['control']['tsr'] # Tip speed ratio
pitch           = np.rad2deg(input_yaml['control']['pitch']) # Pitch angle
Uhub            = 9. # Wind speed
# Airfoil data
n_aoa = 200
aoa   = np.unique(np.hstack([np.linspace(-np.pi, -np.pi / 6., int(n_aoa / 4. + 1)), np.linspace(-np.pi / 6., np.pi / 6., int(n_aoa / 2.)), np.linspace(np.pi / 6., np.pi, int(n_aoa / 4. + 1))]))
airfoils = input_yaml['airfoils']
cl = np.zeros((len(s), n_aoa, 1, 1))
cd = np.zeros((len(s), n_aoa, 1, 1))
cm = np.zeros((len(s), n_aoa, 1, 1))
for i in range(len(s)):
    cl[i,:,0,0] = np.interp(aoa, airfoils[i]['polars'][0]['c_l']['grid'], airfoils[i]['polars'][0]['c_l']['values'])
    cd[i,:,0,0] = np.interp(aoa, airfoils[i]['polars'][0]['c_d']['grid'], airfoils[i]['polars'][0]['c_d']['values'])
    cm[i,:,0,0] = np.interp(aoa, airfoils[i]['polars'][0]['c_m']['grid'], airfoils[i]['polars'][0]['c_m']['values'])

af = [None]*len(s)
for i in range(len(s)):
    af[i] = CCAirfoil(np.rad2deg(aoa), [1e+6], cl[i,:,0,0], cd[i,:,0,0], cm[i,:,0,0])


########## Run CCBlade ##########
get_cp_cm = CCBlade(r, chord, twist, af, hub_r, Rtip, B, rho, mu, cone, tilt, 0., shearExp, hub_height, nSector, presweep, precurve[-1], presweep, presweep[-1], tiploss, hubloss, wakerotation, usecd)   
# get_cp_cm.induction        = True
Omega           = Uhub * tsr / Rtip * 30.0 / np.pi # Rotor speed
myout, derivs = get_cp_cm.evaluate([Uhub], [Omega], [pitch], coefficients=True)
P, T, Q, M, CP, CT, CQ, CM = [myout[key] for key in ['P','T','Q','M','CP','CT','CQ','CM']]
get_cp_cm.induction_inflow = True
loads, deriv = get_cp_cm.distributedAeroLoads([Uhub], Omega, pitch, 0.)


########## Post Process Output ##########
# Compute forces in the airfoil coordinate system, pag 21 of https://www.nrel.gov/docs/fy13osti/58819.pdf
P_b = DirectionVector(loads['Np'], -loads['Tp'], 0)
P_af = P_b.bladeToAirfoil(twist)
# Compute lift and drag forces
F = P_b.bladeToAirfoil(twist + loads['alpha'] + pitch)
# Print output .dat file with the quantities distributed along span
np.savetxt(os.path.join(output_folder, 'distributed_quantities.dat'), np.array([s, r, loads['alpha'], loads['a'], loads['ap'], loads['Cl'], loads['Cd'], F.x, F.y, loads['Np'], -loads['Tp'], P_af.x, P_af.y]).T, header = 'Blade nondimensional span position (-) \t Rotor position (m) \t Angle of attack (deg) \t Axial induction (-) \t Tangential induction (-) \t Lift coefficient (-) \t Drag coefficient (-) \t Lift force (N) \t Drag force (N) \t Force along x BCS - N (N) \t Force along y BCS - T (N) \t Force along x ACS (N) \t Force along y ACS (N)', delimiter = '\t')
# Print output .dat file with the rotor equivalent quantities
np.savetxt(os.path.join(output_folder, 'rotor_equivalent_quantities.dat'), np.array([P, T, Q, M, CP, CT, CQ, CM]).T, header = 'Rotor power (W) \t Rotor thrust (N) \t Rotor torque (Nm) \t Blade root flapwise moment  (Nm) \t Power coefficient (-) \t Thrust coefficient (-) \t Torque coefficient (-) \t Moment coefficient (-)', delimiter = '\t')
# Print outputs to screen
print('Output files printed in folder ' + output_folder)
print('OUTPUTS')
print('Power (W)                 : {:2f}'.format(P[0]))
print('Thrust (N)                : {:2f}'.format(T[0]))
print('Torque (Nm)               : {:2f}'.format(Q[0]))
print('Blade root flp moment (Nm): {:2f}'.format(M[0]))
print('Power coefficient (-)     : {:2f}'.format(CP[0]))
print('Thrust coefficient (-)    : {:2f}'.format(CT[0]))
print('Torque coefficient (-)    : {:2f}'.format(CQ[0]))
print('Moment coefficient (-)    : {:2f}'.format(CM[0]))
