# Modbus RTU Serial Timing Analyzer

Python tool that measures serial write timing against **Modbus RTU** rules (max inter-character gap **1.5T**).

## Modes

- **Single-byte stream** — sends many consecutive bytes and measures the interval between each `write()`.
- **Modbus frame batch** — sends repeated full RTU frames and records average microseconds per byte for each frame send.

Each run prints a short report and writes timestamped **CSV**, **PNG** (histogram), and **TXT** (stats) files in the working directory.

## Requirements

- Python 3.8+
- `pyserial`, `numpy`, `matplotlib`

```bash
pip install pyserial numpy matplotlib
```

## Configuration

Edit the constants at the top of `serial_timing_analyzer.py`:

- `PORT_SZEREGOWY` — serial port (default `COM5`)
- `PREDKOSC` — baud rate (default `115200`, 8E1)
- `LICZBA_BAJTOW` / `LICZBA_RAMEK` — sample counts

## Run

```bash
python serial_timing_analyzer.py
```

Both modes run one after the other.
