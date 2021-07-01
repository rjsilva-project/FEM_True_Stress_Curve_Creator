# coding: utf-8
#Code created by Ramon Juan Silva in December 2020
#The code uses the Krupkowski method to calculate the true stress vs true strain from basic material data.
# Currently the code can just export excel, .png and PAM-CRASH deck. Implementation of ABAQUS and DYNA FEM option in development
# Global Library
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import  LineString
import os
import sys

# Functions

def is_simple_number(value): # Checking If the string is numeric or not
    if not value.strip().replace('-', '').replace('+', '').replace('.', '').isdigit():
        return False
    try:
         float(value)
    except ValueError:
         return False
    return True

# Code
os.system('cls')
print ("Welcome to the real stress x strain curve creator")
print ("Please select below one of the options that best fits your material:")
print ("1 - Mild Steel (YS < 500 MPa)")
print ("2 – High Strength Steel (YS > 500 MPa)")
print ("3 – Aluminum")
print ("4 – Others")
print ("Exit – Close the program")

e = 0
cal_ag = 0
density = 0

# Option to select basic materials properties

classe = input("Select the option: ").upper()

while not False:

    if classe == "1":
        e = 210
        cal_ag = 0.6
        density = 7.87
        break

    elif classe == "2":
        e = 210
        cal_ag = 0.8
        density = 7.87
        break

    elif classe == "3":
        e = 69
        cal_ag = 0.9
        density = 2.7
        break

    elif classe == "4":
        cal_ag = 0.9
        break

    elif classe == "EXIT":
        sys.exit()
        break
    
    else:
        classe = input("Please enter a valid alternative (1, 2, 3, 4 or exit): ").upper()


# Name of Material
os.system('cls')
name = input("What´s the name of the material? ").upper()

# If classe is equal to 4, so you need to include the information below (E and density)

if classe == "4":
    e = input("Please enter the Young Modulus (GPa) of the material?")
    while not False:
        if is_simple_number(e) is True:
            e = float(e)
            break
        else:
            e = input('Please enter a numeric value. ')

    density = input("Please enter the density (g/cm³) of the material?")
    while not False:
        if is_simple_number(density) is True:
            density = float(density)
            break
        else:
            density = input('Please enter a numeric value. ')

# Yield Stress

le = input("Please enter the yield stress (MPa) of the material?")
while not False:
    if is_simple_number(le) is True:
        le = float(le)
        break
    else:
        le = input('Please enter a numeric value. ')

# Ultimate Stress

lr = input("Please enter the ultimate stress (MPa) of the material?")
while not False:
    if is_simple_number(lr) is True:
        lr = float(lr)
        break
    else:
        lr = input('Please enter a numeric value. ')

# Elongation

elong = input("Please enter the elongation (%) of the material?")
while not False:
    if is_simple_number(elong) is True:
        elong = float(elong)
        break
    else:
        elong = input('Please enter a numeric value. ')

# Definition of n

ar = (1 + ((elong*cal_ag)/100))

n = (1.01 * np.log(ar))

alfa = n**n

beta = (n - np.log(ar))**n

k = le/beta

eps0 = n - np.log(ar)

f1 = (ar*lr/le)-(alfa/beta)

# Recalculation of n to approximate f1 to zero

while f1 < 0.0001:
    ar = (1 + ((elong*cal_ag)/100))

    n = n + 0.00001

    alfa = n**n

    beta = (n - np.log(ar))**n

    k = le/beta

    eps0 = n - np.log(ar)

    f1 = (ar*lr/le)-(alfa/beta)
    
# Calculation of the list of real curve

pstrain = [0, 0.003, 0.004, 0.005, 0.007, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2, 0.5, 1]
pstress = []
for strain in pstrain:
    stress = k * ((eps0 + strain)**n)
    pstress.append(stress)

#Pandas Dataframe

df = pd.DataFrame({'Plastic Strain': pstrain, 'Plastic Stress': pstress})

#Graph Export

df.plot(x="Plastic Strain", y="Plastic Stress", figsize=(10, 5))
plt.title('True Stress x Plastic Strain Curve ' + name) #adicionando o título
plt.xlabel('Plastic Strain')
plt.ylabel('True Stress')
plt.legend(loc='best')
plt.savefig(name+'_curve.png')

# Curve to Excel
df.to_excel(name+"_curve.xls", index=False)

# Converting the stress from MPa to GPa
df["Plastic Stress"] = df["Plastic Stress"]/1000

