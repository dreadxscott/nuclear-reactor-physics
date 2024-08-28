import os
import openmc
import openmc.model

# Set the environment variable for OpenMC cross-sections
os.environ['OPENMC_CROSS_SECTIONS'] = '/path/to/endf_data/cross_sections.xml'

# Define materials
u238 = openmc.Material(name='U-238')
u238.add_nuclide('U238', 1.0)
u238.set_density('g/cm3', 18.95)  # Uranium density

water = openmc.Material(name='Water')
water.add_element('H', 2.0)
water.add_element('O', 1.0)
water.set_density('g/cm3', 1.0)
water.add_s_alpha_beta('c_H_in_H2O')  # Thermal scattering

zirconium = openmc.Material(name='Zirconium')
zirconium.add_element('Zr', 1.0)
zirconium.set_density('g/cm3', 6.52)  # Zirconium density

materials = openmc.Materials([u238, water, zirconium])

# Define geometry
fuel_or = 0.42
clad_ir = 0.45
clad_or = 0.48
pitch = 1.26

fuel = openmc.ZCylinder(r=fuel_or)
clad_inner = openmc.ZCylinder(r=clad_ir)
clad_outer = openmc.ZCylinder(r=clad_or)

fuel_region = -fuel
clad_region = +clad_inner & -clad_outer
water_region = +clad_outer

fuel_cell = openmc.Cell(region=fuel_region)
fuel_cell.fill = u238

clad_cell = openmc.Cell(region=clad_region)
clad_cell.fill = zirconium  # Cladding material

water_cell = openmc.Cell(region=water_region & +openmc.YPlane(pitch / 2) & -openmc.YPlane(pitch / 2) &
                        +openmc.XPlane(pitch / 2) & -openmc.XPlane(pitch / 2))
water_cell.fill = water

universe = openmc.Universe(cells=[fuel_cell, clad_cell, water_cell])
geometry = openmc.Geometry(universe)

# Define settings
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 1000

# Define a point source of neutrons
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.energy = openmc.stats.Discrete([2.0e6], [1.0])  # Neutrons with 2 MeV energy
settings.source = source

# Define tally to track reactions
tally = openmc.Tally(name='capture_reactions')
tally.filters = [openmc.CellFilter(fuel_cell)]
tally.scores = ['(n,gamma)']  # Capture reaction

tallies = openmc.Tallies([tally])

# Export to XML
materials.export_to_xml()
geometry.export_to_xml()
settings.export_to_xml()
tallies.export_to_xml()

# Run OpenMC
openmc.run()

# Process results
sp_filename = 'statepoint.100.h5'
with openmc.StatePoint(sp_filename) as sp:
    tally = sp.get_tally(name='capture_reactions')
    print(tally)
