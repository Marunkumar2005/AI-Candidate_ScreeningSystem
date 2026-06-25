import os
import json
from typing import List, Dict
from app.core.config import settings

# Graceful imports
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = bool(settings.OPENAI_API_KEY)
except ImportError:
    OPENAI_AVAILABLE = False


# Role-specific knowledge snippets (fallback when no PDF books available)
ROLE_KNOWLEDGE = {
    "AI/ML Engineer": [
        "Supervised learning involves training a model on labeled data. Common algorithms include linear regression, logistic regression, decision trees, random forests, and support vector machines. The model learns to map inputs to outputs based on training examples.",
        "Neural networks are composed of layers of interconnected nodes. Deep learning uses multiple hidden layers to learn hierarchical representations. Backpropagation computes gradients to update weights via gradient descent.",
        "Overfitting occurs when a model learns noise in training data and fails to generalize. Techniques to combat overfitting include regularization (L1/L2), dropout, early stopping, and cross-validation.",
        "The bias-variance tradeoff describes the balance between underfitting (high bias) and overfitting (high variance). A good model achieves low bias and low variance through proper model selection and regularization.",
        "Retrieval-Augmented Generation (RAG) combines a retrieval system with a generative model. Documents are embedded into a vector space; at query time, relevant chunks are retrieved and provided as context to the LLM.",
        "Transformers use self-attention mechanisms to model relationships between all tokens in a sequence. BERT uses bidirectional attention for understanding; GPT uses causal attention for generation.",
        "Embeddings are dense vector representations of text in a high-dimensional space. Similar concepts have similar vectors. Word2Vec, GloVe, and transformer-based embeddings like sentence-transformers are common approaches.",
        "Cross-validation splits data into k folds, training on k-1 and validating on 1, rotating through all folds. This provides a better estimate of model performance on unseen data.",
        "Feature engineering transforms raw data into informative features. Techniques include normalization, one-hot encoding, polynomial features, and domain-specific transformations.",
        "Gradient descent minimizes the loss function by iteratively updating parameters in the direction of the negative gradient. Variants include SGD, Adam, RMSProp, and AdaGrad with different learning rate schedules.",
        "Convolutional Neural Networks (CNNs) use convolution operations to detect spatial patterns in data like images. Pooling layers reduce dimensionality while preserving important features.",
        "Recurrent Neural Networks (RNNs) process sequential data by maintaining hidden state. LSTMs and GRUs solve the vanishing gradient problem using gating mechanisms.",
        "Clustering algorithms like K-means, DBSCAN, and hierarchical clustering group similar data points without labels. The number of clusters k is a key hyperparameter in K-means.",
        "Principal Component Analysis (PCA) reduces dimensionality by projecting data onto principal components that capture maximum variance. Useful for visualization and reducing computational cost.",
        "Reinforcement learning trains agents to maximize cumulative reward through environment interaction. Key concepts: state, action, reward, policy, value function, Q-learning, and policy gradients.",
    ],
    "Backend Engineer": [
        "RESTful APIs follow principles including statelessness, uniform interface, and resource-based URLs. HTTP methods GET, POST, PUT, PATCH, DELETE correspond to CRUD operations.",
        "Microservices architecture decomposes applications into small, independent services. Each service owns its data, communicates via APIs, and can be deployed independently.",
        "Database indexing improves query performance by creating data structures that allow faster lookups. B-tree indexes are common; composite indexes cover multiple columns.",
        "Caching strategies include cache-aside, read-through, write-through, and write-behind. Redis and Memcached are popular in-memory caching solutions for reducing database load.",
        "Message queues like RabbitMQ and Kafka enable asynchronous communication between services. Producers publish messages; consumers process them independently, improving resilience and scalability.",
        "SQL vs NoSQL: relational databases enforce ACID properties and are great for structured data with relationships. NoSQL databases sacrifice some ACID guarantees for scalability and flexibility.",
        "Authentication with JWT tokens: the server issues a signed token containing claims. The client sends it with requests. The server validates the signature without storing session state.",
        "Docker containers package applications with dependencies for consistent environments. Kubernetes orchestrates containers at scale with features like auto-scaling, service discovery, and rolling updates.",
        "Database transactions ensure ACID properties: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don't interfere), Durability (committed data persists).",
        "Rate limiting protects APIs from abuse and overload. Algorithms include token bucket, leaky bucket, and sliding window. Implementation can be done in middleware or API gateways.",
    ],
    "Data Scientist": [
        "Exploratory Data Analysis (EDA) involves summarizing data characteristics using statistics and visualization. Key steps: check distributions, identify outliers, explore correlations, and understand missing values.",
        "Feature selection methods include filter methods (correlation, chi-square), wrapper methods (recursive feature elimination), and embedded methods (LASSO regularization).",
        "A/B testing compares two versions of a feature by randomly assigning users. Statistical significance is measured using t-tests or chi-square tests with a significance threshold (p < 0.05).",
        "Pandas DataFrames provide powerful data manipulation: groupby aggregations, merge/join operations, pivot tables, and vectorized operations. Understanding memory usage is key for large datasets.",
        "Data pipeline design involves ingestion, transformation, validation, and loading steps. Tools like Apache Airflow, dbt, and Spark are used for orchestration and large-scale processing.",
    ],
    "Full Stack Engineer": [
        "React's component-based architecture enables reusable UI elements. State management with hooks (useState, useReducer) and context API. For complex state, libraries like Redux or Zustand are used.",
        "TypeScript adds static typing to JavaScript, catching errors at compile time. Interfaces define object shapes; generics enable reusable type-safe code.",
        "Web performance optimization: code splitting, lazy loading, image optimization, CDN usage, browser caching headers, and minimizing render-blocking resources.",
        "GraphQL provides a query language for APIs where clients specify exactly what data they need. Reduces over-fetching and under-fetching compared to REST.",
        "CI/CD pipelines automate testing and deployment. GitHub Actions, Jenkins, and GitLab CI run tests on each push and deploy on merge to main branch.",
    ],
    "Frontend Engineer": [
        "CSS Flexbox and Grid provide powerful layout mechanisms. Flexbox is best for one-dimensional layouts; Grid excels at two-dimensional layouts with rows and columns.",
        "Web accessibility (a11y) ensures applications work for all users. Key principles: semantic HTML, ARIA attributes, keyboard navigation, sufficient color contrast, and screen reader support.",
        "Browser rendering pipeline: JavaScript → Style → Layout → Paint → Composite. Understanding this pipeline helps optimize performance and avoid layout thrashing.",
        "State management in React: local state (useState), context for shared state, and external libraries (Redux, Zustand, Jotai) for complex global state management.",
        "Web performance metrics: Core Web Vitals include LCP (Largest Contentful Paint), FID (First Input Delay), and CLS (Cumulative Layout Shift). Tools: Lighthouse, WebPageTest.",
    ]
}


