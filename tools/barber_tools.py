from typing import Optional, Dict
from langchain_core.tools import tool
from .cal_api import cal_check_availability, cal_make_booking
from memory.memory_store import ConversationMemory
import os

# Re-export Cal.com tools
get_cal_availability = cal_check_availability
make_cal_booking = cal_make_booking

_memory = ConversationMemory(storage_path=os.getenv("MEMORY_PATH", "/workspace/data/memory.json"))


@tool
def get_customer_info(name: str) -> str:
    """Fetch customer record using name (mocked)."""
    return f"Customer record fetched for {name}. Membership: non-member."


@tool
def search_knowledge_base(query: str) -> str:
    """Search for common barber service questions (mocked)."""
    return f"Knowledge base notes for '{query}': Walk-ins allowed when slots free; loyalty members get 10% off."


@tool
def get_appointment_status(customer_id: str) -> str:
    """Check a customer's appointment status (mocked)."""
    return f"Appointment status for customer {customer_id}: Confirmed for next scheduled booking."


@tool
def get_services_and_prices() -> dict:
    """List all available services and their prices."""
    return {
        "Haircut": "$25",
        "Beard Trim": "$15",
        "Haircut + Beard": "$35",
        "Premium Grooming Package": "$60",
        "Kids Cut": "$20",
        "Hot Towel Shave": "$30",
    }


@tool
def get_conversation_history(customer_id: str, limit: int = 20) -> str:
    """Return recent conversation history with timestamps for a customer."""
    return _memory.summarize_history(customer_id)


ALL_TOOLS = [
    get_customer_info,
    search_knowledge_base,
    get_appointment_status,
    get_services_and_prices,
    get_conversation_history,
    # Cal.com
    get_cal_availability,
    make_cal_booking,
]