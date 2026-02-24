"""
tabs/circuit_builder.py
───────────────────────
"Circuit Builder" tab — gate palette, circuit wire, run/clear controls,
step-by-step hardware execution, and a live Bloch sphere.

Public API
──────────
build(device, stream_ip) -> None
"""

from __future__ import annotations
import asyncio

from nicegui import ui

import state
import quantum as q
from widgets.bloch import bloch_sphere_svg
from widgets.gate_buttons import gate_palette


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build(device, stream_ip: str) -> None:
    """Render the Circuit Builder tab into the current NiceGUI layout context."""

    # ── mutable UI element references ────────────────────────────────────────
    circuit_display: ui.element | None = None
    circuit_log:     ui.label   | None = None
    bloch_build_html: ui.html   | None = None

    # ── circuit wire renderer ─────────────────────────────────────────────────

    def render_circuit():
        circuit_display.clear()
        with circuit_display:
            if not state.circuit.gates:
                ui.label("← Add gates from the palette above").style(
                    "font-family:var(--font-mono);font-size:0.75rem;color:var(--text-dim)"
                )
                return
            for i, g in enumerate(state.circuit.gates):
                with ui.element("span").classes("circuit-gate-chip").on(
                    "click", lambda i=i: _remove_gate(i)
                ):
                    ui.label(g)

    # ── handlers ──────────────────────────────────────────────────────────────

    def _add_gate(gate: str):
        state.circuit.add(gate)
        render_circuit()

    def _remove_gate(idx: int):
        state.circuit.remove(idx)
        render_circuit()

    def _clear_circuit():
        state.circuit.clear()
        state.qubit.reset()
        render_circuit()
        circuit_log.set_text("")
        bloch_build_html.set_content(
            bloch_sphere_svg(state.qubit.theta, state.qubit.phi, 260)
        )

    async def _run_circuit():
        if not state.circuit.gates:
            circuit_log.set_text("⚠ No gates in circuit. Add gates and try again.")
            return

        state.qubit.reset()
        log_lines = ["Running circuit on hardware…", "Initial state: |0⟩"]
        circuit_log.set_text("\n".join(log_lines))

        for gate in state.circuit.gates:
            t, p = q.apply_gate(gate, state.qubit.theta, state.qubit.phi)
            state.qubit.set(t, p)

            intensities = q.laser_intensities_for_gate(gate)
            for i, v in enumerate(intensities):
                device.red_lasers.set_intensity(idx=i, intensity=v)
            device.trap.mode(q.trap_motion_for_gate(gate))

            bloch_build_html.set_content(
                bloch_sphere_svg(state.qubit.theta, state.qubit.phi, 260)
            )
            p0 = q.prob_zero(state.qubit.theta)
            log_lines.append(
                f"  ▶ Gate {gate}: P(|0⟩)={p0*100:.0f}%  P(|1⟩)={(1-p0)*100:.0f}%"
            )
            circuit_log.set_text("\n".join(log_lines))
            await asyncio.sleep(0.5)

        # Turn lasers off and stop trap
        for i in range(4):
            device.red_lasers.set_intensity(idx=i, intensity=0.0)
        device.trap.mode("stop")

        log_lines.append("✓ Circuit complete. Final state shown on Bloch sphere.")
        circuit_log.set_text("\n".join(log_lines))

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────────────────────

    with ui.row().classes("w-full gap-6").style("align-items:flex-start"):

        # ── LEFT: builder ─────────────────────────────────────────────────────
        with ui.column().style("flex:1;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("CIRCUIT BUILDER").classes("qheading").style("font-size:0.9rem")
                ui.label(
                    "Add gates to the circuit wire below, "
                    "then press RUN to execute on the hardware."
                ).style(
                    "font-family:var(--font-body);font-size:0.82rem;"
                    "color:var(--text-dim);margin-top:4px"
                )

                ui.separator().style("border-color:var(--border);margin:14px 0")

                ui.label("GATE PALETTE").style(
                    "font-family:var(--font-mono);font-size:0.7rem;"
                    "color:var(--text-dim);margin-bottom:8px"
                )
                gate_palette(on_gate=_add_gate)

                ui.label("CIRCUIT WIRE").style(
                    "font-family:var(--font-mono);font-size:0.7rem;"
                    "color:var(--text-dim);margin-bottom:6px"
                )
                circuit_display = ui.element("div").classes("circuit-wire").style(
                    "min-height:80px"
                )

                with ui.row().classes("gap-3").style("margin-top:14px"):
                    ui.button("▶  RUN ON HARDWARE", on_click=_run_circuit).style(
                        "font-family:var(--font-head)!important;font-size:0.75rem!important;"
                        "background:linear-gradient(135deg,var(--accent2),var(--accent))!important;"
                        "color:var(--bg)!important;font-weight:700!important;"
                        "border:none!important;border-radius:8px!important;"
                        "padding:10px 24px!important;letter-spacing:0.1em!important;"
                        "min-height:unset!important"
                    )
                    ui.button("CLEAR", on_click=_clear_circuit).style(
                        "font-family:var(--font-head)!important;font-size:0.75rem!important;"
                        "background:var(--bg2)!important;color:var(--text-dim)!important;"
                        "border:1px solid var(--border)!important;border-radius:8px!important;"
                        "padding:10px 18px!important;min-height:unset!important"
                    )

                ui.separator().style("border-color:var(--border);margin:14px 0")
                circuit_log = ui.label("").style(
                    "font-family:var(--font-mono);font-size:0.78rem;"
                    "color:var(--green);min-height:20px;white-space:pre-line"
                )

        # ── RIGHT: Bloch + camera ─────────────────────────────────────────────
        with ui.column().style("width:300px;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("STATE EVOLUTION").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                bloch_build_html = ui.html(
                    bloch_sphere_svg(state.qubit.theta, state.qubit.phi, 260)
                )

            with ui.card().classes("qcard"):
                ui.label("CAMERA FEED").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                ui.image(stream_ip).style(
                    "width:100%;border-radius:6px;border:1px solid var(--border)"
                )

    # Initialise empty wire
    render_circuit()
