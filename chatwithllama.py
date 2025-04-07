import os
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = ''
os.environ['LANGCHAIN_PROJECT'] = 'LiveLanggraph'

from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm= ChatGroq(groq_api_key= GROQ_API_KEY, model_name='meta-llama/llama-4-scout-17b-16e-instruct')

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages

    # When defining a graph, the first step is to define its State. 
    # The State includes the graph's schema and reducer functions that handle state updates. 
    # State is a TypedDict with one key: messages. 
    
class State(TypedDict): 
    messages:Annotated[list,add_messages]
    # The add_messages reducer function is used to append new messages to the list instead of overwriting it. 
    # Keys without a reducer annotation will overwrite previous values.

# Initialize the state graph using the State class as the base for transitions
graph_builder = StateGraph(State)

# add a "chatbot" node. Nodes represent units of work. They are typically regular python functions.
# chatbot node function takes the current State as input and returns 
# a dictionary containing an updated messages list under the key "messages". 
# This is the basic pattern for all LangGraph node functions.
def chatbot(state:State):
    return{"messages": llm.invoke(state['messages'])}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever the node is used.
graph_builder.add_node("chatbot",chatbot)

#add an entry point. This tells our graph where to start its work each time we run it.
graph_builder.add_edge(START, "chatbot")

#set a finish point. This instructs the graph "any time this node is run, you can exit."
graph_builder.add_edge("chatbot",END)

#creates a "CompiledGraph" we can use invoke on our state.
graph = graph_builder.compile()

def stream_graph_updates(user_input:str):
   for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
      for value in event.values():
         print("Assitant:", value["messages"].content)

while True:
  try:
    user_input=input("User: ")
    if user_input.lower() in ["quit","q","exit"]:
        print("Good Bye")
        break
    stream_graph_updates(user_input)
  except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break

