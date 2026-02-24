"""
config.py
─────────
All application-level constants, hardware settings, gate mappings,
challenge definitions, and CSS theme. Nothing here has side-effects —
import freely from any other module.
"""

import math

# ─────────────────────────────────────────────────────────────────────────────
# HARDWARE
# ─────────────────────────────────────────────────────────────────────────────

# Set to False on a real Raspberry Pi to use actual hardware
MOCK: bool = True

STREAM_IP_MOCK = "docs/img/bloodstone.jpg"  # matches original OQD main.py fallback
STREAM_IP_REAL = "http://127.0.0.1:5000/stream"

NUM_LASER_CHANNELS = 4

# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

APP_TITLE   = "OQD Quantum Explorer"
APP_HOST    = "0.0.0.0"
APP_PORT    = 8080
APP_FAVICON = "⚛"

# ─────────────────────────────────────────────────────────────────────────────
# GATE → HARDWARE MAPPINGS
# ─────────────────────────────────────────────────────────────────────────────

#: Laser intensity pattern (4 channels) for each gate
GATE_LASER_PATTERNS: dict[str, list[float]] = {
    "H": [1.0, 0.0, 1.0, 0.0],
    "X": [1.0, 1.0, 0.0, 0.0],
    "Y": [0.0, 1.0, 1.0, 0.0],
    "Z": [0.0, 0.0, 1.0, 1.0],
    "S": [1.0, 0.0, 0.0, 1.0],
    "T": [0.5, 0.0, 0.0, 0.5],
    "M": [1.0, 1.0, 1.0, 1.0],
}
DEFAULT_LASER_PATTERN: list[float] = [0.5, 0.5, 0.5, 0.5]

#: Trap motion command for each gate
GATE_TRAP_MOTION: dict[str, str] = {
    "H": "stop",
    "X": "left",
    "Y": "right",
    "Z": "stop",
    "S": "left",
    "T": "right",
    "M": "stop",
}
DEFAULT_TRAP_MOTION = "stop"

# ─────────────────────────────────────────────────────────────────────────────
# GATE METADATA  (used in the circuit builder palette)
# ─────────────────────────────────────────────────────────────────────────────

GATE_INFO: dict[str, tuple[str, str]] = {
    "H": ("Hadamard",  "Creates superposition"),
    "X": ("Pauli-X",   "Bit flip (NOT gate)"),
    "Y": ("Pauli-Y",   "Bit+phase flip"),
    "Z": ("Pauli-Z",   "Phase flip"),
    "S": ("S gate",    "π/2 phase shift"),
    "T": ("T gate",    "π/4 phase shift"),
    "M": ("Measure",   "Collapse + readout"),
}

# Gates available in the quick-gate panel (no measurement)
QUICK_GATES = ["H", "X", "Y", "Z", "S", "T"]

# ─────────────────────────────────────────────────────────────────────────────
# CONCEPT CARDS  (Learn tab)
# ─────────────────────────────────────────────────────────────────────────────

