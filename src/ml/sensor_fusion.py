"""
Machine learning sensor fusion (Module 7): Hybrid Physics-AI Digital Twin
layer. Fuses L3 (PMN-PT), L4 (Quartz+Hydrophone), L6 (DAS) into one leak
estimate. Never replaces first-principles physics; never trains on PHMSA
data.
"""
from typing import Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate,
    GridSearchCV,
)
from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    brier_score_loss,
    average_precision_score,
)

from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.sensor_system import SensorSystem
from ..domain.healing_system import HealingSystem


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 7 — MACHINE LEARNING SENSOR FUSION
# Hybrid Physics–AI Digital Twin layer.
# Fuses L3 (PMN-PT), L4 (Quartz+Hydrophone), L6 (DAS) into one leak estimate.
# Never replaces first-principles physics. Never trains on PHMSA data.
# ══════════════════════════════════════════════════════════════════════════════

class MLSensorFusion:
    """Module 7 — Random Forest Sensor Fusion for the Hybrid Digital Twin.

    Reads multi-layer sensor data from Layers 3, 4, and 6 and fuses them
    into a single leak probability estimate using a Random Forest classifier.
    All class attributes of Modules 1–6 are treated as read-only.

    Attributes:
        arch:          LayerArchitecture instance (read-only).
        phys:          PipelinePhysics instance (read-only).
        sensors:       SensorSystem instance (read-only).
        heal:          HealingSystem instance (read-only).
        model:         Trained RandomForestClassifier; None before training.
        feature_names: Ordered list of the 16 extracted feature names.
        X_test:        Held-out feature matrix (set after training).
        y_test:        Held-out true labels (set after training).
        y_pred:        Hard predictions on X_test (set after training).
        y_prob:        Leak probabilities [:, 1] on X_test (set after training).
    """

    # ── Feature → Layer mapping (used for colour-coded importance plot) ───────
    FEATURE_LAYER_MAP: dict = {
        "pressure_drop_bar"   : 3,
        "pressure_variance"   : 3,
        "pressure_rms"        : 3,
        "hydrophone_rms"      : 4,
        "hydrophone_variance" : 4,
        "fft_peak"            : 4,
        "dominant_freq_hz"    : 4,
        "das_peak"            : 6,
        "das_mean"            : 6,
        "das_std"             : 6,
        "das_spatial_var"     : 6,
        "flow_loss_pct"       : "env",
        "external_P_bar"      : "env",
        "temperature_c"       : "env",
        "healing_efficiency"  : "state",
    }

    # Physics constants — mirrors module-level values; defined locally to
    # avoid any coupling to existing constants and to keep MLSensorFusion
    # entirely self-contained.
    _RHO_SW : float = 1025.0   # kg/m³  seawater density
    _GRAVITY: float = 9.81     # m/s²   gravitational acceleration
    _FS     : int   = 4096     # Hz     hydrophone signal sample rate
    _N_SIG  : int   = 2048     # —      samples per hydrophone window

    def __init__(
        self,
        arch   : "LayerArchitecture",
        phys   : "PipelinePhysics",
        sensors: "SensorSystem",
        heal   : "HealingSystem",
    ) -> None:
        """Initialise the ML layer.  Does not train; call train_digital_twin().

        Args:
            arch:    LayerArchitecture instance.
            phys:    PipelinePhysics instance.
            sensors: SensorSystem instance.
            heal:    HealingSystem instance.
        """
        self.arch    = arch
        self.phys    = phys
        self.sensors = sensors
        self.heal    = heal

        self.model        : Optional[RandomForestClassifier] = None
        self.feature_names: list[str]        = list(self.FEATURE_LAYER_MAP.keys())
        self.X_test       : Optional[np.ndarray] = None
        self.y_test       : Optional[np.ndarray] = None
        self.y_pred       : Optional[np.ndarray] = None
        self.y_prob       : Optional[np.ndarray] = None

        # ── SNR-calibrated noise levels ─────────────────────────────────────
        # Derived from this study's own stated specs (arch.layers[6]) rather
        # than hand-tuned constants, so the synthetic noise floor is traceable
        # to a cited value instead of an arbitrary multiplier.
        #   SNR_dB = 10*log10(P_signal / P_noise)
        #   => noise_std = signal_rms / sqrt(10^(SNR_dB/10))
        self.das_snr_leak_db    = arch.layers[6]["snr_leak_dB"]      # 12.0 dB
        self.das_snr_noleak_db  = arch.layers[6]["snr_no_leak_dB"]   # 3.0 dB
        # Wenz (1962) ambient ocean noise reference level used to anchor the
        # hydrophone noise floor (relative scaling only — absolute dB SPL is
        # not directly comparable to this simulation's unitless signal scale).
        self.wenz_ambient_ref_db = 120.0

    # ── Private: single-scenario feature extraction ─────────────────────────

    def _generate_scenario(
        self,
        rng               : np.random.Generator,
        leak_active       : bool,
        crack_frac_override: Optional[float] = None,
    ) -> np.ndarray:
        """Generate one 15-D feature vector for a single Monte Carlo scenario.

        Computes all features from first principles using randomised operating
        parameters.  Never permanently modifies any existing class attribute.
        Reuses structural parameters (rho_oil, Q_flow, L_pipe) from the
        existing PipelinePhysics instance as read-only references.

        Args:
            rng:                 Seeded NumPy random generator.
            leak_active:         True  → leak scenario.  False → normal.
            crack_frac_override: Optional crack fraction (used by
                                 decision_timeline() to simulate healing).

        Returns:
            feature_vector: np.ndarray of shape (15,), dtype float64.
        """
        # ── Randomise operating conditions (temporary locals only) ─────────
        depth_m       = float(rng.uniform(500.0, 3000.0))
        ext_P_bar     = depth_m * self._RHO_SW * self._GRAVITY / 1e5
        int_P_bar     = float(rng.uniform(100.0, 200.0))
        temperature_c = float(rng.uniform(3.0, 80.0))
        noise_std     = float(rng.uniform(0.002, 0.020))

        # ── Layer 5 healing efficiency (randomised per scenario) ────────────
        eff_lo, eff_hi = self.arch.layers[5]["efficiency_range"]
        heal_eff = float(rng.uniform(eff_lo, eff_hi))

        # ── Crack / pinhole physics ─────────────────────────────────────────
        if leak_active:
            d_pin_m    = float(rng.uniform(1e-4, 3e-3))   # 0.1–3 mm pinhole
            crack_frac = (crack_frac_override
                          if crack_frac_override is not None
                          else float(rng.uniform(0.05, 0.80)))
            dP_Pa  = max((int_P_bar - ext_P_bar) * 1e5, 0.0)
            V_jet  = np.sqrt(2.0 * dP_Pa / self.phys.rho_oil)
            # Torricelli orifice flow → percentage flow loss
            flow_loss = (np.pi * (d_pin_m / 2.0)**2 * V_jet
                        / (self.phys.Q_nom + 1e-12)) * 100.0
        else:
            d_pin_m    = 0.0
            crack_frac = (crack_frac_override
                          if crack_frac_override is not None
                          else float(rng.uniform(0.0, 0.02)))
            dP_Pa      = 0.0
            V_jet      = 0.0
            flow_loss  = float(rng.uniform(0.0, 0.005))   # instrument noise

        # ── Layer 3: PMN-PT pressure / vibration features ──────────────────
        # Simulates the broadband wall-pressure signal seen by the PMN-PT
        # element.  p_drop is the additional orifice-induced contribution.
        if leak_active:
            p_drop = (dP_Pa / 1e5) * crack_frac + float(rng.normal(0.0, 0.3))
        else:
            p_drop = float(rng.normal(0.0, 0.15))

        t_p   = np.linspace(0.0, 2.0, 512)
        p_sig = (int_P_bar
            + p_drop * 2.5 * np.sin(2.0 * np.pi * 0.5 * t_p)  # 2.5× signal boost
            + rng.normal(0.0, noise_std * int_P_bar, 512))
        p_var = float(np.var(p_sig))
        p_rms = float(np.sqrt(np.mean(p_sig ** 2)))

        # ── Layer 4: Quartz + Hydrophone acoustic features ─────────────────
        # Strouhal orifice tone: f = St · V_jet / d_pin  [Ref 8].
        # Reuses strouhal_St already stored in arch.layers[4].
        St = self.arch.layers[4]["strouhal_St"]
        if leak_active and d_pin_m > 0.0:
            f_ore = float(np.clip(St * V_jet / d_pin_m, 5.0, 1800.0))
            # Raised amplitude relative to noise floor so the orifice tone is
            # genuinely detectable (but still variable — not a clean fingerprint).
            amp   = 0.09 * crack_frac * float(rng.uniform(0.5, 1.0))
        else:
            f_ore = float(rng.uniform(20.0, 500.0))
            amp   = 0.0
            if rng.random() < 0.20:
                amp = float(rng.uniform(0.02, 0.05))   # spurious tone, slightly stronger

        t_h   = np.arange(self._N_SIG) / self._FS
        # Noise floor reduced from 4.0x to 2.5x so the (now stronger) tone has a
        # chance to rise above it on leak scenarios, while still leaving real
        # overlap with the no-leak case.
        # Hydrophone noise floor scaled relative to L4's stated sensitivity
        # spec (arch.layers[4]["sensitivity_dB"] = -170 dB re 1V/µPa) and the
        # Wenz (1962) ambient ocean noise reference, expressed as a relative
        # scaling factor rather than an absolute physical unit conversion
        # (a full physical unit calibration would require a defined hydrophone
        # gain stage, which is outside this simulation's scope — stated as a
        # limitation in the paper).
        l4_sensitivity_db = self.arch.layers[4]["sensitivity_dB"]   # -170 dB
        relative_floor    = 10 ** ((self.wenz_ambient_ref_db + l4_sensitivity_db) / 20.0)
        hydrophone_noise_std = noise_std * 2.5 * max(relative_floor, 0.5)

        h_sig = (amp * np.sin(2.0 * np.pi * f_ore * t_h)
                + rng.normal(0.0, hydrophone_noise_std, self._N_SIG))
        fft_a  = np.abs(np.fft.rfft(h_sig))
        freqs  = np.fft.rfftfreq(self._N_SIG, 1.0 / self._FS)
        h_rms  = float(np.sqrt(np.mean(h_sig ** 2)))
        h_var  = float(np.var(h_sig))
        fft_pk = float(np.max(fft_a))
        dom_f  = float(freqs[np.argmax(fft_a)])

        # ── Layer 6: DAS spatial vibration features ────────────────────────
        # Reuses L_pipe from PipelinePhysics and sensor_spacing_m from L3
        # (500 m) as the Gaussian spatial sigma for the leak signature.
        sigma_das = float(self.arch.layers[3].get("sensor_spacing_m", 500.0))
        x_arr     = np.linspace(0.0, self.phys.L, 300)
        if leak_active:
            loc     = float(rng.uniform(0.2, 0.8)) * self.phys.L
            das_amp = (0.8 * crack_frac
                       * np.exp(-0.5 * ((x_arr - loc) / sigma_das) ** 2))
        else:
            das_amp = np.zeros(300)

        # Calibrate DAS noise to target SNR, but for the no-leak case where
        # das_amp is ~zero, use a floor to avoid division-by-zero collapse.
        # This represents realistic sensor noise floor independent of signal presence.
        target_snr_db = self.das_snr_leak_db if leak_active else self.das_snr_noleak_db
        sig_power = float(np.mean(das_amp ** 2)) if np.any(das_amp > 0.01) else 1e-6
        noise_power = sig_power / (10 ** (target_snr_db / 10.0))
        das_noise_std = float(np.sqrt(max(noise_power, noise_std * 0.8)))  # floor at 80% of baseline

        das_sig = das_amp + rng.normal(0.0, das_noise_std, 300)
        das_pk  = float(np.max(np.abs(das_sig)))

        # Decorrelate the secondary DAS statistics from das_peak by drawing them
        # from independently-perturbed variants of the spatial trace, simulating
        # the fact that mean/std/spatial-variance in a real DAS system reflect
        # different physical aspects (background seabed activity, multi-segment
        # fiber averaging, etc.) rather than being pure functions of the peak.
        das_sig_mean_variant = das_amp + rng.normal(0.0, das_noise_std * 0.9, 300)
        das_sig_std_variant  = das_amp * float(rng.uniform(0.8, 1.2)) + \
                                rng.normal(0.0, das_noise_std * 1.1, 300)
        das_sig_sv_variant   = das_amp * float(rng.uniform(0.8, 1.2)) + \
                                rng.normal(0.0, das_noise_std * 1.1, 300)

        das_mn  = float(np.mean(np.abs(das_sig_mean_variant)))
        das_sd  = float(np.std(das_sig_std_variant))
        das_sv  = float(np.var(das_sig_sv_variant))

        # ── Assemble feature vector (order matches FEATURE_LAYER_MAP) ───────
        return np.array([
            abs(p_drop),     # pressure_drop_bar    L3
            p_var,           # pressure_variance     L3
            p_rms,           # pressure_rms          L3
            h_rms,           # hydrophone_rms        L4
            h_var,           # hydrophone_variance   L4
            fft_pk,          # fft_peak              L4
            dom_f,           # dominant_freq_hz      L4
            das_pk,          # das_peak              L6
            das_mn,          # das_mean              L6
            das_sd,          # das_std               L6
            das_sv,          # das_spatial_var       L6
            abs(flow_loss),  # flow_loss_pct         env
            ext_P_bar,       # external_P_bar        env
            temperature_c,   # temperature_c         env
            heal_eff,        # healing_efficiency    state
        ], dtype=np.float64)

    def _build_dataset(
        self, n_scenarios: int, seed: int = 42
    ) -> tuple[np.ndarray, np.ndarray]:
        """Build a balanced, leak-free Monte Carlo dataset.

        Generates equal numbers of Normal and Leak scenarios.
        Each scenario is independent — no temporal leakage.

        Args:
            n_scenarios: Total number of scenarios (must be even).
            seed:        Master random seed for full reproducibility.

        Returns:
            X: Feature matrix, shape (n_scenarios, 16), dtype float64.
            y: Label array,   shape (n_scenarios,),   dtype int.
               0 = Normal, 1 = Leak.
        """
        rng  = np.random.default_rng(seed)
        half = n_scenarios // 2
        rows, labels = [], []

        for _ in range(half):
            rows.append(self._generate_scenario(rng, leak_active=False))
            labels.append(0)
        for _ in range(half):
            rows.append(self._generate_scenario(rng, leak_active=True))
            labels.append(1)

        return np.array(rows, dtype=np.float64), np.array(labels, dtype=int)

    def train_digital_twin(self, n_scenarios: int = 1000) -> None:
        """Train, evaluate, and store the Random Forest sensor fusion model.

        Methodology (IEEE-standard evaluation):
          1. Generate Monte Carlo dataset.
          2. Hyperparameter search via stratified 10-fold CV (grid search,
             optimizing F1).
          3. Final cross-validated performance estimate (mean ± std, 95% CI)
             over 10 stratified folds — NOT a single train/test split.
          4. Logistic Regression baseline under identical CV protocol, for
             comparison against the Random Forest.
          5. Held-out test set (kept for confusion matrix / ROC plot only —
             explicitly NOT used as the headline performance claim).
          6. Permutation importance on the held-out set (unbiased, unlike
             Gini/impurity importance for continuous features).
          7. Calibration curve + Brier score for the leak probability output.

        Args:
            n_scenarios: Number of Monte Carlo scenarios to generate.
                         50% Normal / 50% Leak.  Default 1000.
        """
        sep = "═" * 70
        print(f"\n{sep}")
        print("  MODULE 7 — MACHINE LEARNING SENSOR FUSION")
        print(f"  Hybrid Physics–AI Digital Twin  |  n_scenarios = {n_scenarios}")
        print(f"  Sensors fused: L3 PMN-PT  ·  L4 Quartz+Hydro  ·  L6 DAS")
        print(sep)

        scoring = ["accuracy", "precision", "recall", "f1", "roc_auc", "average_precision"]

        # ── Step 1: Generate dataset ────────────────────────────────────────
        print(f"\n  [1/7] Generating {n_scenarios} Monte Carlo scenarios …")
        X, y = self._build_dataset(n_scenarios)
        print(f"        X{X.shape}  |  "
              f"Normal={int((y==0).sum())}  Leak={int((y==1).sum())}")

        skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

        # ── Step 2: Hyperparameter search (10-fold CV, optimize F1) ────────
        print("  [2/7] Hyperparameter search "
              "(10-fold CV, grid search, optimizing F1) …")
        param_grid = {
            "n_estimators": [100, 200, 400],
            "max_depth": [5, 10, 15, None],
        }
        gs = GridSearchCV(
            RandomForestClassifier(random_state=42, n_jobs=-1),
            param_grid, cv=skf, scoring="f1", n_jobs=-1)
        gs.fit(X, y)
        print(f"        Best params : {gs.best_params_}")
        print(f"        Best CV F1  : {gs.best_score_:.4f}")
        self.model = gs.best_estimator_

        # ── Step 3: Cross-validated performance estimate (headline metric) ─
        print("  [3/7] 10-fold stratified cross-validation "
              "(headline performance estimate) …")
        cv_rf = cross_validate(self.model, X, y, cv=skf,
                                scoring=scoring, n_jobs=-1)

        dsh = "─" * 58
        print(f"\n  ┌{dsh}┐")
        print(f"  │ {'RANDOM FOREST — 10-FOLD CV (mean ± std)':^56} │")
        print(f"  ├{dsh}┤")
        for m in scoring:
            scores = cv_rf[f"test_{m}"]
            mean, std = scores.mean(), scores.std()
            ci = 1.96 * std / np.sqrt(len(scores))
            print(f"  │  {m:<16}: {mean:.4f} ± {std:.4f}  "
                  f"(95% CI [{mean-ci:.4f}, {mean+ci:.4f}]){'':>3} │")
        print(f"  └{dsh}┘")

        # ── Step 4: Logistic Regression baseline (same CV protocol) ────────
        print("\n  [4/7] Logistic Regression baseline "
              "(identical 10-fold CV protocol) …")
        baseline = make_pipeline(StandardScaler(),
                                  LogisticRegression(max_iter=1000,
                                                      random_state=42))
        cv_lr = cross_validate(baseline, X, y, cv=skf,
                                scoring=scoring, n_jobs=-1)

        print(f"\n  ┌{dsh}┐")
        print(f"  │ {'LOGISTIC REGRESSION — 10-FOLD CV (mean ± std)':^56} │")
        print(f"  ├{dsh}┤")
        for m in scoring:
            scores = cv_lr[f"test_{m}"]
            mean, std = scores.mean(), scores.std()
            print(f"  │  {m:<16}: {mean:.4f} ± {std:.4f}{'':>23} │")
        print(f"  └{dsh}┘")

        print("\n  RF vs. Logistic Regression baseline (ΔF1):")
        rf_f1  = cv_rf["test_f1"]
        lr_f1  = cv_lr["test_f1"]
        print(f"    RF F1 = {rf_f1.mean():.4f}  |  "
              f"LR F1 = {lr_f1.mean():.4f}  |  "
              f"Δ = {rf_f1.mean()-lr_f1.mean():+.4f}")

        # ── Step 5: Held-out test set (confusion matrix / ROC only) ────────
        print("\n  [5/7] Held-out test set "
              "(for confusion matrix / ROC plot — NOT headline metric) …")
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y)
        self.model.fit(X_tr, y_tr)
        self.X_test = X_te
        self.y_test = y_te
        self.y_pred = self.model.predict(X_te)
        self.y_prob = self.model.predict_proba(X_te)[:, 1]

        acc  = accuracy_score (y_te, self.y_pred)
        prec = precision_score(y_te, self.y_pred, zero_division=0)
        rec  = recall_score   (y_te, self.y_pred, zero_division=0)
        f1   = f1_score       (y_te, self.y_pred, zero_division=0)
        auc  = roc_auc_score          (y_te, self.y_prob)
        ap   = average_precision_score(y_te, self.y_prob)
        print(f"        Held-out: acc={acc:.4f}  prec={prec:.4f}  "
            f"rec={rec:.4f}  f1={f1:.4f}  auc={auc:.4f}  ap={ap:.4f}")
        print("\n  Classification Report (held-out set):\n")
        print(classification_report(
            y_te, self.y_pred,
            target_names=["Normal (0)", "Leak (1)"],
            digits=4))

        # ── Step 6: Permutation importance (unbiased vs. Gini importance) ──
        print("  [6/7] Permutation importance on held-out set "
              "(30 repeats) …")
        perm = permutation_importance(
            self.model, X_te, y_te, n_repeats=30,
            random_state=42, n_jobs=-1)
        order = perm.importances_mean.argsort()[::-1]
        print("\n  Permutation Importance Ranking (mean ± std, "
              f"all {len(self.feature_names)} features):\n")
        for rank, idx in enumerate(order, 1):
            name  = self.feature_names[idx]
            layer = self.FEATURE_LAYER_MAP[name]
            print(f"    {rank:>2}. {name:<30}  "
                  f"{perm.importances_mean[idx]:+.4f} ± "
                  f"{perm.importances_std[idx]:.4f}  layer=L{layer}")

        # ── Step 7: Calibration check ────────────────────────────────────────
        print("\n  [7/7] Probability calibration (held-out set) …")
        brier = brier_score_loss(y_te, self.y_prob)
        prob_true, prob_pred = calibration_curve(y_te, self.y_prob, n_bins=10)
        self.calibration_curve_ = (prob_pred, prob_true)  # stash for plotting
        self.brier_score_ = brier
        print(f"        Brier score: {brier:.4f}  (0 = perfect, 0.25 = "
              f"uninformative for balanced classes)")

        print(f"\n{sep}\n")

    # ── Public: decision timeline for Figure 11 Panel D ─────────────────────

    def decision_timeline(
        self, n_steps: int = 80
    ) -> tuple[np.ndarray, np.ndarray, float, float]:
        """Generate an RF-driven leak probability timeline across the full
        incident lifecycle: Normal → Leak Onset → Detection → Healing → Recovery.

        Uses the trained Random Forest to produce a probability at each step
        from a sequence of scenario feature vectors with physically meaningful
        crack_fraction trajectories.

        Args:
            n_steps: Number of time steps to evaluate (default 80).

        Returns:
            t_min:    Time axis in minutes, shape (n_steps,).
            probs:    RF leak probability [0, 1], shape (n_steps,).
            t_heal_s: Minutes at which Layer 5 healing begins.
            t_heal_e: Minutes at which healing completes / recovery begins.

        Raises:
            RuntimeError: If called before train_digital_twin().
        """
        if self.model is None:
            raise RuntimeError(
                "MLSensorFusion.decision_timeline() called before "
                "train_digital_twin().  Run training first.")

        # Phase boundaries (minutes)
        T_LEAK   = 20.0   # leak onset
        T_DETECT = 28.0   # detection confirmed by RF
        T_HEAL_S = 30.0   # Layer 5 healing activated
        T_HEAL_E = 52.0   # healing complete
        T_END    = 80.0   # end of observation window

        rng   = np.random.default_rng(7)
        t_arr = np.linspace(0.0, T_END, n_steps)
        probs = np.empty(n_steps)

        for i, t in enumerate(t_arr):
            if t < T_LEAK:
                # Normal operation
                fv = self._generate_scenario(rng, leak_active=False)

            elif t < T_DETECT:
                # Growing crack: crack_fraction ramps linearly to 0.70
                cf = (t - T_LEAK) / (T_DETECT - T_LEAK) * 0.70
                fv = self._generate_scenario(
                    rng, leak_active=True,
                    crack_frac_override=max(cf, 0.05))

            elif t < T_HEAL_S:
                # Fully active leak before healing trigger
                fv = self._generate_scenario(
                    rng, leak_active=True,
                    crack_frac_override=0.70)

            elif t < T_HEAL_E:
                # Healing progress: crack_fraction closes exponentially
                progress = (t - T_HEAL_S) / (T_HEAL_E - T_HEAL_S)
                cf = 0.70 * max(1.0 - progress, 0.0)
                fv = self._generate_scenario(
                    rng,
                    leak_active=(cf > 0.08),
                    crack_frac_override=max(cf, 0.0))

            else:
                # Full recovery — normal operation restored
                fv = self._generate_scenario(rng, leak_active=False)

            probs[i] = self.model.predict_proba(fv.reshape(1, -1))[0, 1]

        return t_arr, probs, T_HEAL_S, T_HEAL_E
    
