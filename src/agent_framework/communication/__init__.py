"""
Agent communication protocol package.

This package provides the implementation of the agent communication protocol,
enabling agents to exchange messages and coordinate their activities.
"""

from .protocol import StandardCommunicationProtocol, CommunicatingAgentImpl
from .examples import run_example
from .ad_agency_example import run_ad_agency_example, CampaignManagerAgent, CreativeAgent, AgencyMessageType

__all__ = [
    'StandardCommunicationProtocol', 
    'CommunicatingAgentImpl',
    'run_example',
    'run_ad_agency_example',
    'CampaignManagerAgent',
    'CreativeAgent',
    'AgencyMessageType'
]