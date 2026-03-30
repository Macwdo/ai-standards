---
name: langgraph-service-nodes
description: Build or refactor LangGraph workflows in Python 3.11+ where each node is a thin adapter around a domain service and updates typed state immutably. Use when working with LangGraph, LangChain, ChatOpenAI, clean architecture, reusable node factories, TypedDict graph state, service-backed orchestration, or when converting business logic out of graph definitions and into composable services.
---

# LangGraph Service Nodes

Use this skill to standardize LangGraph code around a service-backed node pattern.

Keep the graph layer thin. Put business logic in domain services, keep graph state typed, and make every node return a new state object instead of mutating the incoming one.

## Core Workflow

1. Define a `TypedDict` state for the workflow.
2. Keep domain logic in service functions outside the graph layer.
3. Create LangGraph nodes with a reusable `service_node` factory.
4. Build the graph by wiring small nodes together with `StateGraph`.
5. Add optional LLM nodes as separate adapters that read and append `messages`.

## State Rules

- Use `TypedDict` for graph state.
- Include only orchestration data in state.
- Add `error: str | None` when nodes need to persist failures.
- Prefer concrete types such as `list[str]` or `list[BaseMessage]`.
- Return `{**state, ...}` updates instead of mutating `state`.

## Service Node Pattern

When the user wants reusable service-backed nodes, implement the node layer with this shape:

```python
def service_node(
    service_func: Callable[..., Any],
    input_mapper: Callable[[WorkflowState], dict[str, Any]],
    output_key: str,
) -> Callable[[WorkflowState], WorkflowState]:
    ...
```

The node must:

- derive service inputs from state through `input_mapper`
- call the injected service function
- write the result back under `output_key`
- clear `error` on success
- store `str(exc)` in `error` on failure
- return a fresh state dictionary

Do not put business rules, database access, or API client setup inside the graph definition.

## Graph Assembly Rules

- Build graphs with `StateGraph(<TypedDictState>)`.
- Add nodes with explicit names.
- Keep the required base flow simple:
  - `START -> get_customer_orders -> END`
- If an LLM step is needed, add it as a separate node after the service-backed node.
- Inject dependencies such as `ChatOpenAI` instances into node factories or graph builders. Do not use globals.

## LLM Node Pattern

When the workflow includes LangChain, read from `state["messages"]` and append the model response into a new `messages` list.

- Accept a `BaseChatModel` or `ChatOpenAI` instance as a parameter.
- Call `llm.invoke(state["messages"])`.
- Return a new state with the appended response.
- Reuse the same `error` handling approach as service-backed nodes.

## Output Expectations

When the user asks for implementation, return full working code with clear separation of:

- state
- services
- node factory
- graph setup

Use type hints and docstrings everywhere. Keep functions small and composable. If the user asks for scalability, show how to add more service-backed nodes by reusing the same `service_node` factory.

For the canonical reference implementation, read [references/service-node-pattern.md](references/service-node-pattern.md).
