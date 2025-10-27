import os
from typing import Optional, Dict, Any

from pydantic import BaseModel
from crewai.tools import BaseTool

from .cal_api import check_cal_availability, create_cal_booking
from memory.memory_store import ConversationMemory


# ------------------------------
# Memory instance
# ------------------------------
_memory = ConversationMemory(storage_path=os.getenv("MEMORY_PATH", "/workspace/data/memory.json"))


# ------------------------------
# Tool: Get Customer Info
# ------------------------------
class GetCustomerInfoArgs(BaseModel):
    name: str


class GetCustomerInfoTool(BaseTool):
    name: str = "get_customer_info"
    description: str = "Fetch a customer's record by name (mocked). Returns membership hints."
    args_schema: type[BaseModel] = GetCustomerInfoArgs

    def _run(self, name: str) -> str:
        return f"Customer record fetched for {name}. Membership: non-member."


# ------------------------------
# Tool: Search Knowledge Base
# ------------------------------
class SearchKnowledgeBaseArgs(BaseModel):
    query: str


class SearchKnowledgeBaseTool(BaseTool):
    name: str = "search_knowledge_base"
    description: str = "Search internal KB for barber shop FAQs and policies (mock)."
    args_schema: type[BaseModel] = SearchKnowledgeBaseArgs

    def _run(self, query: str) -> str:
        return (
            f"KB for '{query}': Walk-ins allowed when slots free; loyalty members get 10% off; "
            f"No-shows may be charged a small fee."
        )


# ------------------------------
# Tool: Get Appointment Status
# ------------------------------
class GetAppointmentStatusArgs(BaseModel):
    customer_id: str


class GetAppointmentStatusTool(BaseTool):
    name: str = "get_appointment_status"
    description: str = "Check a customer's appointment status (mock)."
    args_schema: type[BaseModel] = GetAppointmentStatusArgs

    def _run(self, customer_id: str) -> str:
        return f"Appointment status for customer {customer_id}: Confirmed for next scheduled booking."


# ------------------------------
# Tool: Get Services and Prices
# ------------------------------
class GetServicesAndPricesArgs(BaseModel):
    pass


class GetServicesAndPricesTool(BaseTool):
    name: str = "get_services_and_prices"
    description: str = "List available services and prices as a JSON object."
    args_schema: type[BaseModel] = GetServicesAndPricesArgs

    def _run(self) -> Dict[str, str]:
        return {
            "Haircut": "$25",
            "Beard Trim": "$15",
            "Haircut + Beard": "$35",
            "Premium Grooming Package": "$60",
            "Kids Cut": "$20",
            "Hot Towel Shave": "$30",
        }


# ------------------------------
# Tool: Get Conversation History
# ------------------------------
class GetConversationHistoryArgs(BaseModel):
    customer_id: str
    limit: int = 20


class GetConversationHistoryTool(BaseTool):
    name: str = "get_conversation_history"
    description: str = "Return recent conversation history with timestamps for a customer."
    args_schema: type[BaseModel] = GetConversationHistoryArgs

    def _run(self, customer_id: str, limit: int = 20) -> str:
        return _memory.summarize_history(customer_id)


# ------------------------------
# Tool: Cal.com Availability
# ------------------------------
class CalCheckAvailabilityArgs(BaseModel):
    date: str
    time: Optional[str] = None
    duration_minutes: int = 30


class CalCheckAvailabilityTool(BaseTool):
    name: str = "get_cal_availability"
    description: str = "Check Cal.com availability for a given date/time and duration. Returns JSON."
    args_schema: type[BaseModel] = CalCheckAvailabilityArgs

    def _run(self, date: str, time: Optional[str] = None, duration_minutes: int = 30) -> Dict[str, Any]:
        return check_cal_availability(date, time, duration_minutes)


# ------------------------------
# Tool: Cal.com Booking
# ------------------------------
class CalMakeBookingArgs(BaseModel):
    name: str
    email: str
    date: str
    time: str
    notes: Optional[str] = None
    timezone: Optional[str] = None


class CalMakeBookingTool(BaseTool):
    name: str = "make_cal_booking"
    description: str = "Create a Cal.com booking for the provided customer name/email and date/time. Returns JSON."
    args_schema: type[BaseModel] = CalMakeBookingArgs

    def _run(
        self,
        name: str,
        email: str,
        date: str,
        time: str,
        notes: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> Dict[str, Any]:
        return create_cal_booking(name, email, date, time, notes, timezone)


# Export list of instantiated tools
ALL_TOOLS = [
    GetCustomerInfoTool(),
    SearchKnowledgeBaseTool(),
    GetAppointmentStatusTool(),
    GetServicesAndPricesTool(),
    GetConversationHistoryTool(),
    CalCheckAvailabilityTool(),
    CalMakeBookingTool(),
]