# Deep-Sea Pipeline: Pinhole Leak Detection and Self-Healing Simulation

> A Physics-Grounded Academic Simulation of a 7-Layer Smart Pipeline featuring Pinhole Leak Detection, Multi-Sensor Fusion, Hybrid Self-Healing, Machine Learning Sensor Fusion, and Real-World PHMSA Validation.

This project simulates the complete lifecycle of a deep-sea crude oil pipeline incident: pinhole formation, signal detection across multiple sensing layers, autonomous self-healing, and recovery. It combines fluid mechanics, materials science, acoustic sensing theory, and machine learning into a single literature-grounded simulation, with every material and parameter choice traceable to a published source.

The system models a 7-layer pipeline architecture operating at 3,000 m depth, where a 0.5 mm pinhole leak is detected through pressure, acoustic, and distributed fiber sensing, then autonomously sealed using a three-mechanism hybrid healing system, and finally cross-validated against real PHMSA pipeline incident records.

## Repository

**Repository:** deep-sea-pipeline-pinhole-leak-and-self-healing-simulation

## Overview

This simulation was designed to explore how a multi-layer deep-sea pipeline can detect and respond to a sub-millimeter pinhole leak that is otherwise invisible to conventional flow and pressure monitoring. It demonstrates a practical, literature-backed implementation of:

* Deep-Sea Pipeline Physics (pressure, flow, friction)
* Pinhole Leak Detection Below the Sensor Noise Floor
* Multi-Sensor Fusion (Pressure, Acoustic, Distributed Fiber)
* Three-Mechanism Hybrid Self-Healing
* Random Forest Machine Learning Sensor Fusion
* Energy Harvesting and Autonomous Power Management
* Real-World Validation Against PHMSA Incident Data

The project serves as both an academic design simulation and a research platform for studying multi-layer sensing, materials selection, and reinforcement-style adaptive monitoring in extreme environments.

## Key Features

### Pipeline Physics

* Hydrostatic and Internal Pressure Modeling
* Blasius Turbulent Friction Factor
* ISO 5167 Orifice Discharge Flow
* Reynolds Number and Flow Regime Calculation

### Leak Detection

* Pressure Profile and Flow Rate Degradation Modeling
* Sensor Noise Simulation (Gaussian and Tidal Components)
* Quartz and Hydrophone Hybrid Acoustic Detection
* Strouhal Orifice Tone Calculation
* Dual Redundant Fiber Optic Distributed Acoustic Sensing (DAS)

### Self-Healing System

* IPDI@SPUA Chemical Capsule Sealing
* PTFE Pressurized Vascular Network
* Shape Memory Polymer Mechanical Crack Closure
* Two-Phase Healing Kinetics Model

### Machine Learning Sensor Fusion

* Random Forest Classifier Trained on Monte Carlo Scenarios
* Logistic Regression Baseline Comparison
* Stratified 10-Fold Cross-Validation
* Permutation Feature Importance
* Probability Calibration and Brier Score
* Full Incident Lifecycle Decision Timeline

### Power System

* Piezoelectric Energy Harvesting
* Thermoelectric Generator (Seawater-Oil Gradient)
* Li-Thionyl Backup Battery Modeling
* Sapphire Optical Window Transmittance vs Depth

### Validation

* Cross-Validation Against PHMSA Hazardous Liquid Incident Database
* Pressure, Diameter, and Volume Loss Percentile Benchmarking
* IEEE-Style Validation Summary Report

## Technology Stack

| Layer                   | Technology                              |
| ------------------------ | ---------------------------------------- |
| Programming Language     | Python 3                                 |
| Numerical Computing      | NumPy                                    |
| Data Handling            | Pandas                                   |
| Statistical Modeling     | SciPy (stats)                            |
| Machine Learning         | scikit-learn (Random Forest, Logistic Regression) |
| Visualization            | Matplotlib                               |
| Validation Dataset       | PHMSA Hazardous Liquid Incident Database |
| Execution Interface      | Command-Line (argparse)                  |
| Version Control          | Git & GitHub                             |