class RAGService:
    def __init__(self):
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        if not CHROMA_AVAILABLE:
            return
        try:
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            ef = embedding_functions.DefaultEmbeddingFunction()
            self.collection = self.client.get_or_create_collection(
                name="interview_knowledge",
                embedding_function=ef
            )
            self._seed_knowledge_base()
        except Exception as e:
            print(f"ChromaDB init error: {e}")
            self.client = None

    def _seed_knowledge_base(self):
        if self.collection is None:
            return
        try:
            existing = self.collection.count()
            if existing > 0:
                return
            docs, ids, metas = [], [], []
            for role, chunks in ROLE_KNOWLEDGE.items():
                for i, chunk in enumerate(chunks):
                    docs.append(chunk)
                    ids.append(f"{role}_{i}")
                    metas.append({"role": role, "chunk_index": i})
            if docs:
                self.collection.add(documents=docs, ids=ids, metadatas=metas)
        except Exception as e:
            print(f"Seeding error: {e}")

    def retrieve_context(self, query: str, role: str, n_results: int = None) -> List[str]:
        n = n_results or settings.TOP_K_RETRIEVAL
        if self.collection is not None:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=min(n, self.collection.count()),
                    where={"role": role} if role in ROLE_KNOWLEDGE else None
                )
                if results and results["documents"]:
                    return results["documents"][0]
            except Exception as e:
                print(f"Retrieval error: {e}")
        # Fallback: return first N chunks from role knowledge
        chunks = ROLE_KNOWLEDGE.get(role, ROLE_KNOWLEDGE["AI/ML Engineer"])
        return chunks[:n]

    def build_query(self, skills: List[str], technologies: List[str], role: str) -> str:
        parts = [f"interview questions for {role}"]
        if skills:
            parts.append(f"skills: {', '.join(skills[:5])}")
        if technologies:
            parts.append(f"technologies: {', '.join(technologies[:5])}")
        return ". ".join(parts)


rag_service = RAGService()
