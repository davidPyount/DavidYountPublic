from gSheetClass import Sheet
import matplotlib.pyplot as plt
import numpy as np
import CoolProp as cp
from CoolProp.CoolProp import PhaseSI, PropsSI, get_global_param_string
from pintref import u,Q_
import ansys.fluent.core as pyfluent

# The ID of the spreadsheet.
SAMPLE_SPREADSHEET_ID = '1MXAXnyA1M9qKxzgbTsTFTUtmdIo-qNCpOLmiaSc6G2o'

#Note: THIS SCRIPTS PULLS GOOGLE SHEET DATA EVERYTIME IT RUNS. RUNNING THIS WITHOUT HAVING ACCESS TO THE REQUIRED GOOGLE SHEET SPECIFIED ABOVE WILL CAUSE THE SCRIPT TO FAIL.
#This code is shared with the intent of demonstrating my familiarity with these python libraries. If you would like a video demo of it working let me know.

## Notes ##
#200mm <= D <= 250mm
#0.4 <= betta <= 0.75
#2x10^5 <= ReD < 1x10^6
# Under these conditions our discharge coefficient is C = 0.995
# Paper one says a 1-1.5% accuracy is possible.
# Criteria for validation: 
# Ra/d < 10^-4, where Ra is roughness criterion and d is the throat diameter
# Entrance cylinder length cannot be < D
# Roughness must be less that 10^-4d
# Pressure ducts must have a diamter 1/10 or 1/5 of a diameter of the venturi flowsection and be 4 or more. (An even number)

def main():
    s = Sheet(SAMPLE_SPREADSHEET_ID)
    s.setPintMode("ENABLED") #Enables easy unit reading/writing.

    D = s.read("InletD")
    print(D)

    LOXmf = s.read("LOXMassFlow")
    print(LOXmf)

    Pinlet = s.read("InletP")
    Pinlet.ito('Pa')
    print(Pinlet)


    C = 0.995*u.dimensionless #Coefficient of discharge for machined venturi (sized at 2inch line size, lowest possible value, closest to our case)
    s.write('DischargeCoefficient',C)
    beta = s.read('DiameterRatio') #0.4667 #Diameter ratio. Some value between 0.4 and 0.75. Smaller is better (until it chokes our flow)
    d = D*beta#little d should be 0.35 for beta 0.4667
    s.write("ThroatDiameter",d)


    gamma = 1*u.dimensionless #Expansability factor. Assumed 1 for incompressible fluid.
    s.write("ExpansibilityFactor",gamma)
    E = np.sqrt(1-beta**4) #Velocity of approach factor
    loxDensity = PropsSI('D','T',88.9,'P',6998179,'Oxygen') * u.kg/u.m**3
    s.write('LoxDensity',loxDensity)
    LNGDensity = PropsSI('D','T',88.9,'P',6998179,'Methane') * u.kg/u.m**3
    s.write('LNGDensity',LNGDensity)
    A1 = np.pi * (1/4) * (D**2)
    A2 = np.pi * (1/4) * (d**2)
    A1.ito('m**2')
    A2.ito('m**2')
    d.ito('m')
    s.write('ConvergenceLength',D)
    

    Pmeasured = 985*u.psi
    Pmeasured.ito('Pa')


    #Ideal bernoulli calculated value
    delP = Pinlet - Pmeasured
    delP = 1.5*10**8*u.Pa
    Bernoulliqm = loxDensity*A1*np.sqrt((2*delP)/(loxDensity*( (A1/A2)**2 - 1)))
    Bernoulliqm.ito_base_units()
    print(Bernoulliqm)

    #Using the ISO Standard Equation
    ISOqmLOX = C/E * gamma * (np.pi/4)*d**2*np.sqrt(2*delP*loxDensity)
    ISOqmLOX.ito_base_units()
    print(ISOqmLOX)
    s.write("LoxMassFlowMeasured",ISOqmLOX) #write iso standard adjusted flow rate for LOX

    ISOqmLNG = C/E * gamma * (np.pi/4)*d**2*np.sqrt(2*delP*LNGDensity)
    ISOqmLNG.ito_base_units()
    s.write("LNGMassFlowMeasured",ISOqmLNG) #write iso standard adjusted flow rate for LNG

if __name__ == '__main__':
    main()