#PAM-CRASH shell (MAT 103) reference
cab_shell = []
cab_shell.append("$---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80 \n")
cab_shell.append("$#         IDMAT   MATYP             RHO   ISINT    ISHG  ISTRAT   IFROZ \n")
cab_shell.append("MATER /        1     103                       0       0      \n")
cab_shell.append("$# BLANK                                                     QVM           IDMPD \n")
cab_shell.append("                                                              1.               0 \n")
cab_shell.append("NAME  \n")
cab_shell.append("$#       E    SIGMAy        NU     ALPHA       HGM       HGW       HGQ        As \n")
cab_shell.append("         .CURVE            0.3                                                1. \n")
cab_shell.append("$#     LC1       LC2       LC3       LC4       LC5       LC6       LC7       LC8 \n")
cab_shell.append("         1         0         0         0         0         0         0         0 \n")
cab_shell.append("$#  ERATE1    ERATE2    ERATE3    ERATE4    ERATE5    ERATE6    ERATE7    ERATE8 \n")
cab_shell.append("        0.        0.        0.        0.        0.        0.        0.        0. \n")
cab_shell.append("$#EPSIpmax    STRAT1    STRAT2  REL_THIN  REL_THIC                         BLANK \n")
cab_shell.append("                  0.        0.                                                   \n")
cab_shell.append("$#             BLANK    STRAT3    STRAT4    STRAT5    STRAT6       KSI        Fo \n")
cab_shell.append("                            0.        0.        0.        0.       0.1        0. \n")
cab_shell.append("$# KEYWORD     VALUE                                                       BLANK \n")
cab_shell.append("                                                                                 \n")

#VPS function reference

funcao = []
funcao.append("$#         IDFUN  FUNTYP   SCALX   SCALY  SHIFTX  SHIFTY IFLMEAS   ICOMP \n")
funcao.append("FUNCT /        1      18      1.      1.      0.      0.       0       0 \n")
funcao.append("NAME    \n")
funcao.append("$#                             X               Y \n")
funcao.append("                              0.                 \n")
funcao.append("                           0.003                 \n")
funcao.append("                           0.004                 \n")
funcao.append("                           0.005                 \n")
funcao.append("                           0.007                 \n")
funcao.append("                            0.01                 \n")
funcao.append("                            0.02                 \n")
funcao.append("                            0.03                 \n")
funcao.append("                            0.04                 \n")
funcao.append("                            0.05                 \n")
funcao.append("                            0.06                 \n")
funcao.append("                            0.08                 \n")
funcao.append("                             0.1                 \n")
funcao.append("                            0.12                 \n")
funcao.append("                            0.15                 \n")
funcao.append("                             0.2                 \n")
funcao.append("                             0.5                 \n")
funcao.append("                              1.                 \n")
funcao.append("$---5---10----5---20----5---30----5---40----5---50----5---60----5---70----5---80 \n")

# Converting density to PAM-CRASH unit (mm, kg, ms)

dens_conv = density*(10**-6)

# Converting elongation to adimensional

elong_conv = elong/100

# Changing deck for the final values

cab_shell [5]

cab_shell [5] = "NAME " + name + "\n"

# Converting density string to list

l_densidade = list(str(dens_conv))

t_densidade = list(cab_shell [2])

count = 1
i = len(l_densidade) - 1

while i>=0:
    t_densidade [40 - count] = l_densidade [i]
    i = i - 1
    count = count +1
    
cab_shell [2] = "".join(t_densidade)

# Converting Young Modulus string to list

l_modulo = list(str(e))

t_modulo = list(cab_shell [7])

# Change Young Modulus in the VPS Deck

count = 1
i = len(l_modulo) - 1

while i>=0:
    t_modulo [9 - count] = l_modulo [i]
    i = i - 1
    count = count +1

cab_shell [7] = "".join(t_modulo)

# Converting elongation string to list

l_alongamento = list(str(elong_conv))

t_alongamento = list(cab_shell [13])

# Change alongation in the VPS Deck

count = 1
i = len(l_alongamento) - 1

while i>=0:
    t_alongamento [10 - count] = l_alongamento [i]
    i = i - 1
    count = count +1
    
cab_shell [13] = "".join(t_alongamento)

# Converting name of function

funcao [2]

funcao [2] = "NAME " + name + "_curva \n"

# Change Y values in the function

lo_stress = []

for i in pstress:
    stress_conv = i/1000
    lo_stress.append(stress_conv)

l_stress = []

for i in lo_stress:
     l_stress.append(format(i, '.3f'))

x = 4
z = 0

while not x == 22:

    u_stress = l_stress [z]

    t_stress = list(funcao [x])

    count = 1
    i = len(u_stress) - 1

    while i>=0:
        t_stress [48 - count] = u_stress[i]
        i = i - 1
        count = count +1

    funcao [x] = "".join(t_stress)
    
    x = x + 1
    z = z + 1

# Saving VPS Deck

arquivo = open(name+"_MAT_PAM_CRASH.inc", "w", encoding="utf-8")

arquivo.writelines(cab_shell)
arquivo.writelines(funcao)

arquivo.close()