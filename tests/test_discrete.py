from DriftMLP.drifter_indexing.discrete_system import h3_default, lon_lat_grid


def test_h3_discrete():
    expected = ((9.865832681734334, 4.7062868733504235),
                (9.283044268429405, 4.776797007446319),
                (9.000128062521423, 5.327669399373584),
                (9.298105196185011, 5.813779654081987),
                (9.88431730655166, 5.748137725634694),
                (10.169150245222395, 5.1914759627196165))
    expected = (( 4.7062868733504235, 9.865832681734334),
                (4.776797007446319, 9.283044268429405),
                (5.327669399373584,9.000128062521423),
                (5.813779654081987,9.298105196185011),
                (5.748137725634694,9.88431730655166),
                (5.1914759627196165, 10.169150245222395))

    transformer = h3_default(res=3)
    point = 5, 10
    ind = transformer.geo_to_ind(point[0], point[1])
    geo_boundary = transformer.ind_to_boundary(ind)
    print(geo_boundary)
    assert expected == geo_boundary


def test_lon_lat_grid():
    point = 5, 10
    transformer = lon_lat_grid(res=0.5)
    ind = transformer.geo_to_ind(point[0], point[1])
    geo_boundary = transformer.ind_to_boundary(ind)
    expected_ll = ((5.5, 10.5),
                   (5.5, 10.0),
                   (5.0, 10.0),
                   (5.0, 10.5))
    assert geo_boundary == expected_ll
