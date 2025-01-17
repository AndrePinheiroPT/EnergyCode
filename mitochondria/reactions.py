from random import randint
from time import sleep
from mitochondria.chemistry import *

# Set all molecules
HYDROGEN_CATION = Molecules('H+', 'Hydrogen cation')
WATER = Molecules('H2O', 'Water')
ADP = Molecules('C10H15N5O10P2', 'ADP')
ATP = Molecules('C10H15N5O10P3', 'ATP')
NAD = Molecules('C21H27N7O14P2', 'NAD+')
NADH = Molecules('C21H28N7O14P2', 'NADH')
FAD = Molecules('C27H33P2N9O15', 'FAD')
FADH2 = Molecules('C27H35N9O15P2', 'FADH2')
CARBON_DIOXIDE = Molecules('CO2', 'Carbon dioxide')
PGAL = Molecules('C3H5O5P','PGAL')
GLICOSE = Molecules('C6H12O6', 'Glicose')
OXYGEN_ATOM = Molecules('O', 'Oxygen atom')
OXYGEN = Molecules('O2', 'Oxygen')
PYRUVATE = Molecules('C3H4O3', 'Pyruvate')
LATIC_ACID = Molecules('C3H6O3', 'Pyruvate')
ETANOL = Molecules('C2H5OH', 'Etanol')
COA = Molecules('C21H36N7O16P3S', 'CoA')
ACETYL_COA = Molecules('C23H38N7O17P3S', 'Acetyl CoA')
OXALOACETIC_ACID = Molecules('C4H4O5', 'Oxaloacetic acid')
CITRIC_ACID = Molecules('C6H8O7', 'Citric acid')

# Define systems
cytoplasm_system = 0
mitochondria_inner_system = 0
mitochondria_outer_system = System([])

# Define number of electrons in cahin
complexIV = 0
Q = 0

def glycolysis():
    cytoplasm_system.do_reaction(1*[GLICOSE] + 2*[ATP], 2*[PGAL] + 2*[ADP])
    cytoplasm_system.do_reaction(1*[PGAL, NAD] + 2*[ADP], 1*[PYRUVATE, NADH, HYDROGEN_CATION, HYDROGEN_CATION] + 2*[ATP])


def pyruvate_reduction(lost_CO2):
    if lost_CO2:
        cytoplasm_system.do_reaction(1*[PYRUVATE, NADH, HYDROGEN_CATION], 1*[NAD, LATIC_ACID])
    else:
        cytoplasm_system.do_reaction(1*[PYRUVATE, NADH, HYDROGEN_CATION], 1*[NAD, CARBON_DIOXIDE, ETANOL])


def acetyl_CoA_synthase():
    mitochondria_inner_system.do_reaction(1*[PYRUVATE, NAD, COA], 1*[CARBON_DIOXIDE, NADH, HYDROGEN_CATION, ACETYL_COA])


def krebs_circle():
    mitochondria_inner_system.do_reaction(1*[ACETYL_COA, OXALOACETIC_ACID], 1*[CITRIC_ACID])
    mitochondria_inner_system.do_reaction(
        1*[CITRIC_ACID, FAD, ADP] + 3*[NAD], 
        2*[CARBON_DIOXIDE] + 1*[OXALOACETIC_ACID, FADH2, ATP] + 3*[NADH, HYDROGEN_CATION]
    )


def atpase():
    # Makes ATP using the gradient of hydrogen cations, it is need two hydrogens of difference
    # to do this.
    if mitochondria_outer_system.length(HYDROGEN_CATION) > mitochondria_inner_system.length(HYDROGEN_CATION):
        if mitochondria_outer_system.length(HYDROGEN_CATION) >= 2:
            for i in range(0, 2):
                mitochondria_outer_system.remove_molecule(HYDROGEN_CATION)
                mitochondria_inner_system.add_molecule(HYDROGEN_CATION)
            mitochondria_inner_system.do_reaction([ADP], [ATP])


