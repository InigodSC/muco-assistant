"""
src/graph.py
Construcción del grafo multi-agente con LangGraph.

Arquitectura:
    START → supervisor → [chords_agent | theory_agent | search_agent] → END
                              ↑_____________↓
                         (loop: agentes vuelven al supervisor tras responder)
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import MusicAgentState
from agents import (
    supervisor_node,
    route_supervisor,
    chords_agent_node,
    theory_agent_node,
    search_agent_node,
)


def build_graph() -> tuple:
    """
    Construye y compila el grafo multi-agente con memoria persistente.

    Returns:
        (app, checkpointer) - grafo compilado y el MemorySaver para visualizar estado
    """

    # ── 1. Crear el builder ──────────────────────────────────────────────────
    builder = StateGraph(MusicAgentState)

    # ── 2. Añadir nodos ──────────────────────────────────────────────────────
    builder.add_node("supervisor",    supervisor_node)
    builder.add_node("chords_agent",  chords_agent_node)
    builder.add_node("theory_agent",  theory_agent_node)
    builder.add_node("search_agent",  search_agent_node)

    # ── 3. Edges fijos ───────────────────────────────────────────────────────
    # El grafo siempre empieza en el supervisor
    builder.add_edge(START, "supervisor")

    # Después de cada agente especializado, volvemos al supervisor
    # para que pueda manejar el siguiente turno del usuario
    builder.add_edge("chords_agent", END)
    builder.add_edge("theory_agent", END)
    builder.add_edge("search_agent", END)

    # ── 4. Edge condicional desde supervisor ─────────────────────────────────
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "chords_agent": "chords_agent",
            "theory_agent": "theory_agent",
            "search_agent": "search_agent",
            END: END,
        },
    )

    # ── 5. Memoria persistente (checkpointer) ────────────────────────────────
    # MemorySaver guarda el estado por thread_id → permite memoria entre turnos
    checkpointer = MemorySaver()

    # ── 6. Compilar ──────────────────────────────────────────────────────────
    app = builder.compile(checkpointer=checkpointer)

    return app, checkpointer
