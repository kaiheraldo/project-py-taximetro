# Technical decisions

This document explains the main technical decisions made in Phases 1 and 2 of the taximeter project, and why.

## How to run

```
python3 taximeter.py          # start the taximeter
python3 -m unittest -v        # run the automated tests
```

Only the Python standard library is used, so nothing has to be installed.

## Phase 1

**Time is measured with timestamps, not counters.** The program stores the moment of the last state change (`time.time()`) and, at each change, charges `elapsed seconds x rate` for the state that just ended. A loop that counts seconds would block the program while it waits for the driver's input. With timestamps the fare stays correct however long the driver takes to type.

**Fares are charged per state, at the moment of the change.** Before switching between "stopped" and "moving", the program charges the previous stretch at its own rate. That is why a trip with several changes is still calculated correctly.

**A trip is a dictionary.** It holds the current state, the time of the last change, the running total and the start time. This is enough for Phase 1 and 2. In Phase 3 it is a natural candidate to become a class.

**The main loop is separate from the logic.** Functions such as `update_fare`, `change_state` and `finish_trip` do the work, and `main()` only reads commands. This made the logic easy to test in Phase 2.

**Invalid input never crashes the program.** Unknown commands, commands without an active trip and attempts to exit during a trip print a message and are logged.

## Phase 2

**Logging with the `logging` module.** Every event (program start, trip start, state change, finish, invalid command) is written to `taximeter.log` with a timestamp and a level (INFO or WARNING). This helps diagnose problems after the fact. The log is listed in `.gitignore` because it is generated data.

**Trip history in a JSON file (`trips.json`).** Each finished trip is saved with its start time, end time and total, and the `history` command shows today's trips and their total. JSON was chosen because it is human-readable, built into Python, and easy to move to a database in Phase 4. If the file is missing or corrupted, the program starts with an empty history and logs an error instead of crashing. The file is in `.gitignore` because it holds user data.

**Fares in a config file (`config.json`).** The rates are no longer written in the code, so the client can change prices by editing one file, without touching the program. If the file is missing, invalid or contains negative rates, the program falls back to default rates and logs the problem, so a bad configuration never stops the taximeter from working.

**Automated tests with `unittest`.** There are 13 tests covering fare calculation (including a trip with state changes), config loading (valid, missing, broken and negative-rate files) and history (saving, loading and corrupted files). The clock is replaced with a fake one during the tests, so they run instantly and give the same result every time. Tests that use files work in a temporary folder, so they never touch the real data.

## Workflow

- Each feature was developed on its own branch and merged into `main` through a pull request.
- Commit messages follow the convention `feat:`, `test:`, `chore:` and `docs:`.
- Progress is tracked on the GitHub Projects Kanban board, with one column per phase.