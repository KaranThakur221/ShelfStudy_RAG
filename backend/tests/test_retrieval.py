from app.services import retrieval_service

def test_retrieval_maps_metadata_to_citation_id(monkeypatch):
    monkeypatch.setattr(retrieval_service, "embed", lambda texts: [[0.1, 0.2]])
    monkeypatch.setattr(retrieval_service.vector_store, "search", lambda *args: {
        "ids":[["doc:0"]], "documents":[["Dijkstra uses a priority queue."]],
        "metadatas":[[{"filename":"graphs.pdf","page":4,"document_id":"doc"}]],
        "distances":[[0.1]],
    })
    sources = retrieval_service.retrieve("Dijkstra")
    assert sources[0]["source_id"] == "S1"
    assert sources[0]["filename"] == "graphs.pdf"
    assert sources[0]["page"] == 4
