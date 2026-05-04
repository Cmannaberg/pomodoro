# Pomodoro Timer

A command-line Pomodoro timer written in Python to help you stay focused.

## Features

- ⏱ Configurable work session length (default **25 minutes**)
- ☕ Short breaks (default **5 minutes**) after each session
- 🛋 Long breaks (default **15 minutes**) after every 4 sessions
- 📊 Tracks and displays total completed sessions
- ⌨️ Press **Ctrl+C** at any point to exit gracefully

## Requirements

- Python 3.10 or later (no third-party packages required)

## Usage

```bash
# Start with default durations (25 / 5 / 15 minutes)
python pomodoro.py

# Customize durations
python pomodoro.py --work 50 --short-break 10 --long-break 30

# Change how many sessions before a long break
python pomodoro.py --sessions 2
```

### All options

| Flag | Default | Description |
|------|---------|-------------|
| `--work MINUTES` | 25 | Work session duration |
| `--short-break MINUTES` | 5 | Short break duration |
| `--long-break MINUTES` | 15 | Long break duration |
| `--sessions N` | 4 | Sessions before a long break |

## Running tests

```bash
python -m pytest tests/ -v
```
