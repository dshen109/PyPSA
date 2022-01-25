import pypsa
from numpy.testing import assert_array_almost_equal as equal
import pandas as pd

solver_name = 'gurobi_direct'


def test_quadratic_generator():

    times = pd.date_range('2021-01-01 00:00', '2021-01-01 00:10',
                          freq='5T')

    loads = pd.DataFrame({'load': [220, 240, 250]},
                         index=times)
    gas_curve = [0.4, 0.5]
    coal_curve = [0.5, 0]

    network = pypsa.Network(snapshots=times)
    network.add('Bus', 'bus1')
    network.add('Generator', 'gas', bus='bus1', committable=False,
                supply_curve_linear=gas_curve[0],
                supply_curve_quad=gas_curve[1], p_nom=20)
    network.add('Generator', 'coal', bus='bus1', committable=False,
                supply_curve_linear=coal_curve[0], p_nom=230)
    network.add('Load', 'load', bus='bus1',
                p_set=loads.values.flatten().tolist())

    network.lopf(network.snapshots[:], pyomo=True, solver_name='gurobi_direct')
    power = network.generators_t.p
    price = network.buses_t.marginal_price

    equal(power.gas.values, [0.1, 10, 20])
    equal(power.coal.values, [219.9, 230, 230])

    equal(price.values.flatten(), [0.5, 10.4, 20.4])
