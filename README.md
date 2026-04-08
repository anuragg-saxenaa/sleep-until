# sleep-until

Sleep until a specific wall-clock time, then exit. No more manually calculating seconds.

## Install

```bash
pip install .
# or just chmod +x sleep_until.py and put it in PATH
```

## Usage

```bash
sleep_until <time spec>
```

### Supported formats

| Format | Example | Meaning |
|--------|---------|---------|
| `HH:MM` | `sleep_until 03:00` | Today at 3am (or tomorrow if past) |
| `HH:MM:SS` | `sleep_until 14:30:00` | Today at 14:30 |
| `+Ns` | `sleep_until +300s` | Sleep N seconds (relative) |
| `+Nm` | `sleep_until +5m` | Sleep N minutes |
| `+Nh` | `sleep_until +1h` | Sleep N hours |
| `YYYY-MM-DD HH:MM:SS` | `sleep_until 2026-04-09 09:00:00` | Absolute datetime |
| `YYYY-MM-DDTHH:MM:SS` | `sleep_until 2026-04-09T09:00:00` | ISO 8601 format |

### Options

- `--verbose` — show target time and a live countdown every second
- `-h, --help` — show help

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Completed normally |
| 1 | Interrupted (Ctrl+C) |
| 2 | Invalid time specification |

### Examples

```bash
# Sleep until 3am today (or tomorrow if it's already past 3am)
sleep_until 03:00

# Sleep for 5 minutes
sleep_until +5m

# Sleep until a specific datetime
sleep_until 2026-04-09T09:00:00

# Verbose countdown
sleep_until +60s --verbose
```

## License

MIT