## System Architecture

```text
                         +------------------------+
                         |   Pipeline Conditions   |
                         |  3,000 m / 297 bar /    |
                         |   crude oil / 2-4 C     |
                         +-----------+-------------+
                                     |
                                     v
                     +--------------------------------+
                     |     7-Layer Pipeline Shell      |
                     |  Foam -> Inconel -> Sensors ->  |
                     |   Healing -> Fiber -> Power      |
                     +---------------+------------------+
                                     |
          +--------------------------+-------------------------+
          |                                                     |
          v                                                     v

+-------------------------+                        +--------------------------+
| Detection Subsystem     |                        | Healing Subsystem        |
| L3 Pressure/Vibration   |                        | L5 IPDI + PTFE + SMP     |
| L4 Acoustic Hybrid      |                        | Two-Phase Kinetics       |
| L6 Dual Fiber DAS       |                        |                          |
+-------------------------+                        +--------------------------+
          |                                                     |
          +--------------------------+-------------------------+
                                     |
                                     v
                     +--------------------------------+
                     |  Random Forest Sensor Fusion    |
                     |     (Module 7 Digital Twin)      |
                     +---------------+------------------+
                                     |
                                     v
                     +--------------------------------+
                     |     PHMSA Real-World Validation  |
                     +--------------------------------+
```

### Layer Architecture

| Layer | Material / Technology                  | Main Function                       | Survival Rate |
| ----- | --------------------------------------- | ------------------------------------ | -------------- |
| 1     | UE44/TMA Syntactic Foam + Basalt Fiber  | Pressure damping, buoyancy, insulation | 97-98%        |
| 2     | Inconel 625 Structural Shell            | Structural strength, corrosion resistance | 99%        |
| 3     | PMN-PT + Floating Ceramic Shock Mount   | Pressure and vibration sensing       | 99%            |
| 4     | Quartz + Hydrophone Hybrid              | Acoustic crack and leak detection    | 98%            |
| 5     | Hybrid Healing System                   | Self-healing crack repair            | 99%            |
| 6     | Dual Redundant Fiber Optics             | Data communication and monitoring    | 98%            |
| 7     | Hybrid Power Layer                      | Energy harvesting and backup power   | 98-99%         |

Construction proceeds outside to inside in four steps: Environmental Shielding (Layer 1), Structural Backbone and Senses (Layers 2-3), Internal Protection and Self-Repair (Layers 4-5), and Central Core and Intelligence (Layers 6-7).

## Why Not DCPD and Grubbs Catalyst

The classic White et al. (2001) DCPD plus Grubbs catalyst self-healing system is not used in this simulation, for reasons grounded in subsequent literature:

* Grubbs catalyst is deactivated by seawater moisture and chloride ions, and endo-DCPD sits near its melting point at deep-sea temperatures, preventing the ring-opening polymerization from completing (Mauldin et al., 2007).
* Saline conditions reduce polymerization rate by approximately 60 percent relative to lab conditions (Afrinaldi et al., 2023).
* Deep-sea pressure causes premature capsule rupture in the original formulation (Zeng et al., 2025).

Instead, Layer 5 uses an IPDI (isocyanate) and FBE (Fusion Bonded Epoxy) system, where IPDI reacts with seawater itself as a co-reactant to form polyurea, FBE cures reliably at 4 degrees Celsius, and the combination has been validated at 150 bar immersion for over 1,000 hours.

## Operating Conditions

| Parameter         | Value                  |
| ------------------ | ----------------------- |
| Depth              | 3,000 m                 |
| External Pressure  | Approximately 297 bar   |
| Temperature        | 2-4 degrees Celsius     |
| Fluid              | Crude oil (850 kg/m3)   |
| Pipeline           | 50 km length, 0.5 m diameter |
| Internal Pressure  | 100-150 bar              |
| Pinhole            | 0.5 mm diameter at 20 km from inlet |

## Self-Healing Pipeline

### Current Workflow

