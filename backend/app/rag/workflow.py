"""LangGraph Workflow Assembler."""
from langgraph.graph import StateGraph, END
from app.rag.state import ThreatAnalysisState
from app.rag.nodes import (
    parse_document_node,
    extract_behaviors_node,
    query_neo4j_vector_node,
    filter_and_rank_attack_node,
    traverse_d3fend_graph_node,
    rerank_d3fend_defenses_node,
    synthesize_results_node,
)

def create_threat_rag_graph():
    """Builds and compiles the end-to-end LangGraph state machine."""
    workflow = StateGraph(ThreatAnalysisState)
    
    workflow.add_node("parse_document", parse_document_node)
    workflow.add_node("extract_behaviors", extract_behaviors_node)
    workflow.add_node("query_neo4j_vector", query_neo4j_vector_node)
    workflow.add_node("filter_and_rank_attack", filter_and_rank_attack_node)
    workflow.add_node("traverse_d3fend_graph", traverse_d3fend_graph_node)
    workflow.add_node("rerank_d3fend_defenses", rerank_d3fend_defenses_node)
    workflow.add_node("synthesize_results", synthesize_results_node)
    
    workflow.set_entry_point("parse_document")
    workflow.add_edge("parse_document", "extract_behaviors")
    workflow.add_edge("extract_behaviors", "query_neo4j_vector")
    workflow.add_edge("query_neo4j_vector", "filter_and_rank_attack")
    workflow.add_edge("filter_and_rank_attack", "traverse_d3fend_graph")
    workflow.add_edge("traverse_d3fend_graph", "rerank_d3fend_defenses")
    workflow.add_edge("rerank_d3fend_defenses", "synthesize_results")
    workflow.add_edge("synthesize_results", END)
    
    return workflow.compile()
