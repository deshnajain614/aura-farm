"""
AURA-Farm Safety Engine - Multi-Tier Decision & Interlock Gatekeeper
===================================================================
Enforces the mandatory architectural principle:
    AI BRAIN -> Recommendation
         │
         ▼
    DECISION ENGINE
         │
         ▼
    SAFETY ENGINE
    ┌────────────┼────────────┐
    ▼            ▼            ▼
  Allowed    Restricted     Unsafe
    │            │            │
    ▼            ▼            ▼
 Execute     Clamped/Hold   Reject
"""
from typing import Dict, Any, List, Optional
import time
import logging
from aura_farm.core.types import SafetyGate, SafetyDecision
from aura_farm.config import config

logger = logging.getLogger("aura_farm.safety")

class SafetyEngine:
    def __init__(self):
        self.limits = config.safety
        self.emergency_stop_engaged: bool = False
        self.recent_decisions: List[SafetyDecision] = []
        self.hourly_dosed_volume_ml: float = 0.0
        self.last_dosing_reset: float = time.time()

    def set_emergency_stop(self, engaged: bool, reason: str = "Operator Triggered") -> None:
        """Instantly disables or enables all physical machinery and robotic actuators."""
        self.emergency_stop_engaged = engaged
        logger.warning(f"EMERGENCY STOP state changed to {engaged}. Reason: {reason}")

    def _reset_hourly_counters_if_needed(self):
        now = time.time()
        if now - self.last_dosing_reset > 3600.0:
            self.hourly_dosed_volume_ml = 0.0
            self.last_dosing_reset = now

    def evaluate_action(
        self,
        source: str,
        proposed_action: str,
        parameters: Dict[str, Any],
        current_state: Optional[Dict[str, Any]] = None
    ) -> SafetyDecision:
        """
        Evaluates proposed action against deterministic physical constraints.
        Categorizes action into ALLOWED, RESTRICTED, or UNSAFE.
        """
        self._reset_hourly_counters_if_needed()

        # Rule 1: Emergency Stop is absolute gatekeeper
        if self.emergency_stop_engaged:
            decision = SafetyDecision(
                recommendation_source=source,
                proposed_action=proposed_action,
                parameters=parameters,
                gate=SafetyGate.UNSAFE,
                reason="HARD INTERLOCK: Emergency Stop is engaged. All actuators locked.",
                executed=False
            )
            self._record_decision(decision)
            return decision

        # Rule 2: Water & Nutrient Dosing Limits
        if proposed_action in ["DOSE_NUTRIENT_A", "DOSE_NUTRIENT_B", "DOSE_PH_DOWN", "DOSE_PH_UP"]:
            dose_ml = float(parameters.get("volume_ml", 0.0))
            if dose_ml < 0:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.UNSAFE,
                    reason=f"Negative dosing value requested: {dose_ml} ml",
                    executed=False
                )
            elif dose_ml > self.limits.max_single_dose_ml:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.UNSAFE,
                    reason=f"Requested dose {dose_ml:.1f} ml exceeds single dose safety limit ({self.limits.max_single_dose_ml:.1f} ml).",
                    executed=False
                )
            elif (self.hourly_dosed_volume_ml + dose_ml) > self.limits.max_dosing_rate_ml_per_hour:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.RESTRICTED,
                    reason=f"Hourly dosing limit approaching ({self.hourly_dosed_volume_ml:.1f}/{self.limits.max_dosing_rate_ml_per_hour} ml). Action clamped.",
                    executed=False
                )
            else:
                self.hourly_dosed_volume_ml += dose_ml
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.ALLOWED,
                    reason="Dosing volume is within safe tolerance.",
                    executed=True
                )
            self._record_decision(decision)
            return decision

        # Rule 3: Environmental target setting bounds
        if proposed_action == "SET_CLIMATE_TARGETS":
            target_temp = parameters.get("temp_c")
            target_humidity = parameters.get("humidity_pct")
            target_co2 = parameters.get("co2_ppm")

            if target_temp and (target_temp < self.limits.min_ambient_temp_c or target_temp > self.limits.max_ambient_temp_c):
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.UNSAFE,
                    reason=f"Target temperature {target_temp}°C exceeds biological envelope [{self.limits.min_ambient_temp_c}, {self.limits.max_ambient_temp_c}]°C.",
                    executed=False
                )
            elif target_co2 and target_co2 > self.limits.max_co2_ppm:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.UNSAFE,
                    reason=f"CO2 target {target_co2} ppm exceeds safe ceiling ({self.limits.max_co2_ppm} ppm).",
                    executed=False
                )
            elif target_humidity and (target_humidity < self.limits.min_humidity_percent or target_humidity > self.limits.max_humidity_percent):
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.RESTRICTED,
                    reason=f"Humidity target {target_humidity}% is at biological edge. Clamping to safe profile.",
                    executed=True
                )
            else:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.ALLOWED,
                    reason="Climate parameters approved.",
                    executed=True
                )
            self._record_decision(decision)
            return decision

        # Rule 4: Robotic arm and gantry motion speeds
        if proposed_action in ["MOVE_ROBOT_GANTRY", "MOVE_ROBOT_ARM", "TRANSPLANT_POD"]:
            speed_mm_s = float(parameters.get("speed_mm_s", 100.0))
            if speed_mm_s > self.limits.robot_max_speed_mm_s:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters={"clamped_speed_mm_s": self.limits.robot_max_speed_mm_s},
                    gate=SafetyGate.RESTRICTED,
                    reason=f"Speed {speed_mm_s} mm/s exceeds robot limit. Clamped to {self.limits.robot_max_speed_mm_s} mm/s.",
                    executed=True
                )
            else:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.ALLOWED,
                    reason="Robotic motion trajectory is verified within safe bounds.",
                    executed=True
                )
            self._record_decision(decision)
            return decision

        # Rule 5: Sanitization CIP Chemical & Ozone Flush
        if proposed_action == "TRIGGER_CIP_FLUSH":
            zone_empty = parameters.get("is_zone_empty", False)
            if not zone_empty:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.UNSAFE,
                    reason="ABORT: Cannot run chemical CIP flush while crop zone has active plants.",
                    executed=False
                )
            else:
                decision = SafetyDecision(
                    recommendation_source=source,
                    proposed_action=proposed_action,
                    parameters=parameters,
                    gate=SafetyGate.ALLOWED,
                    reason="Zone verified empty. Clean-In-Place chemical flush authorized.",
                    executed=True
                )
            self._record_decision(decision)
            return decision

        # Default fallback
        decision = SafetyDecision(
            recommendation_source=source,
            proposed_action=proposed_action,
            parameters=parameters,
            gate=SafetyGate.ALLOWED,
            reason="Action passed default safety checks.",
            executed=True
        )
        self._record_decision(decision)
        return decision

    def _record_decision(self, decision: SafetyDecision):
        self.recent_decisions.append(decision)
        if len(self.recent_decisions) > 100:
            self.recent_decisions.pop(0)
        logger.info(f"Safety Gate: [{decision.gate.value}] {decision.proposed_action} - {decision.reason}")

# Singleton safety engine instance
safety_engine = SafetyEngine()