1. Pinhole forms at a point along the pipeline under internal pressure.
2. Pressure and flow signals degrade by a fraction of a percent, well below the sensor noise floor.
3. Layer 3 PMN-PT sensors continuously monitor bulk wall pressure and vibration.
4. Layer 4 Quartz and Hydrophone Hybrid sensors detect the orifice acoustic tone.
5. Layer 6 Dual Redundant Fiber DAS detects distributed vibration along the pipeline.
6. A Random Forest sensor fusion model combines all signals into a leak probability estimate.
7. Layer 5 Hybrid Healing System activates: IPDI@SPUA capsules seal the crack chemically within seconds.
8. PTFE vascular network and shape memory polymer matrix consolidate the seal over several minutes.
9. Pressure and flow signals recover to baseline.
10. The incident is logged and benchmarked against real-world PHMSA pipeline data.

## Hybrid Healing System Model

Layer 5 combines three complementary repair mechanisms.

Mechanism A, IPDI@SPUA chemical capsules, ruptures under deep-sea pressure and reacts with seawater to form polyurea, contributing 55-75 percent sealing efficiency on its own.

Mechanism B, a pressurized PTFE vascular network, delivers sealing fluid continuously over a longer time window, governed by a vascular rate constant of 0.05 per minute.

Mechanism C, a shape memory polymer matrix, mechanically closes microcracks through elastic recovery driven by the temperature difference between crude oil and seawater, adding 5-10 percent efficiency.

Combined, the hybrid system reaches 60-80 percent healing efficiency in realistic deep-sea conditions.

### Two-Phase Simulation Model

```text
Phase 1 (0-60 s)   IPDI@SPUA + SMP sealing
cf(t) = 1 - eta * (1 - exp(-(t - t_onset) / tau_fill))

Phase 2 (60 s - 10 min)   PTFE vascular + SMP recovery
cf(t) = A0 * exp(-k * (t - 60) / 60),  k = 0.05 / min
```

## Machine Learning Sensor Fusion

A Random Forest classifier fuses fifteen features drawn from Layers 3, 4, and 6 (pressure statistics, acoustic FFT features, and distributed acoustic sensing spatial features) into a single leak probability. The model is evaluated using stratified 10-fold cross-validation, compared against a Logistic Regression baseline, and assessed with permutation importance and calibration analysis rather than relying on a single train-test split. A full incident-lifecycle decision timeline traces the predicted leak probability from normal operation through leak onset, detection, healing, and recovery.

## Database and Validation Design

### PHMSA Validation Dataset

| Column                       | Description                       |
| ------------------------------ | ----------------------------------- |
| LEAK_TYPE                      | Type of pipeline failure (e.g. pinhole) |
| COMMODITY_RELEASED_TYPE        | Substance released                |
| ACCIDENT_PSIG                  | Operating pressure at incident    |
| PIPE_DIAMETER                  | Pipe diameter in inches           |
| UNINTENTIONAL_RELEASE_BBLS     | Volume released, in barrels       |
| EST_COST_ENVIRONMENTAL         | Estimated environmental cost      |
| EST_COST_PROP_DAMAGE           | Estimated property damage cost    |
| ON_OFF_SHORE                   | Offshore or onshore classification |
| IYEAR                          | Incident year                     |

Simulation parameters (pipe diameter, operating pressure, pinhole prevalence, and volume loss with and without healing) are benchmarked against this dataset's empirical distribution to confirm the simulation sits within realistic real-world ranges.

## Repository Structure

```text
deep-sea-pipeline-pinhole-leak-and-self-healing-simulation/
│
├── src/
│   ├── __init__.py
│   └── deepsea_pipeline_leak_simulation.py
├── .gitignore
├── main.py
├── phmsa_clean.csv
└── README.md
```

Note: the simulation reads `phmsa_clean.csv` from the current working directory at runtime (`PHMSA_PATH = os.path.join(os.getcwd(), "phmsa_clean.csv")`). This file should be kept at the repository root alongside `main.py`, not inside `src/`, since the script is intended to be run from the project root.

## Installation

### Setup

