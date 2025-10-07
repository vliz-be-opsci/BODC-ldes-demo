# LDES Specification Compliance Changes

This document explains the important changes made to align the LDES fragment template with the official LDES specification as documented at https://semiceu.github.io/LinkedDataEventStreams/.

## Overview

The Linked Data Event Streams (LDES) specification defines standards for publishing and consuming event streams as Linked Data. This project has been updated to comply with the latest version of the specification.

## Changes Made

### 1. Retention Policy (Critical Change)

**Previous Implementation:**
```turtle
ldes:retentionPolicy [
    a ldes:LatestVersionSubset ;
    ldes:amount 100 ;
    ldes:versionKey ( dc:isVersionOf )
] .
```

**Updated Implementation:**
```turtle
ldes:retentionPolicy [
    a ldes:LatestVersionSubset ;
    ldes:versionAmount 100
] .
```

**Explanation:**
- Changed `ldes:amount` to `ldes:versionAmount` to align with the LDES specification
- Removed `ldes:versionKey` as it is no longer part of the retention policy definition in the spec
- The `ldes:versionAmount` property specifies how many versions of each member should be retained in the LDES

### 2. Immutable Property (New Feature)

**Implementation:**
```turtle
<http://vocab.nerc.ac.uk/ldes/{{collection}}>
  a ldes:EventStream ;
  ldes:timestampPath dc:modified ;
  ldes:versionOfPath dc:isVersionOf ;
  ldes:immutable true ;
  ...
```

**Explanation:**
- Added support for the `ldes:immutable` property in the EventStream
- This property can be set to `true` or `false` to indicate whether members in the event stream can be deleted or updated
- The property is now configurable through the `immutable` variable in `BODC_LDES_demo.py`
- When set to `true`, it indicates that members will never be removed from the event stream

### 3. Polling Interval (New Feature)

**Implementation:**
```turtle
<http://vocab.nerc.ac.uk/ldes/{{collection}}>
  a ldes:EventStream ;
  ldes:timestampPath dc:modified ;
  ldes:versionOfPath dc:isVersionOf ;
  ldes:pollingInterval "PT5M"^^xsd:duration ;
  ...
```

**Explanation:**
- Added support for the `ldes:pollingInterval` property in the EventStream
- This property indicates the minimum time clients should wait between polling requests
- The value is specified in ISO 8601 duration format (e.g., "PT5M" for 5 minutes, "PT1H" for 1 hour)
- This helps optimize client-server interactions and reduce unnecessary polling
- The property is configurable through the `polling_interval` variable in `BODC_LDES_demo.py`

## Configuration

These new features can be configured in the `BODC_LDES_demo.py` file:

```python
# define variables
collections = ["P02"]
begin_date = "2012-01-01 00:00:00"
end_date = "2021-01-02 00:00:00"
retention_period = 100
immutable = "true"  # Set to "true" or "false" to enable/disable immutability
polling_interval = "PT5M"  # ISO 8601 duration format (e.g., "PT5M" for 5 minutes)
```

### Configuration Options:

- **retention_period**: Integer value specifying the number of versions to retain
- **immutable**: String value `"true"` or `"false"` indicating if the stream is immutable
- **polling_interval**: ISO 8601 duration string (examples: "PT5M" = 5 minutes, "PT1H" = 1 hour, "P1D" = 1 day)

### Making Properties Optional:

If you want to make `ldes:immutable` or `ldes:pollingInterval` optional, you can:

1. Comment out the corresponding variable in `BODC_LDES_demo.py`
2. Or remove it from the `vars_dict` dictionary

The template will automatically skip these properties if they are not defined.

## Benefits of These Changes

1. **Compliance**: Ensures the LDES feed conforms to the official specification
2. **Interoperability**: Improves compatibility with LDES clients and tools that expect the standard format
3. **Flexibility**: Allows configuration of immutability and polling behavior based on use case requirements
4. **Client Optimization**: Polling interval helps clients avoid unnecessary requests

## References

- LDES Specification: https://semiceu.github.io/LinkedDataEventStreams/
- ISO 8601 Duration Format: https://en.wikipedia.org/wiki/ISO_8601#Durations

## Migration Notes

When regenerating LDES fragments with the updated template, the output will include:
- Correct `ldes:versionAmount` property in retention policies
- Optional `ldes:immutable` property on EventStreams (if configured)
- Optional `ldes:pollingInterval` property on EventStreams (if configured)

Existing clients consuming the LDES feed should continue to work, as the changes are primarily additive (except for the retention policy property rename, which is a spec compliance fix).
