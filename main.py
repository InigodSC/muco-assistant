"""
main.py
Punto de entrada del Music Composer Assistant.

Uso:
    python main.py              # modo interactivo
    python main.py --demo       # ejecuta consultas de demostración
    python main.py --graph      # imprime el grafo ASCII
"""

import os
import sys
import uuid
import argparse
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# ── Cargar variables de entorno ──────────────────────────────────────────────
load_dotenv()


def _check_env():
    """Verifica que las variables críticas estén configuradas."""
    required = {
        "ANTHROPIC_API_KEY": "https://console.anthropic.com/",
        "LANGSMITH_API_KEY": "https://smith.langchain.com/",
    }
    missing = []
    for var, url in required.items():
        if not os.getenv(var):
            missing.append(f"  • {var}  →  {url}")

    if missing:
        print("⚠️  Variables de entorno no configuradas:")
        print("\n".join(missing))
        print("\n💡 Copia .env.example → .env y rellena tus API keys.")
        sys.exit(1)

    tavily = os.getenv("TAVILY_API_KEY")
    if not tavily:
        print("⚠️  TAVILY_API_KEY no configurada → la búsqueda web estará deshabilitada.")
        print("   Consíguelo gratis en: https://tavily.com/\n")


def _print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║          🎵  Music Composer Assistant  🎵               ║
║                                                          ║
║  Multi-Agent · LangGraph · LangSmith Tracing            ║
║                                                          ║
║  Agentes disponibles:                                    ║
║    🎸 Chords Agent  — acordes, progresiones, voicings    ║
║    🎼 Theory Agent  — escalas, modos, armonía, géneros   ║
║    🔍 Search Agent  — búsqueda web en tiempo real        ║
║                                                          ║
║  Escribe 'salir' para terminar · 'nuevo' nueva sesión    ║
╚══════════════════════════════════════════════════════════╝
""")


def _run_query(app, query: str, thread_id: str, verbose: bool = False) -> str:
    """Ejecuta una consulta en el grafo y devuelve la respuesta."""
    config = {
        "configurable": {"thread_id": thread_id},
        # LangSmith recoge automáticamente el tracing con las env vars
    }

    input_state = {
        "messages": [HumanMessage(content=query)],
        "next": "supervisor",
        "current_topic": "",
    }

    if verbose:
        print(f"\n🔄 Procesando con thread_id: {thread_id}")

    result = app.invoke(input_state, config=config)

    # Extraer la última respuesta del asistente
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                return msg.content

    return "No se obtuvo respuesta."


def interactive_mode(app):
    """Modo interactivo con memoria de conversación."""
    _print_banner()
    thread_id = str(uuid.uuid4())[:8]
    print(f"📌 Sesión iniciada: {thread_id}")
    print(f"📊 LangSmith: https://smith.langchain.com/ → proyecto '{os.getenv('LANGSMITH_PROJECT', 'music-composer-assistant')}'\n")

    while True:
        try:
            user_input = input("🎵 Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 ¡Hasta pronto!")
            break

        if not user_input:
            continue

        if user_input.lower() == "salir":
            print("👋 ¡Hasta pronto! Que la música te acompañe. 🎶")
            break

        if user_input.lower() == "nuevo":
            thread_id = str(uuid.uuid4())[:8]
            print(f"🔄 Nueva sesión: {thread_id}\n")
            continue

        if user_input.lower() == "sesion":
            print(f"📌 Sesión actual: {thread_id}\n")
            continue

        print("\n⏳ Pensando...\n")
        try:
            response = _run_query(app, user_input, thread_id)
            print(f"🤖 Asistente:\n{response}\n")
            print("─" * 60)
        except Exception as e:
            print(f"❌ Error: {e}\n")


def demo_mode(app):
    """Ejecuta consultas de demostración para mostrar las capacidades."""
    print("\n🎬 Modo demo — ejecutando consultas de ejemplo\n")

    demo_queries = [
        ("🎸 Acordes", "Dame la progresión ii-V-I en Re mayor con acordes de séptima"),
        ("🔀 Transposición", "Transponer la progresión Am - F - C - G a Bm"),
        ("🎼 Teoría", "Explícame el modo Dorian y para qué géneros es típico"),
        ("📚 Escalas", "Qué escala usaría para improvisar sobre un blues en La menor?"),
        ("🔍 Búsqueda", "Busca información sobre las técnicas de voicing de Bill Evans"),
    ]

    thread_id = "demo-session"

    for emoji_title, query in demo_queries:
        print(f"\n{'='*60}")
        print(f"  {emoji_title}")
        print(f"  Consulta: {query}")
        print(f"{'='*60}")

        try:
            response = _run_query(app, query, thread_id)
            print(f"\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

    print(f"\n✅ Demo completada. Ver trazas en LangSmith:")
    print(f"   https://smith.langchain.com/ → proyecto '{os.getenv('LANGSMITH_PROJECT', 'music-composer-assistant')}'")


def print_graph(app):
    """Imprime la representación ASCII del grafo."""
    print("\n📊 Estructura del grafo:\n")
    try:
        print(app.get_graph().draw_ascii())
    except Exception:
        print("""
    START
      │
      ▼
  supervisor  ──────────────────────────────────────┐
      │                                              │
      ├──→ chords_agent ──→ END                     │
      │                                              │
      ├──→ theory_agent ──→ END                     │
      │                                              │
      ├──→ search_agent ──→ END                     │
      │                                              │
      └──→ END (FINISH)                             │
        """)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Music Composer Assistant")
    parser.add_argument("--demo",  action="store_true", help="Ejecutar consultas de demostración")
    parser.add_argument("--graph", action="store_true", help="Mostrar estructura del grafo")
    parser.add_argument("--no-check", action="store_true", help="Saltar verificación de env vars")
    args = parser.parse_args()

    if not args.no_check:
        _check_env()

    # Importar aquí para que los env vars ya estén cargados
    from src.graph import build_graph
    print("🔧 Construyendo grafo multi-agente...")
    app, _ = build_graph()
    print("✅ Grafo listo.\n")

    if args.graph:
        print_graph(app)
        return

    if args.demo:
        demo_mode(app)
    else:
        interactive_mode(app)


if __name__ == "__main__":
    main()