```bash
cd deep-sea-pipeline-pinhole-leak-and-self-healing-simulation

pip install numpy pandas scipy matplotlib scikit-learn
```

### Run the Full Simulation

```bash
python main.py
```

This generates all 11 figures and saves them to the `outputs/` directory.

### Run Specific Figures

```bash
python main.py --figs 1 2 3
```

### Skip PHMSA Validation

```bash
python main.py --no-phmsa
```

PHMSA validation figures (8, 9, and 10) require `phmsa_clean.csv` to be present at the project root. If the file is missing, the script will print a download link and skip those figures automatically.

## Output Figures

| Figure | Content                                              |
| ------ | ------------------------------------------------------ |
| 1      | Pressure profile and flow rate, showing the leak signal buried in sensor noise |
| 2      | Layer 3, 4, and 6 sensor signal comparison across three pipeline states |
| 3      | Layer 5 hybrid self-healing response over time         |
| 4      | Seven-layer cross-section schematic                    |
| 5      | Dual fiber redundancy and Layer 7 power system          |
| 6      | Structural and environmental property validation        |
| 7      | Performance summary dashboard                           |
| 8      | PHMSA real-world incident landscape                      |
| 9      | Quantitative validation against PHMSA data               |
| 10     | IEEE-style validation summary dashboard                  |
| 11     | Random Forest sensor fusion and digital twin intelligence |

## Project Evolution

### Initial Development

* Pipeline Physics Parameters and Geometry
* Pressure and Flow Equations (Blasius, ISO 5167)
* Layer Architecture Definition

### Detection Modeling

* Sensor Noise Simulation
* Quartz and Hydrophone Hybrid Acoustic Modeling
* Dual Redundant Fiber DAS Modeling

### Self-Healing System

* Initial Single-Agent DCPD Model (deprecated)
* Literature Review of Deep-Sea Healing Failure Modes
* Hybrid IPDI, PTFE, and SMP Three-Mechanism Model

### Machine Learning Integration

* Monte Carlo Scenario Generation
* Random Forest and Logistic Regression Training
* Cross-Validation and Calibration Analysis
* Full Incident Lifecycle Decision Timeline

### Real-World Validation

* PHMSA Dataset Integration
* Percentile Benchmarking of Simulation Parameters
* IEEE-Style Validation Report Generation

## Notable Milestones

* Full Seven-Layer Pipeline Architecture Simulation
* Literature-Grounded Healing Agent Replacement (DCPD to IPDI)
* Multi-Sensor Fusion Across Pressure, Acoustic, and Fiber Modalities
* Random Forest Digital Twin for Leak Probability Estimation
* Cross-Validation Against 5,890 Real PHMSA Pipeline Incidents
* Automated Figure Generation Pipeline (11 Figures)

## Research Applications

This project can be used to study:

* Deep-Sea Pipeline Engineering
* Multi-Sensor Fusion for Structural Health Monitoring
* Self-Healing Materials Under Extreme Pressure
* Machine Learning for Predictive Maintenance
* Reliability Engineering and System Survival Modeling
* Validation of Simulation Models Against Empirical Incident Data

## References

Every material choice, healing agent, sensing principle, and physical constant in this simulation is grounded in a cited source. The full bibliography, as maintained in the project docstring, is reproduced below.

1. White, S. R. et al. (2001). Autonomic healing of polymer composites. *Nature*, 409(6822), 794-797. Original microcapsule self-healing concept under lab (dry) conditions; used as the baseline benchmark this simulation improves upon for deep-sea use.

2. Toohey, K. S. et al. (2007). Self-healing materials with microvascular networks. *Nature Materials*, 6(8), 581-585. Source of the vascular network rate constant (k = 0.05 per minute) used in the Layer 5 Phase 2 healing model.

3. Kessler, M. R. and White, S. R. (2001). Self-activated healing of delamination damage in woven composites. *Composites Part A*, 32(5), 683-699. Epoxy capsule characterization and mechanical recovery data informing the chemical sealing phase.

