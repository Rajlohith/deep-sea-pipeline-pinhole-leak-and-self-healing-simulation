"""
================================================================================
  DEEP-SEA 7-LAYER SMART PIPELINE: PINHOLE LEAK DETECTION & SELF-HEALING
  Complete Academic Simulation — RV College of Engineering, DTL Phase 1
================================================================================

ARCHITECTURE (from project design document — FINAL REVISION, image-verified):
  ┌─────┬───────────────────────────────────────┬──────────────────────────────────┬──────────┐
  │ Layer│ Material / Technology                 │ Main Function                    │ Survival │
  ├─────┼───────────────────────────────────────┼──────────────────────────────────┼──────────┤
  │  1  │ UE44/TMA Syntactic Foam + Basalt Fiber│ Pressure damping+buoyancy+insul. │ 97–98%   │
  │  2  │ Inconel 625 Structural Shell          │ Structural strength+corr.resist. │ 99%      │
  │  3  │ PMN-PT + Floating Ceramic Shock Mount │ Pressure / vibration sensing     │ 99%      │
  │  4  │ Quartz + Hydrophone Hybrid            │ Acoustic crack & leak detection  │ 98%      │
  │  5  │ Hybrid Healing System                 │ Self-healing crack repair        │ 99%      │
  │  6  │ Dual Redundant Fiber Optics           │ Data communication + monitoring  │ 98%      │
  │  7  │ Hybrid Power Layer                    │ Energy harvesting + backup power │ 98–99%   │
  └─────┴───────────────────────────────────────┴──────────────────────────────────┴──────────┘

OPERATING CONDITIONS:
  Depth         : 3,000 m          External P   : ~297 bar
  Temperature   : 2–4 °C           Internal P   : 100–150 bar
  Fluid         : Crude oil         Density      : 850 kg/m³
  Pipeline      : 50 km × Ø 0.5 m  Pinhole      : 0.5 mm Ø at 20 km

CRITICAL DESIGN NOTE — Healing Agent Selection (WHY NOT DCPD):
  The classic White et al. (2001) DCPD + Grubbs catalyst system is NOT used
  in this simulation for deep-sea application. Reasons (literature-grounded):
    1. Grubbs catalyst is deactivated by seawater moisture and NaCl ions
       → Ref [NEW-2] Mauldin et al. (2007): endo-DCPD near its 33°C melt
         point at 3°C; catalyst poisoned before ROMP can complete
    2. Saline polymerisation rate drops 60% (Delft University data)
       → Ref [NEW-4] Afrinaldi et al. (2023)
    3. 300 bar pressure causes 40% premature capsule rupture
       → Ref [NEW-1] Zeng et al. (2025)
  INSTEAD, Layer 5 uses IPDI (isocyanate) + FBE (Fusion Bonded Epoxy):
    - IPDI reacts WITH water to form polyurea → seawater is the co-reactant
    - FBE cures at 4°C and is proven on deepwater pipelines
    - Validated at 15 MPa (150 bar) immersion for 1008 h by Zeng et al. (2025)
    - Healing efficiency at realistic deep-sea conditions: 55–75% (reduced from
      the 70–90% lab values of White 2001, per Delft 60% saline penalty)

REFERENCES:
  [1]  White S.R. et al. (2001). "Autonomic healing of polymer composites."
       Nature, 409(6822), 794–797. https://doi.org/10.1038/35057232
       → Original microcapsule self-healing concept (lab conditions, dry)

  [2]  Toohey K.S. et al. (2007). "Self-healing materials with microvascular
       networks." Nature Materials, 6(8), 581–585.
       https://doi.org/10.1038/nmat1934
       → Vascular network rate constant k = 0.05 min⁻¹ (Fig. 4 calibration)

  [3]  Kessler M.R. & White S.R. (2001). "Self-activated healing of
       delamination damage in woven composites." Composites Part A, 32(5),
       683–699. https://doi.org/10.1016/S1359-835X(00)00149-4
       → Epoxy capsule characterisation and mechanical recovery data

  [4]  Bao X. & Chen L. (2012). "Recent progress in distributed fiber optic
       sensors." Sensors, 12(7), 8601–8639.
       https://doi.org/10.3390/s120708601
       → DAS / BOTDR sensing principles for pipeline leak detection

  [5]  Wenz G.M. (1962). "Acoustic ambient noise in the ocean: Spectra and
       sources." J. Acoust. Soc. Am., 34(12), 1936–1956.
       https://doi.org/10.1121/1.1909155
       → Ocean noise floor 120 dB re 1 µPa; noise amplitude modelling

  [6]  ISO 5167:2003. Measurement of fluid flow by means of pressure
       differential devices. International Organization for Standardization.
       → Orifice discharge coefficient Cd = 0.61

  [7]  Blasius H. (1913). "Das Ähnlichkeitsgesetz bei Reibungsvorgängen in
       Flüssigkeiten." Forschungsarbeiten VDI, 131, 1–40.
       → Turbulent friction factor f = 0.316 / Re^0.25

  [8]  Munson B.R., Young D.F. & Okiishi T.H. (2006). Fundamentals of Fluid
       Mechanics, 5th ed. John Wiley & Sons.
       → Darcy-Weisbach pressure drop; orifice flow derivation

  [9]  API MPMS (Manual of Petroleum Measurement Standards).
       American Petroleum Institute. Washington D.C.
       → Crude oil density 850 kg/m³; viscosity 0.015 Pa·s at ~4°C

  [10] Zeng X. et al. (2025). "Self-healing performance and anti-corrosion
       mechanism of microcapsule-containing epoxy coatings under deep-sea
       environment." Progress in Organic Coatings, 202, 109108.
       https://doi.org/10.1016/j.porgcoat.2025.109108
       → IPDI@SPUA capsules tested at 15 MPa seawater; pressure PROMOTES
         capsule rupture; impedance maintained at 6.32×10⁶ Ω·cm² after
         1008 h immersion at deep-sea pressure [KEY deep-sea validation]

  [11] Feng H. et al. (2020). "Fabrication of microcapsule-type composites
       with the capability of underwater self-healing and damage visualization."
       RSC Advances, 10(56), 33675–33682.
       → Underwater healing efficiency 85.6% using water-activated amine
         curing agents (FLCAs); validates water-reactive healing agent choice

  [12] Mauldin T.C. et al. (2007). "Self-healing kinetics and the stereoisomers
       of dicyclopentadiene." J. R. Soc. Interface, 4(13), 389–393.
       https://doi.org/10.1098/rsif.2006.0200
       → endo-DCPD near solidification at 3°C; exo-DCPD better for low T;
         healing time at 4°C orders of magnitude slower than room temp

  [13] Afrinaldi L.A.T.W. et al. (2023). "Self-healing polymers designed for
       underwater applications." Advances in Polymer Technology, 6614326.
       https://doi.org/10.1155/2023/6614326
       → Polymerisation rates drop 60% in saline vs lab; comprehensive
         underwater challenge review

  [14] PHMSA (2025). Hazardous Liquid Incident Flagged Files (2010–Present).
       U.S. Department of Transportation.
       https://www.phmsa.dot.gov/data-and-statistics/pipeline/pipeline-incident-flagged-files
       → N = 5,890 real pipeline incidents; validation dataset

  [15] Hamilton A.R., Sottos N.R. & White S.R. (2012). "Pressurized vascular
       systems for self-healing materials." J. R. Soc. Interface, 9(70),
       1020–1028. https://doi.org/10.1098/rsif.2011.0875
       → Pressurised PTFE vascular channels at elevated pressure; maps to
         Layer 5 PTFE channel network in deep-sea application

================================================================================
  HOW TO RUN:
    python pipeline_7layer_simulation.py          → all 10 figures
    python pipeline_7layer_simulation.py --figs 1 2 3  → specific figures
    python pipeline_7layer_simulation.py --no-phmsa    → skip PHMSA validation
================================================================================
"""
from .cli import main

__all__ = ["main"]
