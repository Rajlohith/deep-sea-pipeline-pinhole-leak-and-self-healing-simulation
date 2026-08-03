"""Pipeline physics (Module 2): physical constants, geometry, derived quantities."""
import numpy as np

from .layer_architecture import LayerArchitecture


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2 — PIPELINE PHYSICS PARAMETERS
# All physical constants in one place, referenced to specific layers and papers.
# ══════════════════════════════════════════════════════════════════════════════
class PipelinePhysics:
    """
    Physical constants, geometry, and derived quantities for the pipeline.

    Uses:
      — API MPMS [Ref 9]   for oil properties
      — Blasius [Ref 7]    for friction factor
      — ISO 5167 [Ref 6]   for orifice discharge
      — Hydrostatics       for external pressure
    """

    def __init__(self, arch: LayerArchitecture):
        self.arch = arch

        # ── Environment ───────────────────────────────────────────────────────
        self.depth_m      = 3_000.0        # m — study depth (design doc)
        self.rho_sw       = 1_025.0        # kg/m³ — seawater
        self.g            = 9.81           # m/s²
        self.T_C          = 3.0            # °C — NOAA deep-ocean profile
        # Hydrostatic: P = ρ·g·h  → ~297 bar at 3,000 m
        self.P_ext        = self.rho_sw * self.g * self.depth_m  # Pa

        # Verify Layer 1 pressure rating covers external pressure
        L1_rating = arch.layers[1]["pressure_rating_bar"]
        assert L1_rating * 1e5 > self.P_ext, (
            f"Layer 1 ({L1_rating} bar) cannot withstand {self.P_ext/1e5:.0f} bar!")

        # ── Pipeline geometry ─────────────────────────────────────────────────
        self.L            = 50_000.0       # m — 50 km pipeline length
        self.D            = 0.50           # m — internal flow bore diameter
        self.A_pipe       = np.pi * (self.D / 2) ** 2  # m² — flow cross-section

        # ── Internal flow [API MPMS, Ref 9] ──────────────────────────────────
        self.P_inlet      = 150e5          # Pa — 150 bar
        self.P_outlet     = 100e5          # Pa — 100 bar
        self.V_flow       = 1.5            # m/s — nominal crude velocity
        self.Q_nom        = self.A_pipe * self.V_flow   # m³/s — nominal flow
        self.rho_oil      = 850.0          # kg/m³ [API MPMS, Ref 9]
        self.mu_oil       = 0.015          # Pa·s at ~4°C [API MPMS, Ref 9]

        # ── Blasius friction factor (turbulent) [Ref 7] ───────────────────────
        # Re = ρ·V·D / μ;  valid range Re = 4,000–100,000
        self.Re           = self.rho_oil * self.V_flow * self.D / self.mu_oil
        self.f_blasius    = 0.316 / self.Re ** 0.25     # Blasius correlation

        # ── Pinhole leak — Layer 3+4 detect, Layer 5 heals ───────────────────
        self.d_pin        = 0.0005         # m — 0.5 mm pinhole diameter
        self.A_pin        = np.pi * (self.d_pin / 2) ** 2   # m² — pin area
        self.X_leak_m     = 20_000.0       # m — 20 km from inlet
        # ISO 5167 discharge coefficient for sharp-edged orifice [Ref 6]
        self.Cd           = 0.61

        # Driving ΔP: internal pressure minus internal pipe pressure at leak
        # Approximation: use inlet-to-outlet ΔP as proxy [Ref 8, Munson]
        self.dP_orifice   = self.P_inlet - self.P_outlet

        # Maximum (fully open) leak flow: Q = Cd·A·√(2ΔP/ρ)  [Ref 6, 8]
        self.Q_leak_max   = (
            self.Cd * self.A_pin
            * np.sqrt(2 * self.dP_orifice / self.rho_oil)
        )

        # ── Layer 7 power budget ──────────────────────────────────────────────
        L7                      = arch.layers[7]
        self.battery_Wh         = L7["battery_Wh"]
        self.battery_life_yr    = L7["battery_life_yr"]
        self.self_disc_yr       = L7["self_discharge_pct_yr"] / 100.0

    def summary(self):
        print("=" * 65)
        print("  PIPELINE PHYSICS — PARAMETER SUMMARY")
        print("=" * 65)
        print(f"  Depth             : {self.depth_m:.0f} m")
        print(f"  External pressure : {self.P_ext/1e5:.1f} bar  "
              f"(L1 rated {self.arch.layers[1]['pressure_rating_bar']} bar ✓)")
        print(f"  Inlet/Outlet P    : {self.P_inlet/1e5:.0f} / {self.P_outlet/1e5:.0f} bar")
        print(f"  Pipeline          : {self.L/1000:.0f} km × Ø{self.D*100:.0f} cm")
        print(f"  Flow velocity     : {self.V_flow} m/s")
        print(f"  Oil ρ / μ         : {self.rho_oil} kg/m³  /  {self.mu_oil} Pa·s  [Ref 9]")
        print(f"  Reynolds No.      : {self.Re:.0f}")
        print(f"  Blasius f         : {self.f_blasius:.5f}  [Ref 7]")
        print(f"  Pinhole Ø         : {self.d_pin*1000:.1f} mm  @ {self.X_leak_m/1000:.0f} km")
        print(f"  Q_leak_max        : {self.Q_leak_max*1000:.4f} L/s  [ISO 5167]")
        print(f"  Flow loss         : {self.Q_leak_max/self.Q_nom*100:.4f}%  (<< 1% noise)")
        print(f"  L7 battery        : {self.battery_Wh} Wh / {self.battery_life_yr} yr")
        print("=" * 65)

