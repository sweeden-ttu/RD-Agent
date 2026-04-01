"""
RL UI Configuration Constants
"""

from typing import Literal

# Event type definition
EventType = Literal[
    "scenario",
    "llm_call",
    "template",
    "experiment",
    "code",
    "docker_exec",
    "feedback",
    "token",
    "time",
    "settings",
    "hypothesis",
]

# Always visible event types
ALWAYS_VISIBLE_TYPES = [
    "scenario",
    "hypothesis",
    "llm_call",
    "code",
    "podman",
    "feedback",
]

# Optional event types with toggle config (label, default_enabled)
OPTIONAL_TYPES = {
     "experiment",
    "template",
    "token", 
    "time" ,
    "settings"
}
