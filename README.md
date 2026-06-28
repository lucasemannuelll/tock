# Time Tracker

A minimal command-line time tracking tool written in Rust.

## Features

- Start a session with tags and notes
- Stop the current session
- View a summary of today's sessions
- Persistent storage in CSV format

## Installation

```bash
cargo build --release
```

The binary will be available at `target/release/time-tracker`.

## Usage

### Start a session
```bash
start <tags> <note>
```
Example:
```bash
start coding "Working on project"
```

### Stop the current session
```bash
stop
```

### View today's summary
The summary is automatically displayed when you exit the program with `Ctrl+C`.

## Data Storage

Sessions are stored in `~/time-track.csv` with the following fields:
- Start timestamp (Unix epoch)
- End timestamp (Unix epoch)  
- Duration (seconds)
- Tags (comma-separated values, stored with `|` separators)
- Notes

## Example Workflow

```bash
$ start coding "Implementing feature X"
Sessão iniciada

$ start dev "New task"
Sessão já em andamento
Use stop antes de iniciar outra

$ stop
Sessão finalizada

$ start reading "Documentation review"
Sessão iniciada

$ ^C
Encerrando...

=== Resumo de Hoje ===

Total registrado: 1h 23min

coding
  45min

reading
  38min

Ultima sessão
reading | Documentation review
38min 0s
```

## File Format

The CSV file uses the following format:
```
start,end,duration_secs,tags,notes
1700000000,1700003600,3600,"coding,rust","Initial implementation"
```

## Keyboard Shortcuts

- `Ctrl+C` - Stop the program and show summary
- `Enter` - Submit commands

## Command Reference

| Command | Description |
|---------|-------------|
| `start <tags> <note>` | Start a new session |
| `stop` | Stop the current session |
| `Ctrl+C` | Exit and show summary |
