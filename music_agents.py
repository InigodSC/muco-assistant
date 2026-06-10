"""
agents/music_agents.py
Agentes especializados: Chords, Theory y Search.
Todos usan AzureChatOpenAI (GPT-4o) via Azure AI Foundry.
"""

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from src.state import MusicAgentState
from src.llm import get_llm
from tools import (
    get_chord_notes,
    get_scale_notes,
    get_genre_progressions,
    transpose_chord_progression,
    get_modes_info,
    search_music_web,
)


# ── Herramientas por agente ──────────────────────────────────────────────────

CHORDS_TOOLS = [get_chord_notes, transpose_chord_progression, get_genre_progressions]
THEORY_TOOLS = [get_scale_notes, get_genre_progressions, get_modes_info, get_chord_notes]
SEARCH_TOOLS = [search_music_web]


# ── System prompts ───────────────────────────────────────────────────────────

CHORDS_SYSTEM = """Eres un experto en acordes y progresiones musicales.
Tu especialidad son:
- Construcción de acordes (tríadas, séptimas, novenas, etc.)
- Progresiones de acordes para cualquier género
- Voicings y disposiciones de acordes
- Transposición de progresiones a cualquier tonalidad
- Sustituciones armónicas (tritono, backcycling, etc.)

Usa las herramientas disponibles cuando necesites datos exactos de notas o progresiones.
Responde en español, de forma clara y musical. Añade contexto armónico cuando sea útil.
Cuando des progresiones, explica brevemente la función de cada acorde."""


THEORY_SYSTEM = """Eres un teórico musical experto con conocimiento profundo de:
- Escalas y modos (griegos, exóticos, bebop, etc.)
- Armonía funcional y modal
- Géneros musicales y sus características armónicas
- Composición y estructura de canciones
- Contrapunto y voiceleading

Usa las herramientas disponibles para datos precisos sobre escalas, modos y progresiones.
Responde en español con rigor académico pero lenguaje accesible.
Da siempre ejemplos concretos con notas reales."""


SEARCH_SYSTEM = """Eres un asistente de investigación musical conectado a internet.
Tu especialidad es encontrar información actualizada sobre:
- Artistas, bandas y su estilo musical
- Técnicas instrumentales avanzadas
- Equipo, guitarras, pedales, DAWs, plugins
- Noticias y lanzamientos musicales recientes
- Historia de géneros y movimientos musicales

Usa la herramienta de búsqueda para obtener información en tiempo real.
Sintetiza la información encontrada de forma útil y musical.
Responde en español, mencionando las fuentes cuando sean relevantes."""


# ── Factory de agentes ───────────────────────────────────────────────────────

def _create_agent_node(system_prompt: str, tools: list, max_iterations: int = 3):
    """
    Factory: crea un nodo agente con sus herramientas y system prompt.
    Usa AzureChatOpenAI con temperatura 0.2 para respuestas más ricas.
    """
    def agent_node(state: MusicAgentState) -> dict:
        llm = get_llm(temperature=0.2)
        llm_with_tools = llm.bind_tools(tools)
        tool_node = ToolNode(tools)

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        current_messages = messages.copy()

        # Loop ReAct: el agente puede encadenar varias tool calls
        for _ in range(max_iterations):
            response = llm_with_tools.invoke(current_messages)
            current_messages.append(response)

            if not response.tool_calls:
                break

            tool_results = tool_node.invoke({"messages": current_messages})
            current_messages.extend(tool_results["messages"])

        # Devolver solo los mensajes nuevos (sin el system prompt inicial)
        final_messages = current_messages[len(messages):]
        return {"messages": final_messages}

    return agent_node


# ── Nodos exportados ─────────────────────────────────────────────────────────

chords_agent_node = _create_agent_node(CHORDS_SYSTEM, CHORDS_TOOLS)
theory_agent_node = _create_agent_node(THEORY_SYSTEM, THEORY_TOOLS)
search_agent_node = _create_agent_node(SEARCH_SYSTEM, SEARCH_TOOLS)
