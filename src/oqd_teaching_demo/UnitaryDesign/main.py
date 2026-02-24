"""
main.py
───────
OQD Quantum Explorer. 


────────────────
* Initialise hardware via device.py  (Board singleton + atexit cleanup)
* Inject global CSS from config.py
* Render the top-level header and tab bar
* Delegate each tab's content to its module in tabs/
* Expose the original OQD program dialogs (Digital / Analog) as an extra tab
* Launch the NiceGUI server

Run
───
    python main.py

MOCK flag lives in config.py — set MOCK = False on a real Raspberry Pi.
"""

import logging
import atexit

from nicegui import ui

from config import (
    APP_TITLE, APP_HOST, APP_PORT, APP_FAVICON,
    DARK_THEME_CSS,
)
from device import get_board, get_stream_ip
from programs import digital_shor, digital_random, analog_ising, analog_all_to_all

import tabs.learn           as tab_learn
import tabs.circuit_builder as tab_build
import tabs.challenge       as tab_challenge
import tabs.hardware        as tab_hardware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# OQD PROGRAM DIALOGS  (mirror the original main.py control/digital/analog cards)
# ─────────────────────────────────────────────────────────────────────────────

def _build_programs_tab(board, stream_ip: str) -> None:
    """Render the Programs tab — mirrors digital_card + analog_card from OQD main.py."""

    with ui.row().classes("w-full gap-6").style("align-items:flex-start"):

        # ── Digital programs ──────────────────────────────────────────────────
        with ui.column().style("flex:1;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("DIGITAL PROGRAMS").classes("qheading").style("font-size:0.9rem")
                ui.label(
                    "Run pre-compiled quantum circuit programs on the hardware. "
                    "Each button fires a laser sequence mapped from the corresponding algorithm."
                ).style(
                    "font-family:var(--font-body);font-size:0.82rem;"
                    "color:var(--text-dim);margin-top:4px;margin-bottom:14px"
                )

                def _run(program_fn):
                    prog = program_fn()
                    logger.info("Running program: %s  steps=%d", program_fn.__name__,
                                len(prog.red_lasers_intensity))
                    board.device.run(prog)

                _BTN = (
                    "font-family:var(--font-head)!important;font-size:0.78rem!important;"
                    "border-radius:8px!important;padding:10px 20px!important;"
                    "min-height:unset!important;letter-spacing:0.05em!important;"
                )

                with ui.row().style("gap:10px;flex-wrap:wrap"):
                    ui.button(
                        "⚛  SHOR'S ALGORITHM",
                        on_click=lambda: _run(digital_shor)
                    ).style(
                        _BTN +
                        "background:linear-gradient(135deg,var(--accent2),var(--accent))!important;"
                        "color:var(--bg)!important;border:none!important;font-weight:700!important"
                    )
                    ui.button(
                        "🎲  RANDOM CIRCUIT",
                        on_click=lambda: _run(digital_random)
                    ).style(
                        _BTN +
                        "background:var(--bg2)!important;color:var(--accent)!important;"
                        "border:1px solid var(--border)!important"
                    )

            # Analog programs
            with ui.card().classes("qcard"):
                ui.label("ANALOG PROGRAMS").classes("qheading").style("font-size:0.9rem")
                ui.label(
                    "Continuous-wave laser patterns that simulate analog Hamiltonian dynamics. "
                    "Channels are driven with sinusoidal envelopes to model spin-spin interactions."
                ).style(
                    "font-family:var(--font-body);font-size:0.82rem;"
                    "color:var(--text-dim);margin-top:4px;margin-bottom:14px"
                )

                with ui.row().style("gap:10px;flex-wrap:wrap"):
                    ui.button(
                        "🔗  NEAREST-NEIGHBOUR ISING",
                        on_click=lambda: _run(analog_ising)
                    ).style(
                        _BTN +
                        "background:linear-gradient(135deg,var(--red),var(--yellow))!important;"
                        "color:var(--bg)!important;border:none!important;font-weight:700!important"
                    )
                    ui.button(
                        "🌐  ALL-TO-ALL INTERACTIONS",
                        on_click=lambda: _run(analog_all_to_all)
                    ).style(
                        _BTN +
                        "background:var(--bg2)!important;color:var(--yellow)!important;"
                        "border:1px solid var(--border)!important"
                    )

                ui.separator().style("border-color:var(--border);margin:14px 0")
                ui.button(
                    "⏹  STOP PROGRAM",
                    on_click=lambda: (
                        board.device.stop() if hasattr(board.device, "stop")
                        else None
                    )
                ).style(
                    _BTN +
                    "background:var(--red)!important;color:#fff!important;"
                    "border:none!important;font-weight:700!important"
                )

        # ── Camera feed ───────────────────────────────────────────────────────
        with ui.column().style("width:320px;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("CAMERA FEED").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                ui.image(stream_ip).style(
                    "width:100%;border-radius:6px;border:1px solid var(--border)"
                )

            with ui.card().classes("qcard"):
                ui.label("PROGRAM MAPPING").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                ui.html("""
                <div style="font-family:var(--font-mono);font-size:0.72rem;
                            color:var(--text-dim);line-height:1.7">
                  <div style="color:var(--accent);margin-bottom:4px">DIGITAL</div>
                  Each step = 1 gate → binary laser pattern (0 or 1)<br>
                  dt = 0.25 s/step &nbsp;|&nbsp; camera on final step
                  <hr style="border-color:var(--border);margin:8px 0">
                  <div style="color:var(--yellow);margin-bottom:4px">ANALOG</div>
                  Each step = sinusoidal laser intensity (0.0–1.0)<br>
                  Ising: pairs offset by π/2 &nbsp;|&nbsp; All-to-all: in-phase<br>
                  dt = 0.1 s/step &nbsp;|&nbsp; 60 steps total
                </div>
                """)


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Build the full NiceGUI page."""

    # ── Hardware (Board singleton + atexit) ───────────────────────────────────
    board     = get_board()          # atexit.register(board.cleanup) called inside
    stream_ip = get_stream_ip()
    device    = board.device

    logger.info("main(): board=%r  stream_ip=%s", board, stream_ip)

    # ── Global CSS ────────────────────────────────────────────────────────────
    ui.add_head_html(DARK_THEME_CSS)

    # ── Header ────────────────────────────────────────────────────────────────
    with ui.row().classes("w-full items-center justify-between").style(
        "background:#0d0d22;border-bottom:1px solid #1e1e4a;padding:12px 24px;"
    ):
        with ui.row().classes("items-center gap-3"):
            ui.image(
                "https://github.com/OpenQuantumDesign/equilux/blob/"
                "9ed0c5380133e7d135121c44c3f4cdbcb8cf781b/docs/img/oqd-logo.png?raw=true"
            ).style("width:36px;height:36px;border-radius:4px")
            with ui.column().style("gap:2px"):
                ui.label("OQD QUANTUM EXPLORER").classes("qheading").style("font-size:1.2rem")
                ui.label("Interactive Trapped-Ion Teaching Demo").classes("qsub")

        with ui.row().classes("items-center gap-4"):
            ui.label("SCORE").classes("qsub")
            score_label = ui.label("0").classes("score-badge")

    ui.separator().style("margin:0;border-color:#0d0d22")

    # ── Tab bar ───────────────────────────────────────────────────────────────
    with ui.tabs().classes("w-full").style("background:#0d0d22") as tabs:
        t_learn     = ui.tab("⚛  LEARN")
        t_build     = ui.tab("⚙  CIRCUIT BUILDER")
        t_challenge = ui.tab("🎯  CHALLENGE")
        t_programs  = ui.tab("▶  PROGRAMS")      # ← OQD digital/analog programs
        t_hardware  = ui.tab("🔧  HARDWARE")

    # ── Tab panels ────────────────────────────────────────────────────────────
    with ui.tab_panels(tabs, value=t_learn).classes("w-full").style(
        "background:var(--bg);padding:24px"
    ):
        with ui.tab_panel(t_learn):
            tab_learn.build(device=device, score_label=score_label)

        with ui.tab_panel(t_build):
            tab_build.build(device=device, stream_ip=stream_ip)

        with ui.tab_panel(t_challenge):
            tab_challenge.build(device=device, score_label=score_label)

        with ui.tab_panel(t_programs):
            _build_programs_tab(board=board, stream_ip=stream_ip)

        with ui.tab_panel(t_hardware):
            tab_hardware.build(device=device, stream_ip=stream_ip)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ in {"__main__", "__mp_main__"}:
    main()
    ui.run(
        title=APP_TITLE,
        host=APP_HOST,
        port=APP_PORT,
        reload=False,
        favicon=APP_FAVICON,
        dark=True,
    )
