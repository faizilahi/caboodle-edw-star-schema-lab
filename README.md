# Caboodle Star Schema Design Review - Encounter Grain Fight

Faiz Elahi - https://www.linkedin.com/in/faizilahi - https://pendataco.com - https://github.com/faizilahi

Portfolio star-schema lab on synthetic Caboodle-style dimensions and facts. Not an Epic Caboodle engagement; not employment at a health system.

## Grain fights

The first fight is always **encounter vs diagnosis**. `FactEncounter` wants one row per `EncounterKey` (CSN). Coders dump multiple ICD-10s per stay. If you shove diagnosis onto the encounter fact you either lose codes or explode the grain. This repo keeps encounter at stay grain and puts diagnoses on `BridgeEncounterDiagnosis` with a sequence number and present-on-admission flag.

Second fight: **medication administration vs order**. Administrations are timestamped events; orders are intentions. `FactMedicationAdmin` is event grain. Do not conform it to order grain just because pharmacy wants a simpler join.

## Conformed patient

`DimPatient` is the conformed person across Clarity ambulatory, Clarity inpatient, and claims. Durable key is `PatientDurableKey` (synthetic). Same MRN from two source systems collapses here with a source-priority rule: inpatient Clarity wins demographics when conflicted. See `src/conformed_patient.py`.

## Fact vs bridge

| Object | Grain | Why |
|--------|-------|-----|
| `FactEncounter` | EncounterKey | Length of stay, department, admit type |
| `BridgeEncounterDiagnosis` | EncounterKey + DxCode + Seq | Many diagnoses per stay |
| `FactMedicationAdmin` | AdminEventKey | Real-time-ish MAR events |
| `DimDiagnosis` | DxCode | Conformed ICD-10 |

Run the design checks:

```bash
pip install -r requirements.txt
python scripts/generate_star.py
python scripts/run_design_review.py
pytest -q
```

The runner prints grain violations (duplicate encounter keys, bridge rows missing parent fact, patient durable-key collisions).

Synthetic rows only; kept small for git.

---

Faiz Elahi - [LinkedIn](https://www.linkedin.com/in/faizilahi) - [pendataco.com](https://pendataco.com) - [GitHub](https://github.com/faizilahi)

