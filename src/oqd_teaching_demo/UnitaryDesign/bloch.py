"""
widgets/bloch.py
────────────────
Bloch-sphere SVG renderer.

.
Returns raw SVG strings that can be injected with ui.html().
"""

from __future__ import annotations
import math

from quantum import prob_zero, bloch_state_name


def bloch_sphere_svg(theta: float, phi: float, size: int = 220) -> str:
    """
    Generate a styled SVG Bloch sphere for the given qubit state (θ, φ).

    Parameters
    ----------
    theta : polar angle in radians  (0 = north/|0⟩, π = south/|1⟩)
    phi   : azimuthal angle in radians
    size  : pixel dimensions of the square SVG canvas

    Returns
    -------
    str   : complete <svg>…</svg> markup
    """
    cx  = size // 2
    cy  = size // 2
    r   = int(size * 0.4)

    # Project state vector onto 2-D canvas
    vx = r * math.sin(theta) * math.cos(phi)
    vy = -r * math.cos(theta)           # SVG y-axis is inverted

    equator_ry = int(r * 0.35)

    # Interpolate dot colour: green (|0⟩) → cyan (equator) → red (|1⟩)
    p0 = prob_zero(theta)
    if p0 > 0.5:
        t = (p0 - 0.5) * 2
        dot_color = f"rgb({int(255*(1-t))},255,{int(255*(1-t)+136*t)})"
    else:
        t = p0 * 2
        dot_color = f"rgb(255,{int(t*34 + (1-t)*56)},{int(t*34)})"

    label = bloch_state_name(theta, phi)
    lx = cx + vx + 14 if vx >= 0 else cx + vx - 28
    ly = cy + vy

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}"
         xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="bg_grad" cx="40%" cy="35%">
          <stop offset="0%"   stop-color="#1a1a3e"/>
          <stop offset="100%" stop-color="#06060f"/>
        </radialGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <!-- Sphere body -->
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="url(#bg_grad)" stroke="#1e1e4a" stroke-width="1.5"/>

      <!-- Equator (dashed ellipse) -->
      <ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{equator_ry}"
               fill="none" stroke="#1e1e4a"
               stroke-width="1" stroke-dasharray="4,3"/>

      <!-- Axis lines -->
      <line x1="{cx}" y1="{cy-r-10}" x2="{cx}" y2="{cy+r+10}"
            stroke="#2a2a5a" stroke-width="1"/>
      <line x1="{cx-r-10}" y1="{cy}" x2="{cx+r+10}" y2="{cy}"
            stroke="#2a2a5a" stroke-width="1"/>

      <!-- Axis labels -->
      <text x="{cx+4}" y="{cy-r-14}"
            font-family="Share Tech Mono" font-size="12" fill="#00e5ff">|0⟩</text>
      <text x="{cx+4}" y="{cy+r+20}"
            font-family="Share Tech Mono" font-size="12" fill="#ff3860">|1⟩</text>
      <text x="{cx+r+12}" y="{cy+4}"
            font-family="Share Tech Mono" font-size="11" fill="#5a6a8a">x</text>

      <!-- State vector -->
      <line x1="{cx}" y1="{cy}" x2="{cx+vx:.1f}" y2="{cy+vy:.1f}"
            stroke="{dot_color}" stroke-width="2.5" filter="url(#glow)"/>

      <!-- State dot -->
      <circle cx="{cx+vx:.1f}" cy="{cy+vy:.1f}" r="5"
              fill="{dot_color}" filter="url(#glow)"/>

      <!-- State label -->
      <text x="{lx:.1f}" y="{ly+5:.1f}"
            font-family="Share Tech Mono" font-size="13"
            fill="{dot_color}" font-weight="bold">{label}</text>
    </svg>
    """
