from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langsmith import traceable

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
checkpointer = InMemorySaver()


@traceable
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_react_agent(
    model=model,
    checkpointer=checkpointer,
    tools=[get_weather],
)
