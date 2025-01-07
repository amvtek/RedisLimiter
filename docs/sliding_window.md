# Sliding Window Rate Limiter

This command reads and updates a redis `sorted set` used as a `sliding window` index.
It checks that 1 or more `sliding window` counters are below limits.
If all `sliding window` conditions are fullfilled, it records a new timestamped event
in the `sliding window` index...

```bash
$cmd 1 KEY SLW_SIZE_ms SLW_LIMIT [SLW_SIZE_ms SLW_LIMIT]* [EXTRA_TTL_ms] 
```

The `$cmd` string depends if the command is evaluated as a script or a function. See
details afterwards.

The command returns `0` in case of SUCCESS *(no sliding window limit was exceeded)*
otherwise it returns the index of the first failing sliding window *(1 based index)*.

## Parameters

```
KEY: string
    references the sorted set used as index.

SLW_SIZE_ms: int
    sliding window size in milliseconds.

SLW_LIMIT: int
    maximum number of events in sliding window.

EXTRA_TTL_ms: int
    sorted set time to live default to first SLW_SIZE_ms
    if this parameter is set, sorted set time to live is (first SLW_SIZE_ms + EXTRA_TTL_ms).
```

## Burst control

Multiple sliding window maybe defined to control bursts.

For example an API may allow 100 requests per hour, but additionally set a limit that no
more than 10 requests per minute may be received...

When multiple sliding windows are used, the first shall be the one that has the largest
`SLW_SIZE_ms`.

## Script command invocation

The [sliding_window.lua][0] script shall first be loaded to the server.

This is achieved using the redis [SCRIPT LOAD][10] command passing it the content of the
file [sliding_window.lua][0] which returns the script identifier `script_id`.

You then call the command using the [EVALSHA][11] command passing it the `script_id`
parameter.

```bash
EVALSHA $script_id 1 KEY SLW_SIZE_ms SLW_LIMIT [SLW_SIZE_ms SLW_LIMIT]* [EXTRA_TTL_ms]
```
Note that many redis client libraries are able to deploy LUA scripts to the server and
expose them as custom commands. This is probably the simplest way to integrate
[sliding_window.lua][0] to your project.

## Function command invocation

The [redis_limiter_funcs.lua][1] module shall first be deployed to the server.

This is achieved using the redis [FUNCTION LOAD REPLACE][12] passing it the content of
the module [redis_limiter_funcs.lua][1].

You then call the command using the [FCALL][13] command passing it `sliding_window` as
function name.

```bash
FCALL sliding_window 1 KEY SLW_SIZE_ms SLW_LIMIT [SLW_SIZE_ms SLW_LIMIT]* [EXTRA_TTL_ms]
```

## Performance considerations

It is important to limit the size of the `sorted set` used to record events. As a rule
of thumb you should adjust main `SLW_SIZE_ms` parameter so that the maximum number of
events in the sorted set is below 500.

For example, if you are required to enforce a limit of 10000 request per minute instead
to define your sliding window as `60000 10000` you can set it to `3000 500`...

You can edit and use the provided [benchmark][2] script to evaluate your sliding window
performance. To run the benchmark script using docker, in a bash terminal do:

```bash
$> docker compose run --rm devterm bash
$> ./tools/benchmark sliding_window_script
```

[0]: ../src/sliding_window.lua
[1]: ../src/redis_limiter_funcs.lua
[2]: ../tools/benchmark
[10]: https://redict.io/docs/commands/script-load
[11]: https://redict.io/docs/commands/evalsha
[12]: https://redict.io/docs/commands/function-load
[13]: https://redict.io/docs/commands/fcall
