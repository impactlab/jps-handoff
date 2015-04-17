SELECT A.*, B.*, C.*
FROM checkmeter.investigation A
LEFT JOIN checkmeter.irregularity B
ON A.irregularityid = B.irregularityid
LEFT JOIN checkmeter.lossimpacting C
ON B.irregdescription = C.description
WHERE C.lossimpacting IS NOT NULL
