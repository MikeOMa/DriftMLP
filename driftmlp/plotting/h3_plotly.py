import folium
import h3.api.basic_int as h3

from .shape_helpers import split_polys


def visualize_hexagons(hexagons, color="red", folium_map=None, weight=8, fix=True):
    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons.
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # polygons = [split_polys(q,shapely_ret=False) for q in polygons]
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v: v[0], polyline))
        lng.extend(map(lambda v: v[1], polyline))
        if fix:
            polyline_expanded = split_polys(
                [point[::-1] for point in polyline], shapely_ret=False
            )
            polyline_expanded = [
                [point[::-1] for point in poly] for poly in polyline_expanded
            ]
            polylines = polylines + polyline_expanded
        else:
            polylines.append(polyline)

    if folium_map is None:
        m = folium.Map(
            location=[sum(lat) / len(lat), sum(lng) / len(lng)],
            zoom_start=3,
            tiles="cartodbpositron",
        )
    else:
        m = folium_map
    for polyline in polylines:
        my_PolyLine = folium.PolyLine(locations=polyline, weight=weight, color=color)
        m.add_child(my_PolyLine)
    return m


def visualize_polygon(polyline, color):
    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(
        location=[sum(lat) / len(lat), sum(lng) / len(lng)],
        zoom_start=13,
        tiles="cartodbpositron",
    )
    my_PolyLine = folium.PolyLine(locations=polyline, weight=8, color=color)
    m.add_child(my_PolyLine)
    return m


def visualize_point(points, folium_map=None, text=None, **kwargs):
    lat = [point[0] for point in points]
    lng = [point[1] for point in points]

    if folium_map is None:
        m = folium.Map(
            location=[sum(lat) / len(lat), sum(lng) / len(lng)],
            zoom_start=5,
            tiles="cartodbpositron",
        )
    else:
        m = folium_map

    for point in points:
        my_marker = folium.Marker([point[1], point[0]], popup=text, **kwargs)
        m.add_child(my_marker)
    return m
