# -*- coding: utf-8 -*-
# Author: Felipe Bogaerts de Mattos
# Contact me at felipe.bogaerts@engenharia.ufjf.br.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

from rocketsolver.models.materials.elastics import EPDM
from rocketsolver.models.materials.metals import Steel, Al6063T5
from rocketsolver.models.propellants.solid import get_solid_propellant_from_name
from rocketsolver.models.propulsion import SolidMotor
from rocketsolver.models.propulsion.grain import Grain
from rocketsolver.models.propulsion.grain.bates import BatesSegment
from rocketsolver.models.propulsion.structure import MotorStructure
from rocketsolver.models.propulsion.structure.nozzle import Nozzle
from rocketsolver.models.propulsion.structure.chamber import BoltedCombustionChamber
from rocketsolver.models.propulsion.thermals import ThermalLiner
from rocketsolver.simulations.internal_ballistics import (
    InternalBallistics,
    InternalBallisticsParams,
)


def main():
    # Motor configuration:
    propellant = get_solid_propellant_from_name(prop_name="KNSB-NAKKA")
    # Measured, average density of the segments:
    propellant.density = 1656.01

    grain = Grain()

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.27e-3,
            core_diameter=46.44e-3,
            length=201.03e-3,
            spacing=10.18e-3,
        )
    )  # grain no 2

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.56e-3,
            core_diameter=45.15e-3,
            length=194.05e-3,
            spacing=18.24e-3,
        )
    )  # grain no 1

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.70e-3,
            core_diameter=45.58e-3,
            length=202.78e-3,
            spacing=11.68e-3,
        )
    )  # grain no 6

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.72e-3,
            core_diameter=45.34e-3,
            length=194.36e-3,
            spacing=11.55e-3,
        )
    )  # grain no 4

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.49e-3,
            core_diameter=60.60e-3,
            length=204.18e-3,
            spacing=11.53e-3,
        )
    )  # grain no 7

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.77e-3,
            core_diameter=60.49e-3,
            length=198.72e-3,
            spacing=10.43e-3,
        )
    )  # grain no 5

    grain.add_segment(
        BatesSegment(
            outer_diameter=114.74e-3,
            core_diameter=60.64e-3,
            length=193.32e-3,
            spacing=9.92e-3,
        )
    )  # grain no 3

    nozzle = Nozzle(
        throat_diameter=37e-3,
        divergent_angle=12,
        convergent_angle=45,
        expansion_ratio=8,
        material=Steel(),
    )

    liner = ThermalLiner(thickness=2e-3, material=EPDM())

    chamber = BoltedCombustionChamber(
        casing_inner_diameter=128.2e-3,
        outer_diameter=141.3e-3,
        liner=liner,
        length=grain.total_length + 10e-3,
        casing_material=Al6063T5(),
        bulkhead_material=Al6063T5(),
        screw_material=Steel(),
        max_screw_count=30,
        screw_clearance_diameter=9e-3,
        screw_diameter=6.75e-3,
    )

    structure = MotorStructure(
        safety_factor=4,
        dry_mass=21.013,
        nozzle=nozzle,
        chamber=chamber,
    )

    motor = SolidMotor(grain=grain, propellant=propellant, structure=structure)

    # Simulation:
    params = InternalBallisticsParams(0.01, 1.5e6, 0.1e6)
    simulation = InternalBallistics(motor=motor, params=params)
    simulation.run()

    simulation.print_results()


if __name__ == "__main__":
    main()
