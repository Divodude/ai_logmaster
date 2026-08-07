from langgraph.graph import StateGraph

workflow = StateGraph(dict)

workflow.add_node("start", lambda x: x)
# Define the missing node before adding an edge to it
workflow.add_node("missing_node", lambda x: x)

workflow.add_edge("start", "missing_node")

workflow.compile()
