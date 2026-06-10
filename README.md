# 🎵 Music Composer Assistant

Agente multi-agente construido con **LangGraph**, **Azure AI Foundry (GPT-4o)** y tracing en **LangSmith**.

## Arquitectura

```
Usuario
  │
  ▼
┌─────────────────────┐
│   Supervisor Agent  │  ← Enruta la intención del usuario
└──────┬──────────────┘
       │
   ┌───┴────────────────────────────────┐
   │            │              │
   ▼            ▼              ▼
Chords       Theory        Search
Agent        Agent         Agent
(acordes,   (escalas,     (SerpAPI /
 progres.)   modos, teoría) Google Search)
```

## Agentes especializados

| Agente | Herramientas |
|--------|-------------|
| **Supervisor** | Enruta con temperatura 0 para máxima consistencia |
| **Chords Agent** | `get_chord_notes`, `transpose_chord_progression`, `get_genre_progressions` |
| **Theory Agent** | `get_scale_notes`, `get_modes_info`, `get_genre_progressions`, `get_chord_notes` |
| **Search Agent** | `search_music_web` (SerpAPI → Google) |

## Features
- ✅ Multi-agente con patrón Supervisor
- ✅ **Azure AI Foundry** — GPT-4o via `AzureChatOpenAI`
- ✅ **SerpAPI** — búsqueda en Google en tiempo real
- ✅ Memoria persistente por sesión (`MemorySaver` + `thread_id`)
- ✅ Tracing automático en **LangSmith**
- ✅ Loop ReAct: cada agente encadena tool calls según necesite

## Setup

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Variables de entorno
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

| Variable | Dónde encontrarla |
|----------|-------------------|
| `AZURE_OPENAI_API_KEY` | Azure Portal → tu recurso → Keys and Endpoint |
| `AZURE_OPENAI_ENDPOINT` | Azure Portal → tu recurso → Keys and Endpoint |
| `AZURE_OPENAI_API_VERSION` | `2024-08-01-preview` (recomendado) |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Azure AI Foundry → Deployments → nombre del deploy |
| `LANGSMITH_API_KEY` | https://smith.langchain.com/ |
| `SERPAPI_API_KEY` | https://serpapi.com/ (100 búsquedas/mes gratis) |

### 3. Ejecutar
```bash
python main.py          # modo interactivo
python main.py --demo   # 5 consultas de ejemplo
python main.py --graph  # muestra el grafo ASCII
```

## Ejemplo de uso

```
🎵 dame una progresión de jazz en Dm
🎵 qué escala usaría sobre esa progresión?
🎵 busca información sobre Bill Evans y su estilo de voicings
🎵 cómo funciona el modo phrygian en flamenco?
🎵 transponer Am-F-C-G a Bm
```
