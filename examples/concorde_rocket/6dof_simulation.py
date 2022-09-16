# -*- coding: utf-8 -*-
# Author: Felipe Bogaerts de Mattos
# Contact me at felipe.bogaerts@engenharia.ufjf.br.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.

"""
The 6DOF simulation is under development.
"""

import time

from rocketsolver.models.propulsion.grain import Grain
from rocketsolver.models.propulsion.grain.bates import BatesSegment
from rocketsolver.models.propulsion.structure import (
    MotorStructure,
    Nozzle,
)
from rocketsolver.models.propulsion.structure.chamber import BoltedCombustionChamber
from rocketsolver.models.propellants.solid import get_solid_propellant_from_name
from rocketsolver.models.recovery import Recovery
from rocketsolver.models.rocket import Rocket3D
from rocketsolver.models.materials.metals import Steel, Al6063T5
from rocketsolver.models.materials.elastics import EPDM
from rocketsolver.models.propulsion.thermals import ThermalLiner
from rocketsolver.models.recovery.events import (
    AltitudeBasedEvent,
    ApogeeBasedEvent,
)
from rocketsolver.models.recovery.parachutes import HemisphericalParachute
from rocketsolver.models.fuselage import Fuselage3D
from rocketsolver.models.fuselage.components.fins.trapezoidal import TrapezoidalFins
from rocketsolver.models.fuselage.components.body import CylindricalBody
from rocketsolver.models.fuselage.components.nosecones.haack import HaackSeriesNoseCone
from rocketsolver.models.atmosphere import Atmosphere1976
from rocketsolver.models.propulsion import SolidMotor
from rocketsolver.simulations.ballistics_6dof import (
    Ballistic6DOFSimulation,
    Ballistic6DOFSimulationParams,
)


def main():
    start = time.time()  # starting timer

    # Motor:
    propellant = get_solid_propellant_from_name(prop_name="KNSB-NAKKA")

    grain = Grain()

    bates_segment_45 = BatesSegment(
        outer_diameter=115e-3,
        core_diameter=45e-3,
        length=200e-3,
        spacing=10e-3,
    )
    bates_segment_60 = BatesSegment(
        outer_diameter=115e-3,
        core_diameter=60e-3,
        length=200e-3,
        spacing=10e-3,
    )

    grain.add_segment(bates_segment_45)
    grain.add_segment(bates_segment_45)
    grain.add_segment(bates_segment_45)
    grain.add_segment(bates_segment_45)
    grain.add_segment(bates_segment_60)
    grain.add_segment(bates_segment_60)
    grain.add_segment(bates_segment_60)

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

    # Recovery:
    recovery = Recovery()
    recovery.add_event(
        ApogeeBasedEvent(
            trigger_value=1,
            parachute=HemisphericalParachute(diameter=1.25),
        )
    )
    recovery.add_event(
        AltitudeBasedEvent(
            trigger_value=450,
            parachute=HemisphericalParachute(diameter=2.66),
        )
    )

    # Fuselage:
    nose_cone = HaackSeriesNoseCone(
        material=Al6063T5(),
        center_of_gravity=0.5,
        mass=2,
        length=0.5,
        base_diameter=0.17,
        C=0,
    )

    fuselage = Fuselage3D(
        nose_cone=nose_cone,
        mass_without_motor=25,
        I_x=1.2,
        I_y=1.3,
        I_z=1.2,
        I_xy=0.0,
        I_xz=0.0,
        I_yz=0.0,
        I_yx=0.0,
        I_zx=0.0,
        I_zy=0.0,
    )

    fuselage.add_body_segment(
        body_segment=CylindricalBody(
            material=Al6063T5(),
            center_of_gravity=1,
            mass=10,
            outer_diameter=0.17,
            length=3,
            rugosity=5e-3,
            constant_K=0,
            fins=TrapezoidalFins(
                material=Al6063T5(),
                mass=0.1,
                center_of_gravity=0,
                thickness=0.005,
                count=4,
                rugosity=5e-3,
                base_length=150e-3,
                tip_length=100e-3,
                average_span=110e-3,
                height=80e-3,
                body_diameter=0.17,
            ),
        )
    )

    rocket = Rocket3D(propulsion=motor, recovery=recovery, fuselage=fuselage)

    # Simulation:
    params = Ballistic6DOFSimulationParams(
        atmosphere=Atmosphere1976(),
        d_t=0.001,
        initial_elevation_amsl=636,
        rail_length=5,
        launch_angle=90,
        heading_angle=85,
        igniter_pressure=1e6,
    )
    simulation = Ballistic6DOFSimulation(rocket=rocket, params=params)

    simulation.run()
    simulation.print_results()

    print("\n\nExecution time: %.4f seconds\n\n" % (time.time() - start))


if __name__ == "__main__":
    main()
