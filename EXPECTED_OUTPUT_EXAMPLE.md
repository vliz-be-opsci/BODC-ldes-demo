# Expected Output Example

This document shows an example of what the LDES fragment output will look like after the template changes.

## Before (Old Format - Non-compliant)

```turtle
<http://vocab.nerc.ac.uk/ldes/P02/2012-01-01%2000%3A00%3A00_2012-12-31%2000%3A00%3A00>
    a tree:Node ;
    ldes:retentionPolicy [
        a ldes:LatestVersionSubset ;
        ldes:amount 100 ;
        ldes:versionKey ( dc:isVersionOf )
    ] .

<http://vocab.nerc.ac.uk/ldes/P02>
  a ldes:EventStream ;
  ldes:timestampPath dc:modified ;
  ldes:versionOfPath dc:isVersionOf ;
  tree:shape [
    ...
  ] ;
  tree:view <http://vocab.nerc.ac.uk/ldes/P02/2012-01-01%2000%3A00%3A00_2012-12-31%2000%3A00%3A00> ;
  .
```

## After (New Format - LDES Spec Compliant)

```turtle
<http://vocab.nerc.ac.uk/ldes/P02/2012-01-01%2000%3A00%3A00_2012-12-31%2000%3A00%3A00>
    a tree:Node ;
    ldes:retentionPolicy [
        a ldes:LatestVersionSubset ;
        ldes:versionAmount 100
    ] .

<http://vocab.nerc.ac.uk/ldes/P02>
  a ldes:EventStream ;
  ldes:timestampPath dc:modified ;
  ldes:versionOfPath dc:isVersionOf ;
  ldes:immutable true ;
  ldes:pollingInterval "PT5M"^^xsd:duration ;
  tree:shape [
    ...
  ] ;
  tree:view <http://vocab.nerc.ac.uk/ldes/P02/2012-01-01%2000%3A00%3A00_2012-12-31%2000%3A00%3A00> ;
  .
```

## Key Differences

1. **Retention Policy**:
   - `ldes:amount` → `ldes:versionAmount` (spec-compliant property name)
   - Removed `ldes:versionKey` (not part of the spec)

2. **Event Stream**:
   - Added `ldes:immutable true` (new configurable property)
   - Added `ldes:pollingInterval "PT5M"^^xsd:duration` (new configurable property)

## Template Variables

The template now accepts these additional variables:
- `immutable`: Boolean string ("true" or "false") - optional
- `polling_interval`: ISO 8601 duration string - optional

Both properties are optional and will only be included in the output if the corresponding variable is defined.
