# LangGraph Service Node Pattern

Use this reference when the user asks for a reusable LangGraph pattern where each node calls a domain service and updates typed state.

The example below is intentionally split into the same layers the user is likely to request: state, services, node factory, and graph setup.

## `state.py`

```python
"""Typed state for the customer orders workflow."""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import BaseMessage


class CustomerWorkflowState(TypedDict):
    """State shared across the LangGraph workflow."""

    customer_id: str
    customer_orders: list[str]
    messages: list[BaseMessage]
    error: str | None
```

## `services.py`

```python
"""Domain services used by LangGraph nodes."""

from __future__ import annotations


def get_customer_orders_service(*, customer_id: str) -> list[str]:
    """Simulate loading a customer's orders from persistent storage."""

    _ = customer_id
    return ["order_1", "order_2"]
```

## `node_factory.py`

```python
"""Factories for creating LangGraph-compatible nodes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from state import CustomerWorkflowState

ServiceInputMapper = Callable[[CustomerWorkflowState], dict[str, Any]]
WorkflowNode = Callable[[CustomerWorkflowState], CustomerWorkflowState]


def service_node(
    service_func: Callable[..., Any],
    input_mapper: ServiceInputMapper,
    output_key: str,
) -> WorkflowNode:
    """Create a LangGraph node that delegates work to a domain service."""

    def node(state: CustomerWorkflowState) -> CustomerWorkflowState:
        """Call the service and return a new state dictionary."""

        try:
            service_input = input_mapper(state)
            result = service_func(**service_input)
        except Exception as exc:  # pragma: no cover - example error path
            return {**state, "error": str(exc)}

        return {**state, output_key: result, "error": None}

    return node


def append_llm_response_node(*, llm: BaseChatModel) -> WorkflowNode:
    """Create a node that appends an LLM response to the workflow messages."""

    def node(state: CustomerWorkflowState) -> CustomerWorkflowState:
        """Invoke the model with the current messages and append the response."""

        try:
            response = llm.invoke(state["messages"])
        except Exception as exc:  # pragma: no cover - example error path
            return {**state, "error": str(exc)}

        return {
            **state,
            "messages": [*state["messages"], response],
            "error": None,
        }

    return node
```

## `graph.py`

```python
"""Graph assembly for the customer orders workflow."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from node_factory import append_llm_response_node, service_node
from services import get_customer_orders_service
from state import CustomerWorkflowState


def map_customer_id(state: CustomerWorkflowState) -> dict[str, str]:
    """Map graph state into the service input payload."""

    return {"customer_id": state["customer_id"]}


get_customer_orders_node = service_node(
    service_func=get_customer_orders_service,
    input_mapper=map_customer_id,
    output_key="customer_orders",
)


def build_customer_orders_graph() -> Any:
    """Build the required base workflow: START -> get_customer_orders -> END."""

    graph = StateGraph(CustomerWorkflowState)
    graph.add_node("get_customer_orders", get_customer_orders_node)
    graph.add_edge(START, "get_customer_orders")
    graph.add_edge("get_customer_orders", END)
    return graph.compile()


def build_customer_orders_with_llm_graph(*, llm: BaseChatModel) -> Any:
    """Build the workflow with an additional LLM step after loading orders."""

    graph = StateGraph(CustomerWorkflowState)
    graph.add_node("get_customer_orders", get_customer_orders_node)
    graph.add_node("append_llm_response", append_llm_response_node(llm=llm))
    graph.add_edge(START, "get_customer_orders")
    graph.add_edge("get_customer_orders", "append_llm_response")
    graph.add_edge("append_llm_response", END)
    return graph.compile()


if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4.1-mini")
    workflow = build_customer_orders_with_llm_graph(llm=llm)
    result = workflow.invoke(
        {
            "customer_id": "customer_123",
            "customer_orders": [],
            "messages": [],
            "error": None,
        }
    )
    print(result)
```

## Extension Pattern For Multiple Services

Scale the workflow by creating more services and reusing the same node factory:

```python
def get_customer_profile_service(*, customer_id: str) -> dict[str, str]:
    return {"customer_id": customer_id, "tier": "gold"}


def map_customer_profile_input(state: CustomerWorkflowState) -> dict[str, str]:
    return {"customer_id": state["customer_id"]}


get_customer_profile_node = service_node(
    service_func=get_customer_profile_service,
    input_mapper=map_customer_profile_input,
    output_key="customer_profile",
)
```

Then add the new state field, register the new node, and connect it in `StateGraph` without moving business logic into the graph layer.
