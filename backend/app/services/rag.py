import re
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from ..schemas import RAGChunk

class VectorRAGIndex:
    """
    RAG Vector Store powered by ChromaDB.
    Chunks resume and job description, indexes them into a ChromaDB collection,
    attaches metadata (source, section, chunk_id), and runs vector distance queries.
    """
    def __init__(self):
        self.chunks: List[RAGChunk] = []
        self.client = chromadb.EphemeralClient(
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = f"interview_rag_{uuid.uuid4().hex[:8]}"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Interview session RAG vectors"}
        )

    def chunk_document(
        self,
        text: str,
        source: str,
        chunk_size: int = 350,
        overlap: int = 60
    ) -> List[RAGChunk]:
        paragraphs = text.split("\n\n")
        chunks: List[RAGChunk] = []
        current_chunk = []
        current_len = 0
        chunk_idx = 0
        current_section = "General"

        section_pattern = re.compile(
            r'^(experience|work experience|employment|education|skills|technical skills|projects|summary|requirements|responsibilities|qualifications)',
            re.IGNORECASE
        )

        for p in paragraphs:
            p_strip = p.strip()
            if not p_strip:
                continue

            first_line = p_strip.split("\n")[0].strip()
            if section_pattern.match(first_line) and len(first_line) < 50:
                current_section = first_line

            words = p_strip.split()
            if current_len + len(words) > chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(
                    RAGChunk(
                        id=f"{source}_{chunk_idx}",
                        source=source,
                        section=current_section,
                        text=chunk_text,
                        score=0.0
                    )
                )
                chunk_idx += 1
                current_chunk = current_chunk[-overlap:] if overlap < len(current_chunk) else []
                current_len = len(current_chunk)

            current_chunk.extend(words)
            current_len += len(words)

        if current_chunk:
            chunks.append(
                RAGChunk(
                    id=f"{source}_{chunk_idx}",
                    source=source,
                    section=current_section,
                    text=" ".join(current_chunk),
                    score=0.0
                )
            )

        return chunks

    def build_index(self, resume_text: str, jd_text: str):
        """Chunk documents and add embeddings into ChromaDB collection."""
        resume_chunks = self.chunk_document(resume_text, source="resume", chunk_size=150, overlap=30)
        jd_chunks = self.chunk_document(jd_text, source="job_description", chunk_size=150, overlap=30)
        
        self.chunks = resume_chunks + jd_chunks
        if not self.chunks:
            return

        documents = [c.text for c in self.chunks]
        ids = [f"doc_{idx}" for idx in range(len(self.chunks))]
        metadatas = [
            {
                "source": c.source,
                "section": c.section or "General",
                "chunk_id": c.id
            }
            for c in self.chunks
        ]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def query(
        self,
        query_text: str,
        source_filter: Optional[str] = None,
        top_k: int = 3
    ) -> List[RAGChunk]:
        """Query ChromaDB vector index with semantic search and optional source filtering."""
        if not self.chunks:
            return []

        where_filter = {"source": source_filter} if source_filter else None
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(top_k, len(self.chunks)),
                where=where_filter
            )

            retrieved: List[RAGChunk] = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else []
                distances = results["distances"][0] if results.get("distances") else []
                
                for idx, doc_text in enumerate(docs):
                    meta = metas[idx] if idx < len(metas) else {}
                    dist = distances[idx] if idx < len(distances) else 1.0
                    sim_score = max(0.0, 1.0 / (1.0 + float(dist)))
                    
                    retrieved.append(
                        RAGChunk(
                            id=meta.get("chunk_id", f"chunk_{idx}"),
                            source=meta.get("source", "resume"),
                            section=meta.get("section", "General"),
                            text=doc_text,
                            score=round(sim_score, 3)
                        )
                    )
                return retrieved
        except Exception as e:
            keywords = [w.lower() for w in re.findall(r'\w+', query_text) if len(w) > 3]
            scored = []
            for c in self.chunks:
                if source_filter and c.source != source_filter:
                    continue
                match_count = sum(1 for kw in keywords if kw in c.text.lower())
                scored.append((match_count, c))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [c for score, c in scored[:top_k]]

        return []

    def extract_key_skills(self) -> Dict[str, List[str]]:
        """Extract matched and distinctive skills across resume and JD, including AI/ML tech."""
        common_tech_terms = [
            # Languages
            "python", "go", "golang", "java", "c++", "rust", "typescript", "javascript", "r",
            # AI / ML / Data
            "pytorch", "tensorflow", "keras", "hugging face", "huggingface", "transformers",
            "langchain", "llamaindex", "rag", "fine-tuning", "lora", "vector database", "chroma",
            "pinecone", "weaviate", "qdrant", "scikit-learn", "pandas", "numpy", "mlops", "onnx",
            # Backend & Web
            "fastapi", "django", "flask", "react", "next.js", "vue", "node.js",
            # Infrastructure & DBs
            "docker", "kubernetes", "aws", "gcp", "azure", "postgresql", "postgres",
            "mysql", "redis", "mongodb", "kafka", "rabbitmq", "graphql", "rest", "grpc",
            # Architecture & QA
            "microservices", "system design", "ci/cd", "terraform", "elasticsearch", "git",
            "pytest", "unit testing", "distributed systems", "caching", "sql"
        ]

        resume_text = " ".join([c.text.lower() for c in self.chunks if c.source == "resume"])
        jd_text = " ".join([c.text.lower() for c in self.chunks if c.source == "job_description"])

        resume_skills = [s for s in common_tech_terms if re.search(rf'\b{re.escape(s)}\b', resume_text)]
        jd_skills = [s for s in common_tech_terms if re.search(rf'\b{re.escape(s)}\b', jd_text)]

        matched = [s for s in jd_skills if s in resume_skills]
        gaps = [s for s in jd_skills if s not in resume_skills]

        return {
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "matched": matched,
            "gaps": gaps
        }
