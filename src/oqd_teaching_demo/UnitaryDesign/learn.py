"""
tabs/learn.py
─────────────
"Learn" tab  concept cards, live Bloch sphere, quick-gate panel,
probability bars, and laser-status dots.

Public API
──────────
build(device, score_label) -> None
    Renders the full Learn tab contents into the current NiceGUI context.
"""

from __future__ import annotations
import asyncio

from nicegui import ui

import state
import quantum as q
from config import CONCEPT_CARDS, QUICK_GATES
from widgets.bloch import bloch_sphere_svg
from widgets.gate_buttons import quick_gate_row, danger_button, action_button


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _small_btn(label: str, on_click, color="var(--bg2)", text_color="var(--text-dim)", border=True):
    border_style = "border:1px solid var(--border)!important;" if border else "border:none!important;"
    return ui.button(label, on_click=on_click).style(
        f"font-family:var(--font-head)!important;font-size:0.65rem!important;"
        f"background:{color}!important;color:{text_color}!important;"
        f"{border_style}border-radius:6px!important;"
        f"padding:6px 12px!important;min-height:unset!important"
    )


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build(device, score_label) -> None:
    """Render the Learn tab into the current NiceGUI layout context."""

    # ── References to mutable UI elements ────────────────────────────────────
    bloch_html:   ui.html  | None = None
    bloch_build:  ui.html  | None = None
    prob0_bar:    ui.element | None = None
    prob1_bar:    ui.element | None = None
    prob0_pct:    ui.label | None = None
    prob1_pct:    ui.label | None = None
    state_label:  ui.label | None = None
    laser_dots: dict[int, ui.element] = {}

    # ── Internal update helpers ───────────────────────────────────────────────

    def _update_state_display():
        p0 = q.prob_zero(state.qubit.theta)
        p1 = q.prob_one(state.qubit.theta)

        bloch_html.set_content(bloch_sphere_svg(state.qubit.theta, state.qubit.phi))
        prob0_bar.style(f"width:{p0*100:.0f}%")
        prob1_bar.style(f"width:{p1*100:.0f}%")
        prob0_pct.set_text(f"{p0*100:.0f}%")
        prob1_pct.set_text(f"{p1*100:.0f}%")
        state_label.set_text(q.state_label(state.qubit.theta, state.qubit.phi))

    def _update_laser_dots(intensities: list[float]):
        for i, v in enumerate(intensities):
            if i in laser_dots:
                if v > 0.3:
                    laser_dots[i].classes("laser-dot on", remove="laser-dot")
                else:
                    laser_dots[i].classes("laser-dot", remove="laser-dot on")

    async def _laser_off_after(delay: float = 0.6):
        await asyncio.sleep(delay)
        for i in range(4):
            device.red_lasers.set_intensity(idx=i, intensity=0.0)
        _update_laser_dots([0, 0, 0, 0])

    # ── Gate handlers ─────────────────────────────────────────────────────────

    def apply_gate(gate: str):
        t, p = q.apply_gate(gate, state.qubit.theta, state.qubit.phi)
        state.qubit.set(t, p)
        intensities = q.laser_intensities_for_gate(gate)
        for i, v in enumerate(intensities):
            device.red_lasers.set_intensity(idx=i, intensity=v)
        device.trap.mode(q.trap_motion_for_gate(gate))
        _update_laser_dots(intensities)
        _update_state_display()
        asyncio.ensure_future(_laser_off_after(0.6))

    def reset_qubit():
        state.qubit.reset()
        _update_state_display()

    def measure_qubit():
        t, p = q.apply_gate("M", state.qubit.theta, state.qubit.phi)
        state.qubit.set(t, p)
        for i in range(4):
            device.red_lasers.set_intensity(idx=i, intensity=1.0)
        _update_laser_dots([1, 1, 1, 1])
        _update_state_display()
        asyncio.ensure_future(_laser_off_after(0.4))

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────────────────────

    with ui.row().classes("w-full gap-6").style("align-items:flex-start"):

        # ── LEFT: concept cards ───────────────────────────────────────────────
        with ui.column().style("flex:1;min-width:280px;gap:16px"):
            ui.label("QUANTUM CONCEPTS").classes("qheading").style(
                "font-size:0.9rem;margin-bottom:8px"
            )

            for c in CONCEPT_CARDS:
                with ui.card().classes("qcard"):
                    with ui.row().classes("items-center gap-3 w-full"):
                        ui.label(c["icon"]).style(
                            "font-size:1.8rem;color:var(--accent);width:36px;text-align:center"
                        )
                        with ui.column().style("gap:2px;flex:1"):
                            ui.label(c["title"]).style(
                                "font-family:var(--font-head);color:var(--accent);"
                                "font-size:0.85rem;letter-spacing:0.08em"
                            )
                            with ui.row().style("gap:4px;flex-wrap:wrap"):
                                for pill in c["pills"]:
                                    ui.html(f'<span class="concept-pill">{pill}</span>')
                    ui.separator().style("border-color:var(--border);margin:10px 0")
                    ui.label(c["body"]).style(
                        "font-family:var(--font-body);font-size:0.82rem;"
                        "color:var(--text);line-height:1.55;white-space:pre-line"
                    )

        # ── RIGHT: live state panel ───────────────────────────────────────────
        with ui.column().style("width:280px;gap:16px"):

            # Bloch sphere
            with ui.card().classes("qcard"):
                ui.label("BLOCH SPHERE").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                bloch_html = ui.html(
                    bloch_sphere_svg(state.qubit.theta, state.qubit.phi)
                ).style("display:block;margin:auto")

            # Probability + quick gates
            with ui.card().classes("qcard"):
                ui.label("QUBIT STATE").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )

                # |0⟩ bar
                with ui.row().classes("items-center w-full gap-2"):
                    ui.label("|0⟩").style(
                        "font-family:var(--font-mono);color:var(--accent);width:28px"
                    )
                    _bg0 = ui.element("div").classes("prob-bar-bg").style("flex:1")
                    with _bg0:
                        prob0_bar = ui.element("div").classes("prob-bar-fill-0").style(
                            f"width:{q.prob_zero(state.qubit.theta)*100:.0f}%"
                        )
                    prob0_pct = ui.label(
                        f"{q.prob_zero(state.qubit.theta)*100:.0f}%"
                    ).style(
                        "font-family:var(--font-mono);font-size:0.8rem;"
                        "color:var(--accent);width:36px;text-align:right"
                    )

                # |1⟩ bar
                with ui.row().classes("items-center w-full gap-2").style("margin-top:6px"):
                    ui.label("|1⟩").style(
                        "font-family:var(--font-mono);color:var(--red);width:28px"
                    )
                    _bg1 = ui.element("div").classes("prob-bar-bg").style("flex:1")
                    with _bg1:
                        prob1_bar = ui.element("div").classes("prob-bar-fill-1").style(
                            f"width:{q.prob_one(state.qubit.theta)*100:.0f}%"
                        )
                    prob1_pct = ui.label(
                        f"{q.prob_one(state.qubit.theta)*100:.0f}%"
                    ).style(
                        "font-family:var(--font-mono);font-size:0.8rem;"
                        "color:var(--red);width:36px;text-align:right"
                    )

                ui.separator().style("border-color:var(--border);margin:10px 0")

                state_label = ui.label(
                    q.state_label(state.qubit.theta, state.qubit.phi)
                ).style(
                    "font-family:var(--font-mono);color:var(--green);"
                    "font-size:1rem;text-align:center;width:100%"
                )

                ui.separator().style("border-color:var(--border);margin:10px 0")
                ui.label("QUICK GATES").style(
                    "font-family:var(--font-mono);font-size:0.7rem;color:var(--text-dim)"
                )
                quick_gate_row(on_gate=apply_gate, gates=QUICK_GATES)

                with ui.row().style("gap:6px;margin-top:8px;flex-wrap:wrap"):
                    _small_btn("RESET", reset_qubit)
                    _small_btn(
                        "MEASURE", measure_qubit,
                        color="var(--red)", text_color="#fff", border=False
                    )

            # Laser status
            with ui.card().classes("qcard"):
                ui.label("LASER STATUS").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                with ui.row().classes("gap-3 items-center"):
                    for i in range(4):
                        with ui.column().classes("items-center").style("gap:4px"):
                            laser_dots[i] = ui.element("div").classes("laser-dot")
                            ui.label(f"L{i+1}").style(
                                "font-family:var(--font-mono);font-size:0.65rem;"
                                "color:var(--text-dim)"
                            )