CONCEPT_CARDS = [
    {
        "title": "Qubits & States",
        "icon": "◉",
        "pills": ["|0⟩", "|1⟩", "superposition"],
        "body": (
            "A qubit is the quantum analogue of a classical bit. "
            "Unlike a bit (0 or 1), a qubit can exist in a superposition "
            "of both states simultaneously: |ψ⟩ = α|0⟩ + β|1⟩.\n\n"
            "In our demo, the levitated polystyrene balls represent ions "
            "trapped by electromagnetic fields. Each ion is a qubit! "
            "The red lasers drive quantum gate operations on those ions."
        ),
    },
    {
        "title": "Superposition",
        "icon": "≋",
        "pills": ["H gate", "probability", "50/50"],
        "body": (
            "Applying a Hadamard (H) gate puts a qubit into an equal "
            "superposition: |+⟩ = (|0⟩ + |1⟩)/√2.\n\n"
            "On the Bloch sphere this moves the state from the north pole "
            "to the equator. In the demo, lasers 1 & 3 fire to implement "
            "this rotation. Measurement will randomly give 0 or 1 with "
            "equal 50% probability."
        ),
    },
    {
        "title": "Measurement & Collapse",
        "icon": "📡",
        "pills": ["collapse", "Born rule", "outcome"],
        "body": (
            "Measuring a qubit in superposition causes wave-function "
            "collapse. The probability of measuring |0⟩ is |α|², |1⟩ is |β|².\n\n"
            "In our demo the camera captures the ball positions after "
            "measurement – analogous to reading out ion fluorescence in "
            "a real trapped-ion computer."
        ),
    },
    {
        "title": "Quantum Gates",
        "icon": "⊕",
        "pills": ["X", "Y", "Z", "H", "S", "T"],
        "body": (
            "Quantum gates are unitary operations represented by matrices. "
            "Pauli-X flips |0⟩↔|1⟩ (quantum NOT). Z adds a phase flip. "
            "H creates superposition. S/T add fractional phases.\n\n"
            "Each gate fires a specific laser pattern on our demo hardware, "
            "and may move the ion trap left/right to modulate coupling."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# CHALLENGES
# ─────────────────────────────────────────────────────────────────────────────

CHALLENGES: list[dict] = [
    {
        "title":        "CHALLENGE 1: THE FLIP",
        "difficulty":   "★☆☆ BEGINNER",
        "desc":         "Start from the ground state |0⟩ and flip the qubit to the excited state |1⟩.",
        "target_theta": math.pi,
        "target_phi":   0.0,
        "target_label": "|1⟩",
        "points":       100,
    },
    {
        "title":        "CHALLENGE 2: SUPERPOSITION",
        "difficulty":   "★★☆ INTERMEDIATE",
        "desc":         "Create a perfect superposition state |+⟩ = (|0⟩+|1⟩)/√2. You start from |0⟩.",
        "target_theta": math.pi / 2,
        "target_phi":   0.0,
        "target_label": "|+⟩",
        "points":       150,
    },
    {
        "title":        "CHALLENGE 3: PHASE SHIFT",
        "difficulty":   "★★☆ INTERMEDIATE",
        "desc":         "Apply a Hadamard then a Z gate to create the |−⟩ state. H then Z.",
        "target_theta": math.pi / 2,
        "target_phi":   math.pi,
        "target_label": "|−⟩",
        "points":       200,
    },
    {
        "title":        "CHALLENGE 4: RETURN",
        "difficulty":   "★★★ ADVANCED",
        "desc":         "Start at |0⟩, apply H to get |+⟩, then apply H again to return to |0⟩.",
        "target_theta": 0.0,
        "target_phi":   0.0,
        "target_label": "|0⟩",
        "points":       250,
    },
]

# Tolerance (radians) when checking whether the qubit matches the target
CHALLENGE_TOLERANCE = 0.2

# ─────────────────────────────────────────────────────────────────────────────
# CSS THEME
# ─────────────────────────────────────────────────────────────────────────────

DARK_THEME_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=DM+Sans:wght@300;400;600&display=swap');

  :root {
    --bg:        #06060f;
    --bg2:       #0d0d22;
    --panel:     #10102a;
    --border:    #1e1e4a;
    --accent:    #00e5ff;
    --accent2:   #7b2fff;
    --green:     #00ff88;
    --red:       #ff3860;
    --yellow:    #ffd700;
    --text:      #c8d6f0;
    --text-dim:  #5a6a8a;
    --font-mono: 'Share Tech Mono', monospace;
    --font-head: 'Orbitron', sans-serif;
    --font-body: 'DM Sans', sans-serif;
  }

  body, .q-page, .nicegui-content {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
  }

  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--bg2); }
  ::-webkit-scrollbar-thumb { background: var(--accent2); border-radius: 3px; }

  .qcard {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }
  .qcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent2), var(--accent), var(--green));
  }

  .qheading {
    font-family: var(--font-head) !important;
    color: var(--accent) !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .qsub {
    font-family: var(--font-mono) !important;
    color: var(--text-dim);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
  }

  .gate-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px; height: 56px;
    border-radius: 10px;
    font-family: var(--font-mono) !important;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    border: 1px solid var(--border);
    background: var(--bg2);
    color: var(--accent);
    transition: all 0.15s ease;
    user-select: none;
    margin: 4px;
  }
  .gate-btn:hover {
    background: var(--accent2);
    color: #fff;
    border-color: var(--accent2);
    box-shadow: 0 0 18px rgba(123,47,255,0.6);
    transform: translateY(-2px);
  }
  .gate-btn.active {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
    box-shadow: 0 0 22px rgba(0,229,255,0.7);
  }

  .circuit-wire {
    background: var(--bg2);
    border: 1px dashed var(--border);
    border-radius: 8px;
    min-height: 72px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    position: relative;
  }
  .circuit-wire::before {
    content: '|ψ⟩';
    font-family: var(--font-mono);
    color: var(--green);
    font-size: 0.9rem;
    margin-right: 8px;
  }
  .circuit-gate-chip {
    background: var(--accent2);
    color: #fff;
    font-family: var(--font-mono);
    font-weight: 700;
    font-size: 0.85rem;
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
  }
  .circuit-gate-chip:hover::after {
    content: '✕';
    position: absolute;
    top: -6px; right: -6px;
    background: var(--red);
    border-radius: 50%;
    width: 16px; height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    line-height: 16px;
    text-align: center;
  }

  .prob-bar-bg {
    background: var(--bg2);
    border-radius: 4px;
    height: 20px;
    overflow: hidden;
    border: 1px solid var(--border);
  }
  .prob-bar-fill-0 {
    height: 100%;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    border-radius: 4px;
    transition: width 0.4s cubic-bezier(.4,0,.2,1);
  }
  .prob-bar-fill-1 {
    height: 100%;
    background: linear-gradient(90deg, var(--red), var(--yellow));
    border-radius: 4px;
    transition: width 0.4s cubic-bezier(.4,0,.2,1);
  }

  .tut-active {
    border-color: var(--green) !important;
    box-shadow: 0 0 20px rgba(0,255,136,0.2);
  }

  .score-badge {
    font-family: var(--font-head);
    color: var(--yellow);
    font-size: 1.4rem;
    letter-spacing: 0.05em;
  }

  .laser-dot {
    width: 14px; height: 14px;
    border-radius: 50%;
    background: var(--text-dim);
    transition: background 0.3s, box-shadow 0.3s;
    display: inline-block;
    margin: 2px;
  }
  .laser-dot.on {
    background: #ff2222;
    box-shadow: 0 0 14px rgba(255,34,34,0.9);
  }

  .concept-pill {
    display: inline-block;
    background: rgba(0,229,255,0.08);
    border: 1px solid rgba(0,229,255,0.2);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
  }

  @keyframes flash-green { 0%,100% {opacity:1} 50% {opacity:0.3} }
  .flash { animation: flash-green 0.6s ease 2; }

  .qdivider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 16px 0;
  }
</style>
"""
