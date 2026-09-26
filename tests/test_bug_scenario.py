from relaygrid.operations.dispatch import prioritize_incidents
from relaygrid.weather.storm_cells import StormCell, affected_assets, merge_cells


def test_transitive_storms_do_not_duplicate_assets_or_incidents():
    cells = [
        StormCell("A", 0.0, 0.00, 10.0, 25.0, 10.0, 0.0, 100.0),
        StormCell("B", 0.0, 0.08, 10.0, 25.0, 10.0, 10.0, 110.0),
        StormCell("C", 0.0, 0.16, 10.0, 25.0, 10.0, 20.0, 120.0),
    ]
    assert [[cell.cell_id for cell in group] for group in merge_cells(cells)] == [["A", "B", "C"]]

    assets = [("SW1", 0.0, 0.0), ("SW1", 0.0, 0.0), ("SW2", 0.0, 0.02)]
    impacted = affected_assets(cells[0], assets, timestamp_s=50.0)
    assert [asset_id for asset_id, _ in impacted] == ["SW1", "SW2"]

    low = ("I1", 10, 0, 0, 5.0)
    high = ("I1", 10, 1, 1, 6.0)
    other = ("I2", 20, 0, 0, 5.0)
    prioritized = prioritize_incidents([low, other, high])
    assert [incident[0] for incident in prioritized].count("I1") == 1
    assert next(item for item in prioritized if item[0] == "I1") == high
