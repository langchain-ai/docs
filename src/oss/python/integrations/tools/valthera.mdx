---
title: Valthera
---

Enable AI agents to engage users when they're most likely to respond.

## Overview

Valthera is an open-source framework that enables LLM Agents to engage users in a more meaningful way. It is built on BJ Fogg's Behavior Model (B=MAT) and leverages data from multiple sources (such as HubSpot, PostHog, and Snowflake) to assess a user's **motivation** and **ability** before triggering an action.

In this guide, you'll learn:

- **Core Concepts:** Overview of the components (Data Aggregator, Scorer, Reasoning Engine, and Trigger Generator).
- **System Architecture:** How data flows through the system and how decisions are made.
- **Customization:** How to extend connectors, scoring metrics, and decision rules to fit your needs.

Let's dive in!

## Setup

This section covers installation of dependencies and setting up custom data connectors for Valthera.

```python
pip install openai langchain langchain_openai valthera langchain_valthera langgraph
```

```python
from typing import Any, Dict, List

from valthera.connectors.base import BaseConnector


class MockHubSpotConnector(BaseConnector):
    """
    Simulates data retrieval from HubSpot. Provides information such as lead score,
    lifecycle stage, and marketing metrics.
    """

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve mock HubSpot data for a given user.

        Args:
            user_id: The unique identifier for the user

        Returns:
            A dictionary containing HubSpot user data
        """
        return {
            "hubspot_contact_id": "999-ZZZ",
            "lifecycle_stage": "opportunity",
            "lead_status": "engaged",
            "hubspot_lead_score": 100,
            "company_name": "MaxMotivation Corp.",
            "last_contacted_date": "2023-09-20",
            "hubspot_marketing_emails_opened": 20,
            "marketing_emails_clicked": 10,
        }


class MockPostHogConnector(BaseConnector):
    """
    Simulates data retrieval from PostHog. Provides session data and engagement events.
    """

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve mock PostHog data for a given user.

        Args:
            user_id: The unique identifier for the user

        Returns:
            A dictionary containing PostHog user data
        """
        return {
            "distinct_ids": [user_id, f"email_{user_id}"],
            "last_event_timestamp": "2023-09-20T12:34:56Z",
            "feature_flags": ["beta_dashboard", "early_access"],
            "posthog_session_count": 30,
            "avg_session_duration_sec": 400,
            "recent_event_types": ["pageview", "button_click", "premium_feature_used"],
            "posthog_events_count_past_30days": 80,
            "posthog_onboarding_steps_completed": 5,
        }


class MockSnowflakeConnector(BaseConnector):
    """
    Simulates retrieval of additional user profile data from Snowflake.
    """

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve mock Snowflake data for a given user.

        Args:
            user_id: The unique identifier for the user

        Returns:
            A dictionary containing Snowflake user data
        """
        return {
            "user_id": user_id,
            "email": f"{user_id}@example.com",
            "subscription_status": "paid",
            "plan_tier": "premium",
            "account_creation_date": "2023-01-01",
            "preferred_language": "en",
            "last_login_datetime": "2023-09-20T12:00:00Z",
            "behavior_complexity": 3,
        }
```

## Instantiation

In this section, we instantiate the core components. First, we create a Data Aggregator to combine data from the custom connectors. Then, we configure the scoring metrics for motivation and ability.

```python
from valthera.aggregator import DataAggregator

# Constants for configuration
LEAD_SCORE_MAX = 100
EVENTS_COUNT_MAX = 50
EMAILS_OPENED_FACTOR = 10.0
SESSION_COUNT_FACTOR_1 = 5.0
ONBOARDING_STEPS_FACTOR = 5.0
SESSION_COUNT_FACTOR_2 = 10.0
BEHAVIOR_COMPLEXITY_MAX = 5.0

# Initialize data aggregator
data_aggregator = DataAggregator(
    connectors={
        "hubspot": MockHubSpotConnector(),
        "posthog": MockPostHogConnector(),
        "snowflake": MockSnowflakeConnector(),
    }
)

# You can now fetch unified user data by calling data_aggregator.get_user_context(user_id)
```

