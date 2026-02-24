"""
tabs/hardware.py
────────────────
"Hardware" tab — direct laser sliders, trap toggle, camera feed,
and a component-comparison reference card.

Public API
──────────
build(device, stream_ip) -> None
"""

from __future__ import annotations

from nicegui import ui
from config import NUM_LASER_CHANNELS


def build(device, stream_ip: str) -> None:
    """Render the Hardware Control tab into the current NiceGUI layout context."""

    with ui.row().classes("w-full gap-6").style("align-items:flex-start"):

        # ── LEFT: laser sliders + trap toggle ─────────────────────────────────
        with ui.column().style("flex:1;gap:16px"):

            # Laser sliders
            with ui.card().classes("qcard"):
                ui.label("LASER CONTROL").classes("qheading").style(
                    "font-size:0.9rem;margin-bottom:12px"
                )
                sliders: dict[int, ui.slider] = {}

                for i in range(NUM_LASER_CHANNELS):
                    with ui.row().classes("items-center gap-4 w-full").style(
                        "margin-bottom:8px"
                    ):
                        ui.label(f"Control Laser {i+1}").style(
                            "font-family:var(--font-mono);font-size:0.8rem;"
                            "color:var(--text);width:130px"
                        )
                        sliders[i] = (
                            ui.slider(min=0.0, max=1.0, step=0.01, value=0.0)
                            .props("color=red")
                            .style("flex:1")
                            .on(
                                "change",
                                lambda e, idx=i: device.red_lasers.set_intensity(
                                    idx=idx, intensity=e.args
                                ),
                            )
                        )

                def _all_on():
                    for idx, sl in sliders.items():
                        sl.value = 1.0
                        device.red_lasers.set_intensity(idx=idx, intensity=1.0)

                def _all_off():
                    for idx, sl in sliders.items():
                        sl.value = 0.0
                        device.red_lasers.set_intensity(idx=idx, intensity=0.0)

                with ui.row().classes("gap-3").style("margin-top:8px"):
                    ui.button("ALL ON", on_click=_all_on).style(
                        "font-family:var(--font-head)!important;font-size:0.7rem!important;"
                        "background:var(--red)!important;color:#fff!important;"
                        "border:none!important;border-radius:6px!important;"
                        "padding:8px 14px!important;min-height:unset!important"
                    )
                    ui.button("ALL OFF", on_click=_all_off).style(
                        "font-family:var(--font-head)!important;font-size:0.7rem!important;"
                        "background:var(--bg2)!important;color:var(--text-dim)!important;"
                        "border:1px solid var(--border)!important;border-radius:6px!important;"
                        "padding:8px 14px!important;min-height:unset!important"
                    )

            # Trap toggle
            with ui.card().classes("qcard"):
                ui.label("TRAP CONTROL").classes("qheading").style(
                    "font-size:0.9rem;margin-bottom:12px"
                )
                ui.label(
                    "Move the ion trap to adjust coupling between ions. "
                    "Left/right motion modulates the standing wave pattern."
                ).style(
                    "font-family:var(--font-body);font-size:0.8rem;"
                    "color:var(--text-dim);margin-bottom:12px"
                )
                trap_toggle = ui.toggle(
                    {"left": "◀ LEFT", "stop": "■ STOP", "right": "RIGHT ▶"},
                    on_change=lambda e: device.trap.mode(e.value),
                ).style("font-family:var(--font-mono)!important")
                trap_toggle.value = "stop"

        # ── RIGHT: camera + reference card ────────────────────────────────────
        with ui.column().style("width:320px;gap:16px"):

            with ui.card().classes("qcard"):
                ui.label("CAMERA FEED").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                ui.image(stream_ip).style(
                    "width:100%;border-radius:6px;border:1px solid var(--border)"
                )

            with ui.card().classes("qcard"):
                ui.label("ABOUT THE HARDWARE").classes("qheading").style(
                    "font-size:0.8rem;margin-bottom:8px"
                )
                ui.html("""
                <div style="font-family:var(--font-body);font-size:0.8rem;
                            color:var(--text);line-height:1.6">
                  <div style="display:grid;grid-template-columns:1fr 1fr;
                              gap:8px;margin-bottom:10px">

                    <div style="background:var(--bg2);border:1px solid var(--border);
                                border-radius:8px;padding:8px">
                      <div style="font-family:var(--font-mono);color:var(--accent);
                                  font-size:0.7rem">DEMO</div>
                      <div style="margin-top:4px">Acoustic levitator + polystyrene balls</div>
                    </div>

                    <div style="background:var(--bg2);border:1px solid var(--border);
                                border-radius:8px;padding:8px">
                      <div style="font-family:var(--font-mono);color:var(--green);
                                  font-size:0.7rem">REAL QC</div>
                      <div style="margin-top:4px">Electromagnetic ion trap + ions</div>
                    </div>

                    <div style="background:var(--bg2);border:1px solid var(--border);
                                border-radius:8px;padding:8px">
                      <div style="font-family:var(--font-mono);color:var(--accent);
                                  font-size:0.7rem">DEMO</div>
                      <div style="margin-top:4px">5 red diode lasers</div>
                    </div>

                    <div style="background:var(--bg2);border:1px solid var(--border);
                                border-radius:8px;padding:8px">
                      <div style="font-family:var(--font-mono);color:var(--green);
                                  font-size:0.7rem">REAL QC</div>
                      <div style="margin-top:4px">Control lasers for quantum gates</div>
                    </div>
                  </div>

                  Built on Raspberry Pi GPIO → FPGA-based real-time control
                </div>
                """)
