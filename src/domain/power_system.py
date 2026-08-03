"""Power system (Module 6): Layer 7 hybrid power / energy-harvesting model."""
import numpy as np

from .layer_architecture import LayerArchitecture


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 6 — LAYER 7 POWER SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
class PowerSystem:
    """
    Layer 7: Hybrid Power Layer — energy harvesting + Li-Thionyl backup.

    Three-source architecture:
      A) Piezoelectric harvester (PMN-PT wafers): ~50 mW from flow vibrations
      B) Thermoelectric Generator (Bi₂Te₃ TEG):  ~150 mW from oil/seawater ΔT
      C) Li-Thionyl backup battery (Li-SOCl₂):   5,000 Wh, <1%/yr discharge
         Rated −60 to +85°C — proven in Argo floats, deep-sea landers, AUVs.

    Sapphire (Al₂O₃) optical window retained: Mohs 9, rated 6,000 m+,
    85% optical transmittance — through-wall optical monitoring port.

    Battery SOC accounts for harvested power offset reducing discharge rate.
    """

    def __init__(self, arch: LayerArchitecture):
        self.L7  = arch.layers[7]
        self.cap = self.L7["battery_Wh"]
        self.harvest_W = self.L7["total_harvest_mW"] / 1000.0  # W

    def soc_pct(self, t_yr: np.ndarray, avg_W: float = 5.0) -> np.ndarray:
        """
        State of Charge vs time — accounts for harvested power offset.
          Net demand        = avg_W − harvest_W (harvesting reduces draw)
          Energy consumed   = net_W [W] × 8760 [hr/yr] × t_yr
          Self-discharge    = cap × 0.01 × t_yr  (Li-Thionyl spec: <1%/yr)
        Battery is not drawn at all while harvested power covers demand.
        """
        net_W    = max(avg_W - self.harvest_W, 0.0)  # harvesting offsets load
        consumed = net_W * 8760 * t_yr
        sd_loss  = self.cap * self.L7["self_discharge_pct_yr"] / 100.0 * t_yr
        return np.clip((self.cap - consumed - sd_loss) / self.cap * 100, 0, 100)

    def transmittance(self, depth_m: np.ndarray) -> np.ndarray:
        """
        Sapphire optical transmittance vs depth.
        T(d) = T₀ · (1 − 0.05·d/6000)  — slight linear compression penalty.
        T₀ = 85% (rated value at 6,000 m).
        """
        return self.L7["optical_transm"] * (1 - 0.05 * depth_m / 6000.0)

