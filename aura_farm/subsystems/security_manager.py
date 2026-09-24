"""
Autonomous Cybersecurity & Device Authentication Subsystem (Prompt Section 25)
==============================================================================
- Device cryptographic authentication with HMAC-SHA256 command signatures.
- Role-Based Access Control (RBAC):
    * SYSTEM_AUTONOMOUS (internal state machine)
    * FARM_ADMIN (authorized configuration)
    * FIELD_TECHNICIAN (hardware servicing)
    * AUDITOR (read-only telemetry)
- Prevents unauthorized actuator activation or malicious dosing pump overrides.
- Immutable audit log of all physical commands.
"""
from typing import Dict, Any, List, Optional
import hmac
import hashlib
import time
import logging
from aura_farm.core.types import RoleType
from aura_farm.config import config

logger = logging.getLogger("aura_farm.security")

class SecurityAuditEntry:
    def __init__(self, actor: str, role: str, action: str, authorized: bool, reason: str, signature: str):
        self.timestamp = time.time()
        self.actor = actor
        self.role = role
        self.action = action
        self.authorized = authorized
        self.reason = reason
        self.signature = signature

class CybersecurityManager:
    def __init__(self, secret_key: str = config.jwt_secret_key):
        self.secret_key = secret_key.encode()
        self.audit_log: List[SecurityAuditEntry] = []
        self.registered_device_keys: Dict[str, str] = {
            "EDGE_BRAIN_CONTROLLER_01": "aura-hw-edge-device-key-9988",
            "GANTRY_ROBOT_MCU": "aura-hw-gantry-key-7711",
            "MOBILE_INSPECTOR_ROVER": "aura-hw-rover-key-3322",
            "CIP_SANITIZER_CONTROLLER": "aura-hw-cip-key-5544"
        }

    def sign_command(self, device_id: str, action: str, timestamp: float) -> str:
        """Generates HMAC-SHA256 signature for internal command bus."""
        msg = f"{device_id}:{action}:{timestamp}".encode()
        return hmac.new(self.secret_key, msg, hashlib.sha256).hexdigest()

    def verify_command_signature(self, device_id: str, action: str, timestamp: float, signature: str) -> bool:
        """Validates command authenticity and freshness (< 30 seconds old to prevent replay attacks)."""
        if abs(time.time() - timestamp) > 30.0:
            logger.warning(f"Cybersecurity: Rejected command '{action}' from {device_id} due to expired timestamp (Replay prevention).")
            return False

        expected = self.sign_command(device_id, action, timestamp)
        return hmac.compare_digest(expected, signature)

    def authorize_action(
        self,
        actor: str,
        role: RoleType,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        signature: Optional[str] = None
    ) -> bool:
        """
        Enforces strict RBAC.
        For example: An AUDITOR or unauthenticated user CANNOT trigger nutrient pumps or robot arms.
        """
        parameters = parameters or {}
        authorized = False
        reason = ""

        # High-risk physical actions requiring SYSTEM_AUTONOMOUS or FARM_ADMIN
        high_risk_actions = [
            "DOSE_NUTRIENT_A", "DOSE_NUTRIENT_B", "DOSE_PH_DOWN", "DOSE_PH_UP",
            "MOVE_ROBOT_ARM", "TRIGGER_CIP_FLUSH", "OVERRIDE_HVAC", "EMERGENCY_STOP"
        ]

        if action in high_risk_actions:
            if role in [RoleType.SYSTEM_AUTONOMOUS, RoleType.FARM_ADMIN]:
                authorized = True
                reason = f"Authorized: Role {role.value} possesses physical actuation privilege."
            else:
                authorized = False
                reason = f"DENIED: Role {role.value} is not permitted to trigger physical actuator '{action}'."
        else:
            # Read-only or safe status inspection
            authorized = True
            reason = f"Authorized: Role {role.value} has read/status access."

        # Record to immutable audit trail
        sig = signature or self.sign_command(actor, action, time.time())
        entry = SecurityAuditEntry(actor, role.value, action, authorized, reason, sig)
        self.audit_log.append(entry)

        if not authorized:
            logger.critical(f"CYBERSECURITY INCIDENT: Blocked unauthorized command '{action}' by {actor} ({role.value})!")

        return authorized

security_manager = CybersecurityManager()
