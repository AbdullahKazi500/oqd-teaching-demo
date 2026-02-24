"""
tabs/challenge.py
─────────────────
"Challenge" tab — presents progressively harder quantum-state targets,
validates the learner's gate choices, awards points, and drives the hardware
as a victory celebration.

Public API
──────────
build(device, score_label) -> None
"""

from __future__ import annotations
import asyncio

from nicegui import ui

import state
import quantum as q
from config import CHALLENGES, CHALLENGE_TOLERANCE
from widgets.bloch import bloch_sphere_svg
from widgets.gate_buttons import quick_gate_row


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build(device, score_label: ui.label) -> None:
    """Render the Challenge tab into the current NiceGUI layout context."""

    # ── mutable UI references ─────────────────────────────────────────────────
    bloch_html:          ui.html  | None = None
    challenge_title_lbl: ui.label | None = None
    challenge_diff_lbl:  ui.label | None = None
    challenge_desc_lbl:  ui.label | None = None
    challenge_target_lbl:ui.label | None = None
    challenge_status:    ui.label | None = None
    score_big_lbl:       ui.label | None = None
    challenge_count_lbl: ui.label | None = None

    # ── internal helpers ──────────────────────────────────────────────────────

    def _refresh_bloch():
        bloch_html.set_content(
            bloch_sphere_svg(state.qubit.theta, state.qubit.phi, 260)
        )

    def _reset_qubit():
        state.qubit.reset()
        _refresh_bloch()

    def _load_challenge():
        idx = state.score.current_challenge % len(CHALLENGES)
        c   = CHALLENGES[idx]
        challenge_title_lbl.set_text(c["title"])
        challenge_diff_lbl.set_text(c["difficulty"])
        challenge_desc_lbl.set_text(c["desc"])
        challenge_target_lbl.set_text(c["target_label"])
        challenge_status.set_text("")
        challenge_status.style("color:var(--text-dim)")
        _reset_qubit()

    def _check_challenge():
        idx = state.score.current_challenge % len(CHALLENGES)
        c   = CHALLENGES[idx]

        if q.challenge_passed(
            state.qubit.theta, state.qubit.phi,
            c["target_theta"], c["target_phi"],
            tol=CHALLENGE_TOLERANCE,
        ):
            state.score.add(c["points"])
            score_label.set_text(str(state.score.total))
            score_big_lbl.set_text(str(state.score.total))
            challenge_count_lbl.set_text(
                f"{state.score.challenges_done} challenges completed"
            )
            challenge_status.set_text(
                f"✓ CORRECT! +{c['points']} pts — loading next challenge…"
            )
            challenge_status.style("color:var(--green)")

            # Victory: blast all lasers, then cool down
            for i in range(4):
                device.red_lasers.set_intensity(idx=i, intensity=1.0)

            async def _victory_cooldown():
                await asyncio.sleep(0.5)
                for i in range(4):
                    device.red_lasers.set_intensity(idx=i, intensity=0.0)

            asyncio.ensure_future(_victory_cooldown())
            ui.timer(1.5, _load_challenge, once=True)

    def _apply_gate(gate: str):
        t, p = q.apply_gate(gate, state.qubit.theta, state.qubit.phi)
        state.qubit.set(t, p)

        intensities = q.laser_intensities_for_gate(gate)
        for i, v in enumerate(intensities):
            device.red_lasers.set_intensity(idx=i, intensity=v)
        device.trap.mode(q.trap_motion_for_gate(gate))

        _refresh_bloch()
        _check_challenge()

    # ─────────────────────────────────────────────────────────────────────────
    # LAYOUT
    # ─────────────────────────────────────────────────────────────────────────

    with ui.row().classes("w-full gap-6").style("align-items:flex-start"):

        # ── LEFT: challenge card + gate controls ──────────────────────────────
        with ui.column().style("flex:1;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("QUANTUM CHALLENGES").classes("qheading").style("font-size:0.9rem")
                ui.label(
                    "Apply the correct sequence of gates to reach the target state. "
                    "Use quick gates below. Score points for each success!"
                ).style(
                    "font-family:var(--font-body);font-size:0.82rem;"
                    "color:var(--text-dim);margin-top:4px"
                )

            with ui.card().classes("qcard tut-active"):
                with ui.row().classes("items-center justify-between w-full"):
                    challenge_title_lbl = ui.label("").style(
                        "font-family:var(--font-head);color:var(--yellow);"
                        "font-size:1rem;letter-spacing:0.08em"
                    )
                    challenge_diff_lbl = ui.label("").style(
                        "font-family:var(--font-mono);font-size:0.72rem;color:var(--text-dim)"
                    )

                ui.separator().style("border-color:var(--border);margin:10px 0")

                challenge_desc_lbl = ui.label("").style(
                    "font-family:var(--font-body);font-size:0.85rem;"
                    "color:var(--text);line-height:1.55"
                )

                with ui.row().classes("gap-4 items-center").style("margin-top:14px"):
                    ui.label("TARGET STATE:").style(
                        "font-family:var(--font-mono);font-size:0.75rem;color:var(--text-dim)"
                    )
                    challenge_target_lbl = ui.label("").style(
                        "font-family:var(--font-mono);font-size:1.1rem;"
                        "color:var(--accent);font-weight:700"
                    )

                quick_gate_row(on_gate=_apply_gate, gates=["H", "X", "Y", "Z", "S", "T", "M"])

                ui.separator().style("border-color:var(--border);margin:10px 0")
                challenge_status = ui.label("").style(
                    "font-family:var(--font-mono);font-size:0.85rem;"
                    "text-align:center;width:100%"
                )

                with ui.row().classes("gap-3").style("margin-top:8px"):
                    ui.button("RESET QUBIT", on_click=_reset_qubit).style(
                        "font-family:var(--font-head)!important;font-size:0.7rem!important;"
                        "background:var(--bg2)!important;color:var(--text-dim)!important;"
                        "border:1px solid var(--border)!important;border-radius:6px!important;"
                        "padding:8px 14px!important;min-height:unset!important"
                    )
                    ui.button("NEXT CHALLENGE ▶", on_click=_load_challenge).style(
                        "font-family:var(--font-head)!important;font-size:0.7rem!important;"
                        "background:var(--accent2)!important;color:#fff!important;"
                        "border:none!important;border-radius:6px!important;"
                        "padding:8px 14px!important;min-height:unset!important"
                    )

        # ── RIGHT: Bloch + scoreboard ─────────────────────────────────────────
        with ui.column().style("width:300px;gap:16px"):
            with ui.card().classes("qcard"):
                ui.label("CURRENT STATE").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                bloch_html = ui.html(
                    bloch_sphere_svg(state.qubit.theta, state.qubit.phi, 260)
                )

            with ui.card().classes("qcard"):
                ui.label("SCORE BOARD").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                with ui.column().classes("items-center w-full").style("gap:6px"):
                    ui.label("POINTS").style(
                        "font-family:var(--font-mono);font-size:0.7rem;color:var(--text-dim)"
                    )
                    score_big_lbl = ui.label(str(state.score.total)).style(
                        "font-family:var(--font-head);font-size:2.5rem;"
                        "color:var(--yellow);letter-spacing:0.05em;line-height:1"
                    )
                    challenge_count_lbl = ui.label(
                        f"{state.score.challenges_done} challenges completed"
                    ).style(
                        "font-family:var(--font-mono);font-size:0.72rem;color:var(--text-dim)"
                    )

    # Populate first challenge on build
    _load_challenge()