```python
from typing import Callable, Union

from valthera.scorer import ValtheraScorer


# Define transform functions with proper type annotations
def transform_lead_score(x: Union[int, float]) -> float:
    """Transform lead score to a value between 0 and 1."""
    return min(x, LEAD_SCORE_MAX) / LEAD_SCORE_MAX


def transform_events_count(x: Union[int, float]) -> float:
    """Transform events count to a value between 0 and 1."""
    return min(x, EVENTS_COUNT_MAX) / EVENTS_COUNT_MAX


def transform_emails_opened(x: Union[int, float]) -> float:
    """Transform emails opened to a value between 0 and 1."""
    return min(x / EMAILS_OPENED_FACTOR, 1.0)


def transform_session_count_1(x: Union[int, float]) -> float:
    """Transform session count for motivation to a value between 0 and 1."""
    return min(x / SESSION_COUNT_FACTOR_1, 1.0)


def transform_onboarding_steps(x: Union[int, float]) -> float:
    """Transform onboarding steps to a value between 0 and 1."""
    return min(x / ONBOARDING_STEPS_FACTOR, 1.0)


def transform_session_count_2(x: Union[int, float]) -> float:
    """Transform session count for ability to a value between 0 and 1."""
    return min(x / SESSION_COUNT_FACTOR_2, 1.0)


def transform_behavior_complexity(x: Union[int, float]) -> float:
    """Transform behavior complexity to a value between 0 and 1."""
    return 1 - (min(x, BEHAVIOR_COMPLEXITY_MAX) / BEHAVIOR_COMPLEXITY_MAX)


# Scoring configuration for user motivation
motivation_config = [
    {"key": "hubspot_lead_score", "weight": 0.30, "transform": transform_lead_score},
    {
        "key": "posthog_events_count_past_30days",
        "weight": 0.30,
        "transform": transform_events_count,
    },
    {
        "key": "hubspot_marketing_emails_opened",
        "weight": 0.20,
        "transform": transform_emails_opened,
    },
    {
        "key": "posthog_session_count",
        "weight": 0.20,
        "transform": transform_session_count_1,
    },
]

# Scoring configuration for user ability
ability_config = [
    {
        "key": "posthog_onboarding_steps_completed",
        "weight": 0.30,
        "transform": transform_onboarding_steps,
    },
    {
        "key": "posthog_session_count",
        "weight": 0.30,
        "transform": transform_session_count_2,
    },
    {
        "key": "behavior_complexity",
        "weight": 0.40,
        "transform": transform_behavior_complexity,
    },
]

# Instantiate the scorer
scorer = ValtheraScorer(motivation_config, ability_config)
```

## Invocation

Next, we set up the Reasoning Engine and Trigger Generator, then bring all components together by instantiating the Valthera Tool. Finally, we execute the agent workflow to process an input message.

```python
import os

from langchain_openai import ChatOpenAI
from valthera.reasoning_engine import ReasoningEngine

# Define threshold as constant
SCORE_THRESHOLD = 0.75


# Function to safely get API key
def get_openai_api_key() -> str:
    """Get OpenAI API key with error handling."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key


# Decision rules using constant
decision_rules = [
    {
        "condition": f"motivation >= {SCORE_THRESHOLD} and ability >= {SCORE_THRESHOLD}",
        "action": "trigger",
        "description": "Both scores are high enough.",
    },
    {
        "condition": f"motivation < {SCORE_THRESHOLD}",
        "action": "improve_motivation",
        "description": "User motivation is low.",
    },
    {
        "condition": f"ability < {SCORE_THRESHOLD}",
        "action": "improve_ability",
        "description": "User ability is low.",
    },
    {
        "condition": "otherwise",
        "action": "defer",
        "description": "No action needed at this time.",
    },
]

try:
    api_key = get_openai_api_key()
    reasoning_engine = ReasoningEngine(
        llm=ChatOpenAI(
            model_name="gpt-4-turbo", temperature=0.0, openai_api_key=api_key
        ),
        decision_rules=decision_rules,
    )
except ValueError as e:
    print(f"Error initializing reasoning engine: {e}")
```

```python
from valthera.trigger_generator import TriggerGenerator

try:
    api_key = get_openai_api_key()  # Reuse the function for consistency
    trigger_generator = TriggerGenerator(
        llm=ChatOpenAI(
            model_name="gpt-4-turbo", temperature=0.7, openai_api_key=api_key
        )
    )
except ValueError as e:
    print(f"Error initializing trigger generator: {e}")
```

```python
from langchain_valthera.tools import ValtheraTool
from langchain.agents import create_agent

try:
    api_key = get_openai_api_key()

    # Initialize Valthera tool
    valthera_tool = ValtheraTool(
        data_aggregator=data_aggregator,
        motivation_config=motivation_config,
        ability_config=ability_config,
        reasoning_engine=reasoning_engine,
        trigger_generator=trigger_generator,
    )

    # Create agent with LLM
    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.0, openai_api_key=api_key)
    tools = [valthera_tool]
    graph = create_agent(llm, tools=tools)

    # Define input message for testing
    inputs = {
        "messages": [("user", "Evaluate behavior for user_12345: Finish Onboarding")]
    }

    # Process the input and display responses
    print("Running Valthera agent workflow...")
    for response in graph.stream(inputs, stream_mode="values"):
        print(response)

except Exception as e:
    print(f"Error running Valthera workflow: {e}")
```

## Chaining

This integration does not currently support chaining operations. Future releases may include chaining support.

## API reference

Below is an overview of the key APIs provided by the Valthera integration:

- **Data Aggregator:** Use `data_aggregator.get_user_context(user_id)` to fetch aggregated user data.
- **Scorer:** The `ValtheraScorer` computes motivation and ability scores based on the provided configurations.
- **Reasoning Engine:** The `ReasoningEngine` evaluates decision rules to determine the appropriate action (trigger, improve motivation, improve ability, or defer).
- **Trigger Generator:** Generates personalized trigger messages using the LLM.
- **Valthera Tool:** Integrates all the components to process inputs and execute the agent workflow.

For detailed usage, refer to the inline documentation in the source code.
