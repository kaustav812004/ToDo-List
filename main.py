import os
from crewai import Crew
from agents import BarberAgents
from tasks import BarberTasks
from memory.memory_store import ConversationMemory
from rich import print
from dotenv import load_dotenv

load_dotenv()


class BarberServiceCrew:
    def __init__(self, customer_id: str, customer_name: str, service_request: str, customer_details=None, model: str = "gpt-4o"):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.service_request = service_request
        self.customer_details = customer_details or {}
        self.model = model
        self.memory = ConversationMemory(storage_path=os.getenv("MEMORY_PATH", "/workspace/data/memory.json"))

    def run(self):
        agents = BarberAgents(model=self.model)
        tasks = BarberTasks()

        customer_service_manager = agents.customer_service_manager()
        appointment_specialist = agents.appointment_booking_specialist()
        service_consultant = agents.service_consultant()
        pricing_specialist = agents.pricing_payment_specialist()
        support_agent = agents.customer_support_agent()

        crew_tasks = []
        crew_agents = [customer_service_manager]

        req_lower = (self.service_request or "").lower()
        details = self.customer_details

        # Persist the incoming user request with timestamp
        self.memory.add_message(self.customer_id, role="user", content=self.service_request)

        # Shop info
        if any(k in req_lower for k in ["information", "hours", "open", "location", "where"]):
            crew_tasks.append(
                tasks.provide_shop_information(
                    customer_service_manager,
                    details.get("info_type", "general"),
                    details.get("specific_questions"),
                )
            )

        # Appointment flow
        if any(k in req_lower for k in ["appointment", "book", "schedule"]):
            crew_agents.append(appointment_specialist)
            crew_tasks.append(
                tasks.manage_appointment(
                    appointment_specialist,
                    self.customer_name,
                    details.get("preferred_date", "flexible"),
                    details.get("preferred_time", "flexible"),
                    details.get("service_type", "haircut"),
                    details.get("special_requests"),
                    details.get("email", "guest@example.com"),
                    details.get("timezone", os.getenv("DEFAULT_TIMEZONE", "UTC")),
                )
            )

        # Recommendations
        if any(k in req_lower for k in ["recommend", "service", "suggest"]):
            crew_agents.append(service_consultant)
            crew_tasks.append(
                tasks.recommend_services(
                    service_consultant,
                    details.get("profile", "new customer"),
                    details.get("hair_type", "unknown"),
                    details.get("lifestyle", "busy professional"),
                    details.get("budget", "$50-100"),
                    details.get("special_occasions"),
                )
            )

        # Pricing
        if any(k in req_lower for k in ["price", "cost", "how much", "pricing"]):
            crew_agents.append(pricing_specialist)
            crew_tasks.append(
                tasks.handle_pricing_inquiry(
                    pricing_specialist,
                    details.get("services_interested", "haircut and beard trim"),
                    details.get("package_deals", True),
                    details.get("membership_status", "non-member"),
                    details.get("pricing_questions"),
                )
            )

        # Support / issues
        if any(k in req_lower for k in ["complaint", "issue", "problem", "bad", "refund"]):
            crew_agents.append(support_agent)
            crew_tasks.append(
                tasks.resolve_customer_issue(
                    support_agent,
                    details.get("issue_description", self.service_request),
                    details.get("customer_history", "regular customer"),
                    details.get("urgency", "medium"),
                    details.get("preferred_resolution"),
                )
            )

        # Default path
        if not crew_tasks:
            crew_agents.append(service_consultant)
            crew_tasks.append(
                tasks.recommend_services(
                    service_consultant,
                    "general inquiry",
                    "unknown",
                    "unknown",
                    "flexible",
                    None,
                )
            )

        # Include conversation history as context (memory)
        history_summary = self.memory.summarize_history(self.customer_id)
        for t in crew_tasks:
            t.description = (
                "Conversation history (latest first):\n" + history_summary + "\n\n" + t.description
            )

        crew = Crew(
            agents=crew_agents,
            tasks=crew_tasks,
            verbose=True,
            memory=False,
        )

        result = crew.kickoff()

        # Persist assistant reply to memory
        if isinstance(result, str):
            self.memory.add_message(self.customer_id, role="assistant", content=result)
        else:
            self.memory.add_message(self.customer_id, role="assistant", content=str(result))

        return result


if __name__ == "__main__":
    print("\n==============================")
    print(" Welcome to BarberBot Crew")
    print("==============================")

    name = input("Enter your name: ").strip() or "Guest"
    email = input("Enter your email: ").strip() or "guest@example.com"
    req = input("What would you like to do (pricing/booking/recommend/info/issue): ").strip()
    date = input("Preferred date (e.g., 2025-08-20 or 'tomorrow'): ").strip() or "flexible"
    time = input("Preferred time (e.g., 3pm): ").strip() or "flexible"
    service_type = input("Service you want (e.g., haircut): ").strip() or "haircut"
    spe_req = input("Any special requests: ").strip() or ""
    timezone = input("Your timezone (e.g., America/New_York): ").strip() or os.getenv("DEFAULT_TIMEZONE", "UTC")

    crew = BarberServiceCrew(
        customer_id=email or name,
        customer_name=name,
        service_request=req,
        customer_details={
            "preferred_date": date,
            "preferred_time": time,
            "service_type": service_type,
            "special_requests": spe_req,
            "email": email,
            "timezone": timezone,
        },
    )

    result = crew.run()

    print("\n==============================")
    print(" Response ✂️")
    print("==============================")
    print(result)