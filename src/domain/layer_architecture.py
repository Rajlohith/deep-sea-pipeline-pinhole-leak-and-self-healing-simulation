"""Layer architecture (Module 1): the 7-layer pipeline design document."""
from typing import Dict, Tuple

from ..config import LAYER_CLR


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1 — LAYER ARCHITECTURE
# Encodes the 7-layer design doc exactly as specified in the project images.
# Every material choice is grounded in published deep-sea engineering practice.
# ══════════════════════════════════════════════════════════════════════════════
class LayerArchitecture:
    """
    Digital representation of the 7-Layer Smart Pipeline design document.

    Design philosophy — four construction steps, outside → inside:
      STEP 1  Environmental Shielding     → Layer 1
      STEP 2  Structural Backbone & Senses → Layers 2, 3
      STEP 3  Internal Protection & Repair → Layers 4, 5
      STEP 4  Central Core & Intelligence  → Layers 6, 7

    Survival % values come directly from the project architecture table
    (images provided). System survival = product of per-layer probabilities.
    """

    def __init__(self):
        self.layers: Dict[int, dict] = {

            # ── LAYER 1: UE44/TMA Syntactic Foam + Basalt Fiber ─────────────
            # UE44/TMA is a Trelleborg-grade syntactic foam (glass microspheres
            # in epoxy matrix, density ~440 kg/m³) specifically rated for
            # deep-water deployment.  Basalt Fiber reinforcement (tensile strength
            # ~4,800 MPa) replaces 3LPP as the outer structural skin — basalt is
            # corrosion-immune, has lower density than carbon fibre, and adds
            # acoustic damping.  Together they provide pressure damping, positive
            # buoyancy compensation, and superior thermal insulation.
            # Source: Final project design image — L1 "UE44/TMA Syntactic Foam + Basalt Fiber"
            1: {
                "material"        : "UE44/TMA Syntactic Foam + Basalt Fiber",
                "role"            : "Pressure damping + buoyancy + insulation",
                "step"            : "STEP 1 — Environmental Shielding",
                "survival_pct"    : 97.5,          # midpoint of 97–98%
                "thickness_mm"    : 25.0,
                "color"           : LAYER_CLR[1],
                "pressure_rating_bar": 350,         # rated well above 297 bar study depth
                "max_depth_m"     : 3000,
                "temp_range_C"    : (-5, 150),
                "foam_type"       : "UE44/TMA",     # Trelleborg deep-sea grade syntactic foam
                "foam_density_kg_m3": 440,          # UE44/TMA bulk density (~440 kg/m³)
                "basalt_tensile_MPa": 4800,         # Basalt fibre tensile strength
                "thermal_conductivity_W_mK": 0.12, # better insulation than 3LPP
                "acoustic_damping_dB_m": 6.0,      # dB/m sound attenuation at 10 kHz
                "buoyancy_neutral_depth_m": 3500,  # positive buoyancy to 3,500 m
            },

            # ── LAYER 2: Inconel 625 Structural Shell ────────────────────────
            # Inconel 625 (Ni-Cr-Mo superalloy) forms the load-bearing structural
            # shell of the pipeline.  Near-zero corrosion rate in seawater
            # (<0.005 mm/yr) — used in deep-sea wellheads, risers, and BOP stacks
            # for decades.  Acts as structural spine AND EMI-shielded signal
            # corridor for Layers 3/6/7.
            # Source: Final project design image — L2 "Inconel 625 Structural Shell"
            2: {
                "material"        : "Inconel 625 Structural Shell",
                "role"            : "Structural strength + corrosion resistance",
                "step"            : "STEP 2 — Structural Backbone & Senses",
                "survival_pct"    : 99.0,
                "thickness_mm"    : 15.0,
                "color"           : LAYER_CLR[2],
                "yield_MPa"       : 517,
                "UTS_MPa"         : 930,
                "corrosion_mm_yr" : 0.005,          # near zero in seawater
                "temp_range_C"    : (-196, 980),
                "saltwater_immune": True,
            },

            # ── LAYER 3: PMN-PT + Floating Ceramic Shock Mount ──────────────
            # PMN-PT (Lead Magnesium Niobate-Lead Titanate, Pb(Mg₁/₃Nb₂/₃)O₃-
            # PbTiO₃) is a single-crystal piezoelectric with d33 ~2000 pC/N —
            # nearly 1,000× more sensitive than quartz (d33 ~2.3 pC/N).  This
            # makes it ideal for broadband pressure and low-frequency vibration
            # sensing across the entire pipeline wall.
            # The Floating Ceramic Shock Mount mechanically decouples the PMN-PT
            # element from the Inconel shell, providing ~20 dB of structure-borne
            # vibration isolation and preventing sensor overload during water-
            # hammer transients.  Together they monitor bulk wall pressure and
            # vibration continuously, feeding data to Layer 6 DAS.
            # Source: Final project design image — L3 "PMN-PT + Floating Ceramic Shock Mount"
            3: {
                "material"        : "PMN-PT + Floating Ceramic Shock Mount",
                "role"            : "Pressure / vibration sensing",
                "step"            : "STEP 2 — Structural Backbone & Senses",
                "survival_pct"    : 99.0,
                "thickness_mm"    : 8.0,
                "color"           : LAYER_CLR[3],
                "d33_pC_N"        : 2000,           # PMN-PT piezoelectric coeff. (vs quartz 2.3)
                "dielectric_const": 5000,           # high ε enables low-noise charge amp
                "freq_range_Hz"   : (0.01, 10_000), # broad pressure + vibration band
                "sensitivity_dB"  : -150,           # dB re 1 V/µPa (PMN-PT at resonance)
                "depth_rating_m"  : 6000,
                "mount_isolation_dB": 20,           # structure-borne vibration rejection
                "sensor_spacing_m": 500,
                "sensing_modes"   : ["bulk_pressure", "vibration", "water_hammer"],
            },

            # ── LAYER 4: Quartz + Hydrophone Hybrid ──────────────────────────
            # This hybrid acoustic layer pairs two complementary technologies:
            #   (a) Quartz piezoelectric element: ultra-stable, low-noise reference
            #       with a frequency-independent response from DC to 100 kHz.
            #       Acts as the timing and frequency-calibration anchor for the
            #       system, enabling precise measurement of the Strouhal orifice tone.
            #   (b) Wideband Hydrophone: high-sensitivity omnidirectional receiver
            #       for far-field leak acoustics along the pipeline bore.
            # Together they form a matched-filter detector: quartz identifies the
            # precise orifice tone frequency (f = St·V_jet/d_pin); the hydrophone
            # detects it across the 500 m sensor spacing.  This hybrid architecture
            # resolves pinhole signatures down to 0.01% flow loss — well below the
            # ±0.6% pressure noise floor (mandating this dedicated acoustic layer).
            # Source: Final project design image — L4 "Quartz + Hydrophone Hybrid"
            4: {
                "material"        : "Quartz + Hydrophone Hybrid",
                "role"            : "Acoustic crack & leak detection",
                "step"            : "STEP 3 — Internal Protection & Self-Repair",
                "survival_pct"    : 98.0,
                "thickness_mm"    : 6.0,
                "color"           : LAYER_CLR[4],
                "strouhal_St"     : 0.2,            # Strouhal No. for sharp-edged orifice [Ref 8]
                "freq_range_Hz"   : (1, 100_000),   # wideband acoustic coverage
                "sensitivity_dB"  : -170,           # dB re 1 V/µPa (quartz element)
                "depth_rating_m"  : 6000,
                "sensor_spacing_m": 500,
                "det_threshold_pct": 0.01,          # <0.01% flow loss detectable
                "quartz_stab_ppm" : 0.1,            # quartz frequency stability (ppm/°C)
                "hybrid_snr_gain_dB": 6.0,          # SNR gain vs single-element
            },

            # ── LAYER 5: Hybrid Healing System ───────────────────────────────
            # The Hybrid Healing System combines THREE autonomous repair mechanisms
            # to address crack initiation and pinhole development:
            #
            #   Mechanism A — IPDI@SPUA Chemical Capsules:
            #     Isophorone Diisocyanate (IPDI) microencapsulated in polyurea
            #     shells (IPDI@SPUA) — validated at 150 bar seawater by Zeng
            #     et al. (2025) [Ref 10].  Deep-sea pressure PROMOTES rupture;
            #     IPDI + H₂O → polyurea, using seawater as co-reactant.
            #     NOT DCPD+Grubbs (deactivated by Cl⁻/moisture at 3°C [Ref 12]).
            #
            #   Mechanism B — PTFE Vascular Network:
            #     Pressurised PTFE microchannels (Ø 0.3 mm, rated 6,000 m+)
            #     deliver sealing fluid continuously [Ref 2, 15].  Calibrated to
            #     Toohey et al. (2007) vascular rate constant k = 0.05 min⁻¹.
            #
            #   Mechanism C — Shape Memory Polymer (SMP) Matrix:
            #     SMP filler within the PTFE network mechanically closes micro-
            #     cracks by elastic recovery when local temperature fluctuates
            #     (crude oil vs seawater ΔT).  Adds ~5–10% efficiency gain.
            #
            # Combined deep-sea efficiency: 60–80% (improved from IPDI-only 55–75%
            # by SMP mechanical closure contribution).
            # Source: Final project design image — L5 "Hybrid Healing System"
            5: {
                "material"         : "Hybrid Healing System",
                "role"             : "Self-healing crack repair",
                "step"             : "STEP 3 — Internal Protection & Self-Repair",
                "survival_pct"     : 99.0,
                "thickness_mm"     : 10.0,
                "color"            : LAYER_CLR[5],
                "ptfe_ch_diam_mm"  : 0.3,
                "ipdi_cure_temp_C" : 4,             # IPDI cures at deep-sea T [Ref 10]
                "depth_rated_m"    : 6000,
                # ── Phase 1: IPDI@SPUA chemical sealing (0–60 s) ─────────────
                "phase1_name"      : "IPDI@SPUA + SMP Crack Seal",
                "phase1_time_s"    : 60,
                "tau_phase1_s"     : 12.0,          # exponential time constant [Ref 10]
                "onset_s"          : 5.0,            # pressure-wave trigger delay
                # ── Phase 2: PTFE vascular consolidation (60 s – 10 min) ──────
                "phase2_name"      : "PTFE Vascular + SMP Recovery",
                "k_phase2_min"     : 0.05,           # min⁻¹ [Ref 2, Fig 4]
                # ── Hybrid efficiency (improved vs IPDI-only) ─────────────────
                # IPDI-only (55–75%) + SMP mechanical assist (+5–10%) = 60–80%
                "efficiency_range" : (0.60, 0.80),
                "efficiency_note"  : "Hybrid: IPDI (55-75%) + SMP mechanical closure (+5-10%)",
                "smp_contribution_pct": 7.5,        # midpoint SMP assist
            },

            # ── LAYER 6: Dual Silica Fiber Optic (DAS) ───────────────────────
            # Two silica fibres carry Distributed Acoustic Sensing (DAS) signals.
            # Rayleigh backscatter along the fibre picks up vibration at the
            # pinhole.  Light is UNAFFECTED by hydrostatic pressure — unlike
            # electrical sensors.  If Fiber A fails, Fiber B takes over instantly.
            # Detection time < 30 s established in [Ref 4] Bao & Chen (2012).
            # Source: Project images — "If one breaks — second takes over
            # instantly — light unaffected by pressure"
            6: {
                "material"         : "Dual Redundant Fiber Optics",
                "role"             : "Data communication + monitoring",
                "step"             : "STEP 4 — Central Core & Intelligence",
                "survival_pct"     : 98.0,
                "thickness_mm"     : 4.0,
                "color"            : LAYER_CLR[6],
                "spatial_res_m"    : 1.0,
                "detection_time_s" : 30,
                "snr_leak_dB"      : 12.0,
                "snr_no_leak_dB"   : 3.0,
                "redundant"        : True,           # dual fibre for failover
                "pressure_immune"  : True,
                "bandwidth_Hz"     : 50_000,
                "fiber_count"      : 2,
            },

            # ── LAYER 7: Hybrid Power Layer ──────────────────────────────────
            # The Hybrid Power Layer integrates THREE energy sources to guarantee
            # autonomous, maintenance-free operation at 3,000 m for 10+ years:
            #
            #   Source A — Piezoelectric Energy Harvester:
            #     Stack of PMN-PT wafers (complementary to Layer 3) scavenges
            #     energy from pipeline flow-induced vibrations.
            #     Yield: ~50 mW continuous at nominal flow velocity (1.5 m/s).
            #
            #   Source B — Thermoelectric Generator (TEG):
            #     Bi₂Te₃ TEG modules span the wall thermal gradient between
            #     crude oil (~40°C internal) and seawater (3°C external), ΔT≈37 K.
            #     Yield: ~150 mW (Seebeck coefficient 200 µV/K, ZT ~ 1.0).
            #
            #   Source C — Li-Thionyl Backup Battery (Li-SOCl₂):
            #     5,000 Wh primary cell; <1%/yr self-discharge; rated −60 to +85°C;
            #     proven in Argo floats and deep-sea landers for 10-year missions.
            #     Activates automatically if harvested power drops below threshold.
            #
            # Total available: ~200 mW harvested + 5,000 Wh battery backup.
            # Sapphire (Al₂O₃) optical window retained as monitoring port.
            # Source: Final project design image — L7 "Hybrid Power Layer"
            7: {
                "material"         : "Hybrid Power Layer",
                "role"             : "Energy harvesting + backup power",
                "step"             : "STEP 4 — Central Core & Intelligence",
                "survival_pct"     : 98.5,           # midpoint 98–99%
                "thickness_mm"     : 6.0,
                "color"            : LAYER_CLR[7],
                # ── Harvesting sub-systems ────────────────────────────────────
                "piezo_harvest_mW" : 50,             # PMN-PT flow vibration harvest
                "teg_harvest_mW"   : 150,            # Bi₂Te₃ TEG at ΔT=37 K
                "total_harvest_mW" : 200,            # combined harvested power
                # ── Li-Thionyl backup battery ─────────────────────────────────
                "battery_Wh"       : 5000,
                "battery_life_yr"  : 10,
                "battery_T_range_C": (-60, 85),
                "self_discharge_pct_yr": 1.0,        # <1%/yr (Li-Thionyl spec)
                # ── Optical monitoring port ────────────────────────────────────
                "sapphire_depth_m" : 6000,
                "optical_transm"   : 0.85,
                "hardness_mohs"    : 9.0,
            },
        }

        # Step → layer mapping for summary & cross-section figure
        self.steps = {
            "STEP 1 — Environmental Shielding"          : [1],
            "STEP 2 — Structural Backbone & Senses"     : [2, 3],
            "STEP 3 — Internal Protection & Self-Repair": [4, 5],
            "STEP 4 — Central Core & Intelligence"      : [6, 7],
        }

    def overall_survival(self) -> float:
        """System survival = product of per-layer survival probabilities."""
        p = 1.0
        for L in self.layers.values():
            p *= L["survival_pct"] / 100.0
        return p * 100.0

    def display_radii(self, r_total: float = 0.97) -> Dict[int, Tuple[float, float]]:
        """
        Compute (r_inner, r_outer) for cross-section visualisation.
        Layers scaled proportionally by thickness_mm, fitted inside r_total.
        """
        total_t = sum(L["thickness_mm"] for L in self.layers.values())
        radii   = {}
        r_outer = r_total
        for i in range(1, 8):
            frac    = self.layers[i]["thickness_mm"] / total_t
            r_inner = max(r_outer - frac * r_total, 0.05)
            radii[i] = (r_inner, r_outer)
            r_outer  = r_inner
        return radii

    def summary(self):
        print("=" * 72)
        print("  7-LAYER SMART PIPELINE — ARCHITECTURE SUMMARY")
        print("=" * 72)
        for step, nums in self.steps.items():
            print(f"\n  {step}")
            for n in nums:
                L = self.layers[n]
                note = ""
                if n == 5:
                    note = "  ← Hybrid: IPDI@SPUA + PTFE + SMP (3-mechanism)"
                print(f"    L{n}: {L['material']:<50} "
                      f"{L['survival_pct']:.1f}%{note}")
        print(f"\n  System Survival: {self.overall_survival():.2f}%")
        print("=" * 72)

