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

load_dotenv()


def _check_env():
    """Verifica que las variables críticas de Azure y LangSmith estén configuradas."""
    required = {
        "AZURE_OPENAI_API_KEY":       "Azure Portal → tu recurso OpenAI → Keys and Endpoint",
        "AZURE_OPENAI_ENDPOINT":      "Azure Portal → tu recurso OpenAI → Keys and Endpoint",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "Azure AI Foundry → Deployments → nombre del deploy",
        "LANGSMITH_API_KEY":          "https://smith.langchain.com/",
    }
    missing = []
    for var, hint in required.items():
        if not os.getenv(var):
            missing.append(f"  • {var}\n      → {hint}")

    if missing:
        print("⚠️  Variables de entorno no configuradas:\n")
        print("\n".join(missing))
        print("\n💡 Copia .env.example → .env y rellena tus credenciales.")
        sys.exit(1)

    if not os.getenv("SERPAPI_API_KEY"):
        print("⚠️  SERPAPI_API_KEY no configurada → búsqueda web deshabilitada.")
        print("   Consíguelo gratis en: https://serpapi.com/ (100 búsquedas/mes)\n")


def _print_banner():
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    print(f"""
╔══════════════════════════════════════════════════════════╗
║          🎵  Music Composer Assistant  🎵               ║
║                                                          ║
║  Multi-Agent · LangGraph · LangSmith Tracing            ║
║  Modelo: Azure AI Foundry → {deployment:<26}║
║                                                          ║
║  Agentes disponibles:                                    ║
║    🎸 Chords Agent  — acordes, progresiones, voicings    ║
║    🎼 Theory Agent  — escalas, modos, armonía, géneros   ║
║    🔍 Search Agent  — Google Search en tiempo real       ║
║                                                          ║
║  Escribe 'salir' para terminar · 'nuevo' nueva sesión    ║
╚══════════════════════════════════════════════════════════╝
""")


def _run_query(app, query: str, thread_id: str) -> str:
    """Ejecuta una consulta en el grafo y devuelve la respuesta final."""
    config = {"configurable": {"thread_id": thread_id}}

    input_state = {
        "messages": [HumanMessage(content=query)],
        "next": "supervisor",
        "current_topic": "",
    }

    result = app.invoke(input_state, config=config)

    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            if not getattr(msg, "tool_calls", None):
                return msg.content

    return "No se obtuvo respuesta."


def interactive_mode(app):
    _print_banner()
    thread_id = str(uuid.uuid4())[:8]
    project = os.getenv("LANGSMITH_PROJECT", "music-composer-assistant")
    print(f"📌 Sesión: {thread_id}")
    print(f"📊 LangSmith: https://smith.langchain.com/ → proyecto '{project}'\n")

    while True:
        try:
            user_input = input("🎵 Tú: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 ¡Hasta pronto!")
            break

        if not user_input:
            continue
        if user_input.lower() == "salir":
            print("👋 ¡Hasta pronto! 🎶")
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
    print("\n🎬 Modo demo — ejecutando consultas de ejemplo\n")

    demo_queries = [
        ("🎸 Acordes",      "Dame la progresión ii-V-I en Re mayor con acordes de séptima"),
        ("🔀 Transposición", "Transponer la progresión Am - F - C - G a Bm"),
        ("🎼 Teoría",        "Explícame el modo Dorian y para qué géneros es típico"),
        ("📚 Escalas",       "Qué escala usaría para improvisar sobre un blues en La menor?"),
        ("🔍 Búsqueda",      "Busca información sobre las técnicas de voicing de Bill Evans"),
    ]

    thread_id = "demo-session"
    for emoji_title, query in demo_queries:
        print(f"\n{'='*60}\n  {emoji_title}\n  Consulta: {query}\n{'='*60}")
        try:
            print(f"\n{_run_query(app, query, thread_id)}\n")
        except Exception as e:
            print(f"❌ Error: {e}")

    project = os.getenv("LANGSMITH_PROJECT", "music-composer-assistant")
    print(f"\n✅ Demo completada. Ver trazas en LangSmith:")
    print(f"   https://smith.langchain.com/ → proyecto '{project}'")


def print_graph(app):
    print("\n📊 Estructura del grafo:\n")
    try:
        print(app.get_graph().draw_ascii())
    except Exception:
        print("  START → supervisor → chords_agent / theory_agent / search_agent → END")


def main():
    parser = argparse.ArgumentParser(description="Music Composer Assistant")
    parser.add_argument("--demo",     action="store_true", help="Ejecutar consultas de demostración")
    parser.add_argument("--graph",    action="store_true", help="Mostrar estructura del grafo")
    parser.add_argument("--no-check", action="store_true", help="Saltar verificación de env vars")
    args = parser.parse_args()

    if not args.no_check:
        _check_env()

    from src.graph import build_graph
    print("🔧 Construyendo grafo multi-agente (Azure AI Foundry / GPT-4o)...")
    app, _ = build_graph()
    print("✅ Grafo listo.\n")

    if args.graph:
        print_graph(app)
    elif args.demo:
        demo_mode(app)
    else:
        interactive_mode(app)


if __name__ == "__main__":
    main()
