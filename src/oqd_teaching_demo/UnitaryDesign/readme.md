# OQD Quantum Explorer

Interactive trapped-ion quantum computing teaching demo built on NiceGUI.

## Project Structure

```
oqd_explorer/
│
├── main.py                  # Entry point — wires all modules together & starts server
├── config.py                # All constants: hardware flags, gate maps, CSS theme, challenges
├── device.py                # Hardware abstraction (real Device / MockDevice / StubDevice)
├── state.py                 # Shared mutable state: QubitState, CircuitState, ScoreState
├── quantum.py               # Pure quantum math: gate logic, probabilities, state labels
│
├── widgets/
│   ├── __init__.py
│   ├── bloch.py             # Bloch sphere SVG renderer
│   └── gate_buttons.py      # Reusable gate button rows and palette components
│
└── tabs/
    ├── __init__.py
    ├── learn.py             # "Learn" tab — concept cards, Bloch sphere, quick gates
    ├── circuit_builder.py   # "Circuit Builder" tab — gate palette, wire, run on hardware
    ├── challenge.py         # "Challenge" tab — target states, scoring, gate input
    └── hardware.py          # "Hardware" tab — direct laser sliders, trap, camera feed
```

## Module Responsibilities

| Module | Role |
|--------|------|
| `config.py` | Single source of truth for every constant. No side-effects. |
| `device.py` | Returns the right device object based on `MOCK` flag in config. |
| `state.py` | Singleton dataclasses for qubit state, circuit queue, and score. |
| `quantum.py` | Stateless gate math — `apply_gate`, `prob_zero`, `state_label`, etc. |
| `widgets/bloch.py` | SVG Bloch sphere — pure function, no NiceGUI dependency. |
| `widgets/gate_buttons.py` | Reusable NiceGUI button components for gate selection. |
| `tabs/learn.py` | Learn tab UI + handlers (reads/writes `state.qubit`). |
| `tabs/circuit_builder.py` | Builder tab UI + async hardware execution loop. |
| `tabs/challenge.py` | Challenge tab UI + challenge loading, scoring, validation. |
| `tabs/hardware.py` | Hardware tab UI — direct laser/trap control. |
| `main.py` | Composes all tabs, injects CSS, runs `ui.run()`. |

## Running

```bash
# Install dependencies
pip install nicegui

# Mock mode (no hardware required) — set MOCK = True in config.py
python main.py

# Real hardware (Raspberry Pi)
# Set MOCK = False in config.py, then:
python main.py
```

## Configuration

All settings live in `config.py`:

- `MOCK` — toggle between real hardware and stub device
- `GATE_LASER_PATTERNS` — map gate names to 4-channel laser intensities
- `GATE_TRAP_MOTION` — map gate names to trap motion commands
- `CHALLENGES` — list of challenge dicts (add your own here)
- `DARK_THEME_CSS` — full CSS theme string injected into the page head
