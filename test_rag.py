from rag_system import HomeRAGSystem
from logger import load_logs

rag = HomeRAGSystem()
logs = load_logs()
rag.build_index_from_logs(logs)

test_queries = [
    "Who came home?",
    "What happened with the lights?",
    "Did anyone new join the household?",
]

for query in test_queries:
    print(f"\nQuery: {query}")
    results = rag.retrieve_relevant_logs(query, k=2, max_distance=1.5)
    if results:
        for text, dist in results:
            print(f"  → ({dist:.3f}) {text}")
    else:
        print("  → No relevant information found")