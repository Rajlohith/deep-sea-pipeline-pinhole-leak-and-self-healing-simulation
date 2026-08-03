"""
Main orchestrator: CLI argument parsing and the top-level simulation run
that initialises every module, trains the digital twin, and dispatches to
the requested figures (and, unless skipped, the PHMSA validation report).
"""
import os
import argparse

from .config import OUTPUT_DIR, PHMSA_PATH
from .domain import (
    LayerArchitecture,
    PipelinePhysics,
    LeakSimulator,
    SensorSystem,
    HealingSystem,
    PowerSystem,
)
from .ml import MLSensorFusion
from .validation import _load_phmsa, print_ieee_report
from .plotting import (
    fig1_pressure_flow,
    fig2_sensor_signals,
    fig3_healing_response,
    fig4_cross_section,
    fig5_intelligence_layer,
    fig6_structural_environment,
    fig7_performance_summary,
    fig8_phmsa_landscape,
    fig9_quantitative_validation,
    fig10_ieee_validation_dashboard,
    fig11_ml_sensor_fusion,
)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="7-Layer Deep-Sea Pipeline Simulation")
    parser.add_argument("--figs", type=int, nargs="+",
                        help="Which figures to render (1-11). Default: all.")
    parser.add_argument("--no-phmsa", action="store_true",
                        help="Skip PHMSA validation (Figs 8-10)")
    args = parser.parse_args()

    print("=" * 72)
    print("  DEEP-SEA 7-LAYER SMART PIPELINE — FINAL ARCHITECTURE SIMULATION")
    print("  Pinhole Detection (PMN-PT+Quartz/Hydro) + Hybrid Healing + PHMSA Validation")
    print("  RV College of Engineering — DTL Phase 1")
    print("=" * 72)

    # ── Initialise all modules ────────────────────────────────────────────────
    arch    = LayerArchitecture()
    phys    = PipelinePhysics(arch)
    leak    = LeakSimulator(phys)
    sensors = SensorSystem(phys, arch)
    heal    = HealingSystem(arch, seed=13)
    power   = PowerSystem(arch)

    # ── Module 7: Machine Learning Sensor Fusion ──────────────────────────
    # Must be initialised AFTER all physics modules; does not modify any of
    # them.  Reads arch, phys, sensors, heal as read-only references.
    ml = MLSensorFusion(arch, phys, sensors, heal)
    ml.train_digital_twin(n_scenarios=1000)

    arch.summary()
    phys.summary()
    print(f"\n  Layer 5 hybrid agent   : IPDI@SPUA + PTFE vascular + SMP matrix")
    print(f"  Hybrid efficiency      : η = {heal.eta*100:.1f}%  "
          f"(60–80% hybrid; IPDI-only was 55–75%)")
    print(f"  Orifice acoustic tone  : f = {sensors.f_orifice:.0f} Hz  "
          f"(Strouhal, L4 Quartz+Hydrophone Hybrid)")
    print(f"\n  Rendering figures → {OUTPUT_DIR}\n")

    # ── Figure dispatch table ─────────────────────────────────────────────────
    sim_figs = {
        1: lambda: fig1_pressure_flow(phys, leak),
        2: lambda: fig2_sensor_signals(phys, arch, sensors),
        3: lambda: fig3_healing_response(phys, leak, heal),
        4: lambda: fig4_cross_section(phys, arch),
        5: lambda: fig5_intelligence_layer(phys, arch, sensors, power),
        6: lambda: fig6_structural_environment(phys, arch, heal),
        7: lambda: fig7_performance_summary(phys, arch, heal),
        11: lambda: fig11_ml_sensor_fusion(ml, arch),   # ← NEW
    }

    # Determine which figs to render
    if args.figs:
        to_render = args.figs
    else:
        to_render = list(range(1, 12))   # now includes Fig 11

    # Simulation figures (1–7)
    for n in to_render:
        if n in sim_figs:
            sim_figs[n]()

    # PHMSA validation figures (8–10)
    if not args.no_phmsa and any(n in to_render for n in [8, 9, 10]):
        if not os.path.exists(PHMSA_PATH):
            print(f"\n  ⚠ PHMSA dataset not found at {PHMSA_PATH}")
            print("    Download from:")
            print("    https://www.phmsa.dot.gov/data-and-statistics/pipeline/"
                  "pipeline-incident-flagged-files")
            print("    Save as phmsa_clean.csv in the same directory.\n")
        else:
            print("\n  Loading PHMSA dataset …")
            df = _load_phmsa()
            print(f"  ✓ {len(df):,} incidents loaded\n")

            if 8 in to_render:
                fig8_phmsa_landscape(df)
            if 9 in to_render:
                fig9_quantitative_validation(df, phys, heal)
            if 10 in to_render:
                fig10_ieee_validation_dashboard(df, phys, arch, heal)

            if any(n in to_render for n in [8, 9, 10]):
                print_ieee_report(df, phys, arch, heal)

    print("\n" + "=" * 72)
    print(f"  ✓ All requested figures saved to {OUTPUT_DIR}")
    print("=" * 72)


if __name__ == "__main__":
    main()