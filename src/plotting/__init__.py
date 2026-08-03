"""
Plotting layer: one module per figure (Figs 1-11), plus the shared
``_save`` helper. Each figure function takes only the domain/ML objects it
actually needs and writes a single PNG to ``config.OUTPUT_DIR``.
"""
from .utils import _save
from .fig01_pressure_flow import fig1_pressure_flow
from .fig02_sensor_signals import fig2_sensor_signals
from .fig03_healing_response import fig3_healing_response
from .fig04_cross_section import fig4_cross_section
from .fig05_intelligence_layer import fig5_intelligence_layer
from .fig06_structural_environment import fig6_structural_environment
from .fig07_performance_summary import fig7_performance_summary
from .fig08_phmsa_landscape import fig8_phmsa_landscape
from .fig09_quantitative_validation import fig9_quantitative_validation
from .fig10_ieee_validation_dashboard import fig10_ieee_validation_dashboard
from .fig11_ml_sensor_fusion import fig11_ml_sensor_fusion

__all__ = [
    "_save",
    "fig1_pressure_flow",
    "fig2_sensor_signals",
    "fig3_healing_response",
    "fig4_cross_section",
    "fig5_intelligence_layer",
    "fig6_structural_environment",
    "fig7_performance_summary",
    "fig8_phmsa_landscape",
    "fig9_quantitative_validation",
    "fig10_ieee_validation_dashboard",
    "fig11_ml_sensor_fusion",
]
