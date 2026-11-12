
from backend.rag.hybrid_retrieval import hybrid_retriever
from backend.rag.reranker import evidence_reranker
from backend.rag.context_builder import context_builder
from backend.agents import summary_generation_agent

query = (
    "What are the current evidence-based approaches "
    "for Type 2 Diabetes management in adults, including "
    "pharmacological treatments, lifestyle interventions, "
    "cardiovascular risk management, and recent clinical "
    "guideline recommendations?"
)

print("\n1. HYBRID RETRIEVAL")

retrieved = hybrid_retriever.search(
    query=query,
    top_k=10
)

print("Retrieved documents:", len(retrieved))

for i, item in enumerate(retrieved[:3], 1):
    print(f"\nDocument {i}")
    print("ID:", item.get("id"))
    print("Text:", item.get("text", "")[:300])
    print("Metadata:", item.get("metadata", {}))


print("\n2. RERANKING")

ranked = evidence_reranker.rerank(
    query=query,
    documents=retrieved,
    top_k=5
)

print("Ranked documents:", len(ranked))

for i, item in enumerate(ranked, 1):
    print(f"\nRank {i}")
    print("Score:", item.get("rerank_score"))
    print("Text:", item.get("text", "")[:200])


print("\n3. CONTEXT BUILDING")

context_result = context_builder.build(
    query=query,
    documents=ranked
)

context = context_result.get("context", "")
citations = context_result.get("citations", [])

print("Context length:", len(context))
print("Citation count:", len(citations))
print("Context preview:", context[:1000])


print("\n4. SUMMARY GENERATION")

summary = summary_generation_agent.run(
    question=query,
    context=context,
    citations=citations,
    safety={}
)

print("Summary success:", summary.get("success"))
print("Findings count:", len(summary.get("findings", [])))
print("Executive summary:", summary.get("executive_summary"))
print("Evidence limitations:", summary.get("evidence_limitations"))
print("Generated findings:")

for finding in summary.get("findings", []):
    print(finding)

print("\n5. DEBUG COMPLETE")
