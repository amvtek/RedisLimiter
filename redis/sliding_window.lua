--[[
This command reads and updates a redis "sorted set" used as a "sliding window" index.
It checks that 1 or more "sliding window" counters are below limits.
If all "sliding window" conditions are fullfilled, it records a new timestamped event
in the "sliding window" index...

Usage
-----
EVAL path/to/sliding_window.lua 1 key at_usec ttl_msec slwsize_ms slwlimit [slwsize_ms slwlimit]*

Parameters
----------
key: string | KEYS[1]
    key of the sorted set to be read & updated

at_usec: integer | ARGV[1]
    timestamp to use when accessing the sliding window index
    it is interpreted as the number of microseconds since 1970-01-01 (Unix Epoch)
    if at_usec is zero, it will be replaced by redis server current time.

ttl_msec: integer | ARGV[2]
    time to live in millisecond for the "sliding window" index referenced by slwkey.

slwsize_ms: integer | ARGV[3]
    sliding window size in millisecond
    the sliding window range is [(at_usec - slwsize_ms) .. at_usec]

slwlimit: integer | ARGV[4]
    maximum number of events in sliding window

It is possible to define & control more than 1 sliding windows by passing additional
slwsize_ms, slwlimit parameters to the command...

Returns
-------
error status code
    0 in case all sliding windows were successfully checked
    i > 0 in case of error
    i is the index of the first failed sliding window

========================================================================================
Remarks
-------
redis uses LUA version 5.1
LUA version 5.1 has a single number type that allows representing integers below 2^53

Internally this command manipulates microseconds precision timestamp.
It was found that LUA 5.1 integers are sufficient to represent such timestamp, below are
some brief explanations of why this is the case:

Assume we keep on using LUA 5.1 until 2070-01-01
The maximum value of the timestamp we need to consider is approximately
    tsmax = (100y * 365d * 24h * 3600s) * 1E6 = 3.1536E15
    tsmax requires 51.4859 bits < 53 bits
    tsmax requires 16 decimal digits
]]--

-- KEYS length shall be 1
local numkeys = #KEYS
if (numkeys ~= 1) then
  return redis.error_reply("Invalid Key Number")
end

-- read sliding window key
local slwkey = KEYS[1]

-- ARGV length shall be an even number larger than 4
local numargs = #ARGV
if ((numargs % 2) ~= 0) or (numargs < 4) then
  return redis.error_reply("Invalid Args Number")
end

-- read at_usec parameter
-- at_usec normally is current redis time converted to usec
-- script allows passing at_usec explicitly to ease testing
local at_usec = tonumber(ARGV[1])
if at_usec == 0 then
  local redis_time = redis.call("TIME")
  at_usec = redis_time[1] * 1e6 + redis_time[2]
end

-- read time to live in millisecond ms
local ttl_ms = tonumber(ARGV[2])
local ttl_usec = math.floor(ttl_ms * 1000)
if ttl_usec > at_usec then
  return redis.error_reply("Invalid ttl duration, can not be larger than at time!")
end

-- clamp the sliding windows
-- note that remstop is prefixed by '(' so that it is excluded from the range
local remstop = string.format("(%016d_000000", at_usec - ttl_usec)
redis.call('ZREMRANGEBYLEX', slwkey, '-', remstop)

-- check that the index contains less than 1E6 events
local zcard = redis.call('ZCARD', slwkey)
if zcard > 999999 then
  return redis.error_reply("Index is full, contains more than 1E6 events!")
end

-- check all sliding window conditions
-- script allows enforcing 1 or more condition
-- each sliding window condition is defined by 2 numbers slwsize slwlimit
-- slwsize is the size of the sliding window in ms
-- slwlimit is the maximum number of 'events'
local numcond = (numargs / 2) - 1
for i=1, numcond do
  local slwsize_usec = math.floor(tonumber(ARGV[2*i + 1]) * 1000)
  local slwlimit = tonumber(ARGV[2*i + 2])
  -- slwstart, slwend are prefixed with '[' so that redis interprets them as inclusive
  local slwstart = string.format("[%016d_000000", at_usec - slwsize_usec)
  local slwend = string.format("[%016d_999999", at_usec)
  local numevt = redis.call('ZLEXCOUNT', slwkey, slwstart, slwend)
  if numevt >= slwlimit then
    -- as in C we use non zero value to report error
    return i
  end
end

-- all sliding window checks were successful
-- hence we record a new event
-- Note that we append current index cardinality to the event
-- This is because many events can have the same microsecond timestamp
local evtkey = string.format("%016d_%06d", at_usec, zcard)
redis.call('ZADD', slwkey, 0, evtkey)

-- schedule key expiration
local ttl_sec = math.ceil(ttl_ms / 1000)
redis.call('EXPIRE', slwkey, ttl_sec)

-- 0 status means success
return 0
