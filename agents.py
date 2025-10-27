import os
from crewai import Agent, LLM
from tools.barber_tools import ALL_TOOLS


class BarberAgents:
    def __init__(self, model: str = "gpt-4o"):
        azure_base = os.getenv("AZURE_API_BASE")
        azure_key = os.getenv("AZURE_API_KEY")
        azure_version = os.getenv("AZURE_API_VERSION")
        azure_deploy = os.getenv("AZURE_DEPLOYMENT_NAME", model)
        openai_key = os.getenv("OPENAI_API_KEY")

        try:
            if azure_base and azure_key and azure_version and azure_deploy:
                self.llm = LLM(
                    api_base=azure_base,
                    api_key=azure_key,
                    api_version=azure_version,
                    model=f"azure/{azure_deploy}",
                    temperature=0.4,
                    max_tokens=1200,
                    timeout=60,
                    max_retries=3,
                )
            elif openai_key:
                # Fallback to OpenAI if available
                self.llm = LLM(
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    temperature=0.4,
                    max_tokens=1200,
                    timeout=60,
                    max_retries=3,
                )
            else:
                raise RuntimeError(
                    "Missing Azure OpenAI env (AZURE_API_BASE, AZURE_API_KEY, AZURE_API_VERSION, AZURE_DEPLOYMENT_NAME) "
                    "and no OPENAI_API_KEY fallback found. Configure `.env` before running."
                )
        except Exception as e:
            print("[ERROR] LLM init failed:", e)
            raise

    def customer_service_manager(self) -> Agent:
        return Agent(
            role="Customer Service Manager",
            goal="Help customers with appointments, questions, and resolving any issues",
            backstory="You work in a premium barber shop helping customers every day.",
            tools=ALL_TOOLS,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def appointment_booking_specialist(self) -> Agent:
        return Agent(
            role="Appointment Booking Specialist",
            goal="Schedule appointments and manage booking slots efficiently using Cal.com",
            backstory="You are detail-oriented and know how to fill up a barber's calendar efficiently.",
            tools=[t for t in ALL_TOOLS if t.name in [
                "get_cal_availability",
                "make_cal_booking",
                "get_customer_info",
                "get_conversation_history",
            ]],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def service_consultant(self) -> Agent:
        return Agent(
            role="Service Consultant",
            goal="Help customers choose the best grooming service",
            backstory="You know everything about hairstyles and customer grooming.",
            tools=[t for t in ALL_TOOLS if t.name in [
                "search_knowledge_base",
                "get_services_and_prices",
                "get_conversation_history",
            ]],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def pricing_payment_specialist(self) -> Agent:
        return Agent(
            role="Pricing and Payment Specialist",
            goal="Explain service prices and offers clearly to customers",
            backstory="You ensure pricing is never a confusion for customers.",
            tools=[t for t in ALL_TOOLS if t.name in [
                "get_services_and_prices",
                "search_knowledge_base",
                "get_conversation_history",
            ]],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )

    def customer_support_agent(self) -> Agent:
        return Agent(
            role="Customer Support Agent",
            goal="Resolve any complaints or service issues with empathy and speed",
            backstory="You are trained in customer retention and problem resolution.",
            tools=[t for t in ALL_TOOLS if t.name in [
                "get_customer_info",
                "get_appointment_status",
                "search_knowledge_base",
                "get_conversation_history",
            ]],
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
        )