def hydro_protein():
    # Ative transport
    for k in range(0, 2):
        mitochondria_inner_system.remove_molecule(HYDROGEN_CATION)
        mitochondria_outer_system.add_molecule(HYDROGEN_CATION)


def electron_transport_chain():
    global Q, complexIV

    # Get all electrons and add them in Q
    if mitochondria_inner_system.length(NADH) >= 1 and mitochondria_inner_system.length(HYDROGEN_CATION) >= 2:
        hydro_protein()
        mitochondria_inner_system.do_reaction(1*[NADH], 1*[NAD] + 2*[HYDROGEN_CATION])
        Q += 2

    if mitochondria_inner_system.length(FADH2) >= 1 and mitochondria_inner_system.length(HYDROGEN_CATION) >= 2:
        hydro_protein()
        mitochondria_inner_system.do_reaction(1*[FADH2], 1*[FAD] + 2*[HYDROGEN_CATION])
        Q += 2

    # Protein which uses electrons to do ative trasport
    if mitochondria_inner_system.length(HYDROGEN_CATION) >= 2 and Q >= 2 and complexIV < 4:
        hydro_protein()
        Q -= 2
        complexIV += 2

    # Protein which uses electrons to do ative trasport and make water with them
    if mitochondria_inner_system.length(HYDROGEN_CATION) >= 4 and mitochondria_inner_system.length(OXYGEN) >= 1 and complexIV == 4:
        complexIV -= 4
        mitochondria_inner_system.do_reaction(4*[HYDROGEN_CATION] + 2*[OXYGEN], 2*[WATER])


def show_status(opt):
    if opt == 1:
        print(f'cytoplasm_system: Glicose {cytoplasm_system.length(GLICOSE)} | ATP {cytoplasm_system.length(ATP)} | NADH+ {cytoplasm_system.length(NADH)}  ', end='/  ')
        print(f'mitochondria_inner_system: ATP {mitochondria_inner_system.length(ATP)} | NADH {mitochondria_inner_system.length(NADH)} | CO2 {mitochondria_inner_system.length(CARBON_DIOXIDE)} ', end='')
        print(f'| FADH2 {mitochondria_inner_system.length(FADH2)} | H+ {mitochondria_inner_system.length(HYDROGEN_CATION)} | Water {mitochondria_inner_system.length(WATER)} | Nº of electrons in chain {Q} ')
    else:
        print(f'cytoplasm_system: Glicose {cytoplasm_system.length(GLICOSE)} | ATP {cytoplasm_system.length(ATP)} | NADH+ {cytoplasm_system.length(NADH)} | CO2 {cytoplasm_system.length(CARBON_DIOXIDE)} | Latic acid {cytoplasm_system.length(LATIC_ACID)} | Etanol {cytoplasm_system.length(ETANOL)}')


def simulation(o2, glicose, coa, fad, atp_cy, atp_mi, adp_cy, adp_mi, nad_cy, nad_mi, nadh_cy, nadh_mi, opt):
    global cytoplasm_system, mitochondria_inner_system

    # Set the values of the systems
    cytoplasm_system = System(glicose*[GLICOSE] + atp_cy*[ATP] + adp_cy*[ADP] + nad_cy*[NAD])
    mitochondria_inner_system = System(coa*[COA] + nad_mi*[NAD] + fad*[FAD] + 1*[OXALOACETIC_ACID] + adp_mi*[ADP] + o2*[OXYGEN])

    while True:
        glycolysis()

        if opt == 1:
            if cytoplasm_system.length(PYRUVATE) >= 1:
                cytoplasm_system.remove_molecule(PYRUVATE)
                mitochondria_inner_system.add_molecule(PYRUVATE)

            if cytoplasm_system.length(NADH) >= 1:
                cytoplasm_system.remove_molecule(NADH)
                mitochondria_inner_system.add_molecule(NADH)

            acetyl_CoA_synthase()
            krebs_circle()

            electron_transport_chain()
            atpase()

        if opt == 2:
            pyruvate_reduction(False)
        if opt == 3:
            pyruvate_reduction(True)

        show_status(opt)
        sleep(1/4)
    






