-- Grain and bridge integrity checks (Snowflake-shaped)

-- Duplicate encounter keys (should be 0)
SELECT EncounterKey, COUNT(*) AS c
FROM FactEncounter
GROUP BY 1
HAVING COUNT(*) > 1;

-- Bridge orphans
SELECT b.*
FROM BridgeEncounterDiagnosis b
LEFT JOIN FactEncounter f ON f.EncounterKey = b.EncounterKey
WHERE f.EncounterKey IS NULL;

-- Diagnosis explosion warning if reporting join is wrong
SELECT f.EncounterKey, COUNT(*) AS joined_rows
FROM FactEncounter f
JOIN BridgeEncounterDiagnosis b ON b.EncounterKey = f.EncounterKey
GROUP BY 1
HAVING COUNT(*) > 1;
