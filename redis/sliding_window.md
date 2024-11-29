# Sliding Window

This redis LUA command reads and updates a redis "sorted set" used as a "sliding window"
index. It checks that 1 or more "sliding window" counters are below limits. If all
"sliding window" conditions are fullfilled, it records a new timestamped event in the
"sliding window" index...

## Usage

```
EVAL path/to/sliding_window.lua 1 key at_usec ttl_msec slwsize_ms slwlimit [slwsize_ms slwlimit]*
```

### Parameters

`key`: string | KEYS[1]
: key of the sorted set to be read & updated

`at_usec`: integer | ARGV[1]
: timestamp to use when accessing the sliding window index
: it is interpreted as the number of microseconds since 1970-01-01 (Unix Epoch)
: if at_usec is zero, it will be replaced by redis server current time.

`ttl_msec`: integer | ARGV[2]
: time to live in millisecond for the "sliding window" index referenced by slwkey.

`slwsize_ms`: integer | ARGV[3]
: sliding window size in millisecond
: the sliding window range is `[(at_usec - slwsize_ms) .. at_usec]`

`slwlimit`: integer | ARGV[4]
: maximum number of events in sliding window

It is possible to define & control more than 1 sliding windows by passing additional
`slwsize_ms`, `slwlimit` parameters to the command...

### Returns

error status code
: 0 in case all sliding windows were successfully checked
: i > 0 in case of error
: i is the index of the first failed sliding window

## Remarks

redis uses LUA version 5.1
LUA version 5.1 has a single number type that allows representing integers below 2^53

Internally this command manipulates microseconds precision timestamp.
It was found that LUA 5.1 integers are sufficient to represent such timestamp, below are
some brief explanations of why this is the case:

Assume we keep on using LUA 5.1 until 2070-01-01
The maximum value of the timestamp we need to consider is approximately

```
    tsmax = (100y * 365d * 24h * 3600s) * 1E6 = 3.1536E15
    tsmax requires 51.4859 bits < 53 bits
    tsmax requires 16 decimal digits
```
