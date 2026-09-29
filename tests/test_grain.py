import pandas as pd

from src.grain import bridge_explodes_fact, orphan_bridge


def test_orphan_detection():
    fact = pd.DataFrame([{"EncounterKey": "E1"}])
    bridge = pd.DataFrame([{"EncounterKey": "E2", "DxCode": "I10"}])
    assert len(orphan_bridge(bridge, fact)) == 1


def test_explosion_flag():
    fact = pd.DataFrame([{"EncounterKey": "E1", "LOSDays": 2}])
    bridge = pd.DataFrame(
        [
            {"EncounterKey": "E1", "DxCode": "I10", "DiagnosisSeq": 1},
            {"EncounterKey": "E1", "DxCode": "E11.9", "DiagnosisSeq": 2},
        ]
    )
    assert bool(bridge_explodes_fact(fact, bridge))