4. Bao, X. and Chen, L. (2012). Recent progress in distributed fiber optic sensors. *Sensors*, 12(7), 8601-8639. Basis for the Layer 6 distributed acoustic sensing (DAS) and BOTDR pipeline leak detection principles, including the under-30-second detection time benchmark.

5. Wenz, G. M. (1962). Acoustic ambient noise in the ocean: Spectra and sources. *Journal of the Acoustical Society of America*, 34(12), 1936-1956. Source of the ocean ambient noise floor (120 dB re 1 microPa) used to calibrate hydrophone noise in Layer 4 and Module 7.

6. ISO 5167:2003. Measurement of fluid flow by means of pressure differential devices. International Organization for Standardization. Source of the orifice discharge coefficient (Cd = 0.61) used throughout the leak flow rate calculations.

7. Blasius, H. (1913). Das Ahnlichkeitsgesetz bei Reibungsvorgangen in Flussigkeiten. *Forschungsarbeiten VDI*, 131, 1-40. Source of the turbulent friction factor correlation (f = 0.316 / Re^0.25) used in the pipeline flow model.

8. Munson, B. R., Young, D. F., and Okiishi, T. H. (2006). *Fundamentals of Fluid Mechanics*, 5th ed. John Wiley and Sons. Source of the Darcy-Weisbach pressure drop relation, orifice flow derivation, and the Strouhal number (St = 0.2) used for the orifice vortex shedding tone calculation.

9. American Petroleum Institute. API MPMS (Manual of Petroleum Measurement Standards). Washington, D.C. Source of crude oil density (850 kg/m3) and viscosity (0.015 Pa.s at approximately 4 degrees Celsius) used in the physics module.

10. Zeng, X. et al. (2025). Self-healing performance and anti-corrosion mechanism of microcapsule-containing epoxy coatings under deep-sea environment. *Progress in Organic Coatings*, 202, 109108. The key deep-sea validation source: IPDI@SPUA capsules tested at 15 MPa seawater pressure, showing pressure promotes (rather than prevents) capsule rupture, with impedance maintained after 1,008 hours of immersion. This is the primary justification for replacing DCPD with IPDI in Layer 5.

11. Feng, H. et al. (2020). Fabrication of microcapsule-type composites with the capability of underwater self-healing and damage visualization. *RSC Advances*, 10(56), 33675-33682. Reports 85.6 percent underwater healing efficiency using water-activated amine curing agents, validating the broader choice of water-reactive (rather than water-sensitive) healing chemistry.

12. Mauldin, T. C. et al. (2007). Self-healing kinetics and the stereoisomers of dicyclopentadiene. *Journal of the Royal Society Interface*, 4(13), 389-393. Shows endo-DCPD sits near its solidification point at 3 degrees Celsius and that healing time at this temperature is orders of magnitude slower than at room temperature, the primary literature basis for excluding DCPD plus Grubbs catalyst from this design.

13. Afrinaldi, L. A. T. W. et al. (2023). Self-healing polymers designed for underwater applications. *Advances in Polymer Technology*, 2023, 6614326. Reports a 60 percent reduction in polymerization rate under saline conditions relative to lab conditions; used to derive the realistic 55-75 percent deep-sea healing efficiency range for the IPDI agent (down from the 70-90 percent lab values reported by White, 2001).

14. U.S. Department of Transportation, Pipeline and Hazardous Materials Safety Administration (PHMSA) (2025). Hazardous Liquid Incident Flagged Files (2010-Present). The real-world validation dataset (N = 5,890 incidents) used in Figures 8 through 10 and the IEEE-style validation report to benchmark simulated pipe diameter, operating pressure, leak type prevalence, and volume loss against empirical incident records.

15. Hamilton, A. R., Sottos, N. R., and White, S. R. (2012). Pressurized vascular systems for self-healing materials. *Journal of the Royal Society Interface*, 9(70), 1020-1028. Source for pressurized PTFE vascular channel behavior at elevated pressure, mapped directly to the Layer 5 PTFE channel network used in this simulation's deep-sea application.
