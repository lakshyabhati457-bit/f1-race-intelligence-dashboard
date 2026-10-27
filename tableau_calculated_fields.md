# Tableau calculated fields

Use these calculations after connecting the CSV files and establishing the joins described in README.md.

## Podium Flag
```tableau
IF INT([positionOrder]) >= 1 AND INT([positionOrder]) <= 3 THEN 1 ELSE 0 END
```

## Driver Points
```tableau
SUM([points])
```

## Podium Finishes
```tableau
SUM([Podium Flag])
```

## Season label
```tableau
STR([year])
```

## Retirement / non-finish proxy
Build this only after joining `status.csv`:
```tableau
IF LOWER([status]) = "finished"
OR CONTAINS(LOWER([status]), "lap") THEN "Finished / classified"
ELSE "Other status" END
```
Review edge cases before using this as a formal reliability KPI.
