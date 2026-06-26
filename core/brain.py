from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectProfile:
    project_type: str
    target_customer: str
    industry: str
    recommended_frontend: str
    recommended_backend: str
    recommended_database: str
    recommended_hosting: str
    recommended_payment: str
    ai_required: bool
    crm_required: bool
    landing_page_required: bool
    mobile_app_required: bool
    estimated_complexity: str
    estimated_budget: str
    development_priority: str


class Brain:
    """Deterministic decision-making engine for project profiling."""

    def analyze(self, user_idea: str) -> ProjectProfile:
        """Analyze a user idea and return a deterministic project profile."""
        text = user_idea.strip().lower()
        profile = self._base_profile(text)
        profile = self._apply_domain_overrides(profile, text)
        profile = self._apply_requirement_flags(profile, text)
        return profile

    def _base_profile(self, text: str) -> ProjectProfile:
        if any(keyword in text for keyword in ["crm", "customer relationship", "customer management"]):
            return ProjectProfile(
                project_type="CRM",
                target_customer="SMBs that need customer and sales lifecycle management.",
                industry="Business Operations",
                recommended_frontend="React",
                recommended_backend="FastAPI",
                recommended_database="PostgreSQL",
                recommended_hosting="Railway",
                recommended_payment="Subscription billing with tiered plans",
                ai_required=False,
                crm_required=True,
                landing_page_required=False,
                mobile_app_required=False,
                estimated_complexity="Medium",
                estimated_budget="15,000-30,000 PLN",
                development_priority="High",
            )

        if any(keyword in text for keyword in ["ai", "machine learning", "ml", "predictive"]):
            return ProjectProfile(
                project_type="AI SaaS",
                target_customer="Product teams and enterprises seeking automation and insights.",
                industry="Technology",
                recommended_frontend="React",
                recommended_backend="FastAPI",
                recommended_database="PostgreSQL",
                recommended_hosting="Railway",
                recommended_payment="Usage-based billing",
                ai_required=True,
                crm_required=False,
                landing_page_required=True,
                mobile_app_required=False,
                estimated_complexity="High",
                estimated_budget="30,000-60,000 PLN",
                development_priority="Critical",
            )

        if any(keyword in text for keyword in ["mobile", "flutter", "android", "ios"]):
            return ProjectProfile(
                project_type="Mobile App",
                target_customer="Mobile-first users demanding native-like experiences.",
                industry="Consumer Apps",
                recommended_frontend="Flutter",
                recommended_backend="Firebase Functions",
                recommended_database="Firebase Firestore",
                recommended_hosting="Firebase Hosting",
                recommended_payment="In-app purchases or subscription",
                ai_required=False,
                crm_required=False,
                landing_page_required=True,
                mobile_app_required=True,
                estimated_complexity="Medium",
                estimated_budget="20,000-40,000 PLN",
                development_priority="High",
            )

        if any(keyword in text for keyword in ["landing page", "website", "portfolio"]):
            return ProjectProfile(
                project_type="Landing Page",
                target_customer="Small business owners and freelancers needing a web presence.",
                industry="Marketing",
                recommended_frontend="HTML/CSS/JS",
                recommended_backend="None",
                recommended_database="None",
                recommended_hosting="GitHub Pages",
                recommended_payment="One-time setup fee",
                ai_required=False,
                crm_required=False,
                landing_page_required=True,
                mobile_app_required=False,
                estimated_complexity="Low",
                estimated_budget="2,000-6,000 PLN",
                development_priority="Medium",
            )

        return ProjectProfile(
            project_type="General Web App",
            target_customer="Early adopters who value polished digital workflows.",
            industry="Technology",
            recommended_frontend="React",
            recommended_backend="FastAPI",
            recommended_database="PostgreSQL",
            recommended_hosting="Railway",
            recommended_payment="Subscription or usage-based billing",
            ai_required=False,
            crm_required=False,
            landing_page_required=True,
            mobile_app_required=False,
            estimated_complexity="Medium",
            estimated_budget="15,000-35,000 PLN",
            development_priority="High",
        )

    def _apply_domain_overrides(self, profile: ProjectProfile, text: str) -> ProjectProfile:
        if any(keyword in text for keyword in ["e-commerce", "shop", "store"]):
            return ProjectProfile(
                project_type="E-commerce",
                target_customer="Online retailers and merchants selling products digitally.",
                industry="E-commerce",
                recommended_frontend="React",
                recommended_backend="FastAPI",
                recommended_database="PostgreSQL",
                recommended_hosting="Railway",
                recommended_payment="Stripe or PayPal integration",
                ai_required=profile.ai_required,
                crm_required=profile.crm_required,
                landing_page_required=True,
                mobile_app_required=profile.mobile_app_required,
                estimated_complexity="High",
                estimated_budget="35,000-70,000 PLN",
                development_priority="Critical",
            )

        if any(keyword in text for keyword in ["saas", "platform", "multi-tenant"]):
            return ProjectProfile(
                project_type="SaaS Platform",
                target_customer="Business users and developers needing scalable software.",
                industry="SaaS",
                recommended_frontend=profile.recommended_frontend,
                recommended_backend=profile.recommended_backend,
                recommended_database=profile.recommended_database,
                recommended_hosting=profile.recommended_hosting,
                recommended_payment="Subscription billing",
                ai_required=profile.ai_required,
                crm_required=profile.crm_required,
                landing_page_required=True,
                mobile_app_required=profile.mobile_app_required,
                estimated_complexity="High",
                estimated_budget="25,000-55,000 PLN",
                development_priority="Critical",
            )

        return profile

    def _apply_requirement_flags(self, profile: ProjectProfile, text: str) -> ProjectProfile:
        ai_required = profile.ai_required or any(keyword in text for keyword in ["chatbot", "recommendation", "automation"])
        crm_required = profile.crm_required or any(keyword in text for keyword in ["customer", "sales pipeline", "lead management"])
        landing_page_required = profile.landing_page_required or any(keyword in text for keyword in ["landing page", "website", "homepage"])
        mobile_app_required = profile.mobile_app_required or any(keyword in text for keyword in ["mobile", "app", "iphone", "android"])

        return ProjectProfile(
            project_type=profile.project_type,
            target_customer=profile.target_customer,
            industry=profile.industry,
            recommended_frontend=profile.recommended_frontend,
            recommended_backend=profile.recommended_backend,
            recommended_database=profile.recommended_database,
            recommended_hosting=profile.recommended_hosting,
            recommended_payment=profile.recommended_payment,
            ai_required=ai_required,
            crm_required=crm_required,
            landing_page_required=landing_page_required,
            mobile_app_required=mobile_app_required,
            estimated_complexity=profile.estimated_complexity,
            estimated_budget=profile.estimated_budget,
            development_priority=profile.development_priority,
        )
