"""
main.py
───────
OQD Quantum Explorer .


────────────────
* Initialise hardware (via device.py)
* Inject global CSS (from config.py)
* Render the top-level header and tab bar
* Delegate each tab's content to its dedicated module in tabs/
* Launch the NiceGUI server

Run
───
    python main.py
or (mock mode is set in config.py):
    MOCK=True python main.py
"""

from nicegui import ui

#  project modules 
from config import (
    APP_TITLE, APP_HOST, APP_PORT, APP_FAVICON,
    DARK_THEME_CSS,
)
from device import get_device, get_stream_ip
import tabs.learn           as tab_learn
import tabs.circuit_builder as tab_build
import tabs.challenge       as tab_challenge
import tabs.hardware        as tab_hardware



# APPLICATION
#

def main() -> None:
    """Build the full NiceGUI page."""

    # ── Hardware ──────────────────────────────────────────────────────────────
    device    = get_device()
    stream_ip = get_stream_ip()

    # ── Global CSS ────────────────────────────────────────────────────────────
    ui.add_head_html(DARK_THEME_CSS)

    # ── Header ────────────────────────────────────────────────────────────────
    with ui.row().classes("w-full items-center justify-between").style(
        "background:#0d0d22;border-bottom:1px solid #1e1e4a;padding:12px 24px;"
    ):
        with ui.column().style("gap:2px"):
            ui.label("OQD QUANTUM EXPLORER").classes("qheading").style("font-size:1.2rem")
            ui.label("Interactive Trapped-Ion Teaching Demo").classes("qsub")

        with ui.row().classes("items-center gap-4"):
            ui.label("SCORE").classes("qsub")
            # score_label is passed down to tabs that need to update it
            score_label = ui.label("0").classes("score-badge")

    ui.separator().style("margin:0;border-color:#0d0d22")

    # ── Tab bar ───────────────────────────────────────────────────────────────
    with ui.tabs().classes("w-full").style("background:#0d0d22") as tabs:
        t_learn     = ui.tab("⚛  LEARN")
        t_build     = ui.tab("⚙  CIRCUIT BUILDER")
        t_challenge = ui.tab("🎯  CHALLENGE")
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

        with ui.tab_panel(t_hardware):
            tab_hardware.build(device=device, stream_ip=stream_ip)



# ENTRY POINT


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
