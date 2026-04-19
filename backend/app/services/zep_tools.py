"""
Zep retrieval tool service.
Wraps graph search, node reading, and edge querying for use by the Report Agent.

Core retrieval tools:
1. InsightForge (deep-insight retrieval) — most powerful; auto-generates sub-questions
   and retrieves across multiple dimensions.
2. PanoramaSearch (broad search) — fetches the full picture, including expired content.
3. QuickSearch (simple search) — fast, lightweight retrieval.
"""

import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from zep_cloud.client import Zep

from ..config import Config
from ..utils.logger import get_logger
from ..utils.llm_client import LLMClient
from ..utils.locale import t
from ..utils.zep_paging import fetch_all_nodes, fetch_all_edges

logger = get_logger('bigbrother.zep_tools')


@dataclass
class SearchResult:
    """Search result."""
    facts: List[str]
    edges: List[Dict[str, Any]]
    nodes: List[Dict[str, Any]]
    query: str
    total_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "facts": self.facts,
            "edges": self.edges,
            "nodes": self.nodes,
            "query": self.query,
            "total_count": self.total_count
        }
    
    def to_text(self) -> str:
        """Convert to text format for LLM consumption."""
        text_parts = [f"Search query: {self.query}", f"Found {self.total_count} relevant entries"]

        if self.facts:
            text_parts.append("\n### Related facts:")
            for i, fact in enumerate(self.facts, 1):
                text_parts.append(f"{i}. {fact}")

        return "\n".join(text_parts)


@dataclass
class NodeInfo:
    """Node information."""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "labels": self.labels,
            "summary": self.summary,
            "attributes": self.attributes
        }
    
    def to_text(self) -> str:
        """Convert to text format."""
        entity_type = next((l for l in self.labels if l not in ["Entity", "Node"]), "unknown")
        return f"Entity: {self.name} (type: {entity_type})\nSummary: {self.summary}"


@dataclass
class EdgeInfo:
    """Edge information."""
    uuid: str
    name: str
    fact: str
    source_node_uuid: str
    target_node_uuid: str
    source_node_name: Optional[str] = None
    target_node_name: Optional[str] = None
    # Temporal metadata
    created_at: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    expired_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "fact": self.fact,
            "source_node_uuid": self.source_node_uuid,
            "target_node_uuid": self.target_node_uuid,
            "source_node_name": self.source_node_name,
            "target_node_name": self.target_node_name,
            "created_at": self.created_at,
            "valid_at": self.valid_at,
            "invalid_at": self.invalid_at,
            "expired_at": self.expired_at
        }
    
    def to_text(self, include_temporal: bool = False) -> str:
        """Convert to text format."""
        source = self.source_node_name or self.source_node_uuid[:8]
        target = self.target_node_name or self.target_node_uuid[:8]
        base_text = f"Relationship: {source} --[{self.name}]--> {target}\nFact: {self.fact}"

        if include_temporal:
            valid_at = self.valid_at or "unknown"
            invalid_at = self.invalid_at or "present"
            base_text += f"\nValid: {valid_at} - {invalid_at}"
            if self.expired_at:
                base_text += f" (expired: {self.expired_at})"

        return base_text

    @property
    def is_expired(self) -> bool:
        """Whether the edge has expired."""
        return self.expired_at is not None

    @property
    def is_invalid(self) -> bool:
        """Whether the edge has been invalidated."""
        return self.invalid_at is not None


@dataclass
class InsightForgeResult:
    """
    Deep-insight retrieval result (InsightForge).
    Contains multi-dimensional retrieval results across several sub-questions.
    """
    query: str
    simulation_requirement: str
    sub_queries: List[str]

    # Per-dimension retrieval results
    semantic_facts: List[str] = field(default_factory=list)       # Semantic search results
    entity_insights: List[Dict[str, Any]] = field(default_factory=list)  # Entity insights
    relationship_chains: List[str] = field(default_factory=list)  # Relationship chains

    # Statistics
    total_facts: int = 0
    total_entities: int = 0
    total_relationships: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "simulation_requirement": self.simulation_requirement,
            "sub_queries": self.sub_queries,
            "semantic_facts": self.semantic_facts,
            "entity_insights": self.entity_insights,
            "relationship_chains": self.relationship_chains,
            "total_facts": self.total_facts,
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships
        }
    
    def to_text(self) -> str:
        """Convert to detailed text format for LLM consumption."""
        text_parts = [
            f"## Deep Forecast Analysis",
            f"Query: {self.query}",
            f"Forecast scenario: {self.simulation_requirement}",
            f"\n### Statistics",
            f"- Related forecast facts: {self.total_facts}",
            f"- Entities involved: {self.total_entities}",
            f"- Relationship chains: {self.total_relationships}",
        ]

        # Sub-questions
        if self.sub_queries:
            text_parts.append(f"\n### Sub-questions Analysed")
            for i, sq in enumerate(self.sub_queries, 1):
                text_parts.append(f"{i}. {sq}")

        # Semantic search results
        if self.semantic_facts:
            text_parts.append(f"\n### [Key Facts] (quote these verbatim in the report)")
            for i, fact in enumerate(self.semantic_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")

        # Entity insights
        if self.entity_insights:
            text_parts.append(f"\n### [Core Entities]")
            for entity in self.entity_insights:
                text_parts.append(f"- **{entity.get('name', 'Unknown')}** ({entity.get('type', 'Entity')})")
                if entity.get('summary'):
                    text_parts.append(f"  Summary: \"{entity.get('summary')}\"")
                if entity.get('related_facts'):
                    text_parts.append(f"  Related facts: {len(entity.get('related_facts', []))}")

        # Relationship chains
        if self.relationship_chains:
            text_parts.append(f"\n### [Relationship Chains]")
            for chain in self.relationship_chains:
                text_parts.append(f"- {chain}")

        return "\n".join(text_parts)


@dataclass
class PanoramaResult:
    """
    Broad search result (Panorama).
    Contains all related information including expired/historical content.
    """
    query: str

    # All nodes
    all_nodes: List[NodeInfo] = field(default_factory=list)
    # All edges (including expired ones)
    all_edges: List[EdgeInfo] = field(default_factory=list)
    # Currently active facts
    active_facts: List[str] = field(default_factory=list)
    # Expired / invalidated facts (historical record)
    historical_facts: List[str] = field(default_factory=list)

    # Statistics
    total_nodes: int = 0
    total_edges: int = 0
    active_count: int = 0
    historical_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "all_nodes": [n.to_dict() for n in self.all_nodes],
            "all_edges": [e.to_dict() for e in self.all_edges],
            "active_facts": self.active_facts,
            "historical_facts": self.historical_facts,
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "active_count": self.active_count,
            "historical_count": self.historical_count
        }
    
    def to_text(self) -> str:
        """Convert to text format (complete, untruncated)."""
        text_parts = [
            f"## Broad Search Results (Full Panorama View)",
            f"Query: {self.query}",
            f"\n### Statistics",
            f"- Total nodes: {self.total_nodes}",
            f"- Total edges: {self.total_edges}",
            f"- Active facts: {self.active_count}",
            f"- Historical / expired facts: {self.historical_count}",
        ]

        # Active facts (complete, untruncated)
        if self.active_facts:
            text_parts.append(f"\n### [Active Facts] (simulation results verbatim)")
            for i, fact in enumerate(self.active_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")

        # Historical / expired facts (complete, untruncated)
        if self.historical_facts:
            text_parts.append(f"\n### [Historical / Expired Facts] (change log)")
            for i, fact in enumerate(self.historical_facts, 1):
                text_parts.append(f"{i}. \"{fact}\"")

        # Key entities (complete, untruncated)
        if self.all_nodes:
            text_parts.append(f"\n### [Entities Involved]")
            for node in self.all_nodes:
                entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "Entity")
                text_parts.append(f"- **{node.name}** ({entity_type})")

        return "\n".join(text_parts)


@dataclass
class AgentInterview:
    """Single-agent interview result."""
    agent_name: str
    agent_role: str  # Role type (e.g. student, teacher, media, etc.)
    agent_bio: str   # Short biography
    question: str    # Interview question(s)
    response: str    # Interview response
    key_quotes: List[str] = field(default_factory=list)  # Key quotes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "agent_bio": self.agent_bio,
            "question": self.question,
            "response": self.response,
            "key_quotes": self.key_quotes
        }
    
    def to_text(self) -> str:
        text = f"**{self.agent_name}** ({self.agent_role})\n"
        # Show full agent bio, untruncated
        text += f"_Bio: {self.agent_bio}_\n\n"
        text += f"**Q:** {self.question}\n\n"
        text += f"**A:** {self.response}\n"
        if self.key_quotes:
            text += "\n**Key quotes:**\n"
            for quote in self.key_quotes:
                # Strip various quotation mark styles
                clean_quote = quote.replace('\u201c', '').replace('\u201d', '').replace('"', '')
                clean_quote = clean_quote.replace('\u300c', '').replace('\u300d', '')
                clean_quote = clean_quote.strip()
                # Remove leading punctuation
                while clean_quote and clean_quote[0] in '，,；;：:、。！？\n\r\t ':
                    clean_quote = clean_quote[1:]
                # Skip junk content containing question numbers (Chinese: 问题1-9)
                skip = False
                for d in '123456789':
                    if f'\u95ee\u9898{d}' in clean_quote:
                        skip = True
                        break
                if skip:
                    continue
                # Truncate overly long content at a sentence boundary rather than cutting hard
                if len(clean_quote) > 150:
                    dot_pos = clean_quote.find('\u3002', 80)
                    if dot_pos > 0:
                        clean_quote = clean_quote[:dot_pos + 1]
                    else:
                        clean_quote = clean_quote[:147] + "..."
                if clean_quote and len(clean_quote) >= 10:
                    text += f'> "{clean_quote}"\n'
        return text


@dataclass
class InterviewResult:
    """
    Interview result.
    Contains responses from multiple simulated agents.
    """
    interview_topic: str             # Interview topic
    interview_questions: List[str]   # Interview question list

    # Agents selected for the interview
    selected_agents: List[Dict[str, Any]] = field(default_factory=list)
    # Per-agent interview responses
    interviews: List[AgentInterview] = field(default_factory=list)

    # Rationale for selecting the agents
    selection_reasoning: str = ""
    # Synthesised interview summary
    summary: str = ""

    # Statistics
    total_agents: int = 0
    interviewed_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_topic": self.interview_topic,
            "interview_questions": self.interview_questions,
            "selected_agents": self.selected_agents,
            "interviews": [i.to_dict() for i in self.interviews],
            "selection_reasoning": self.selection_reasoning,
            "summary": self.summary,
            "total_agents": self.total_agents,
            "interviewed_count": self.interviewed_count
        }
    
    def to_text(self) -> str:
        """Convert to detailed text format for LLM consumption and report citation."""
        text_parts = [
            "## In-Depth Interview Report",
            f"**Topic:** {self.interview_topic}",
            f"**Interviewed:** {self.interviewed_count} / {self.total_agents} simulated agents",
            "\n### Agent Selection Rationale",
            self.selection_reasoning or "(selected automatically)",
            "\n---",
            "\n### Interview Transcripts",
        ]

        if self.interviews:
            for i, interview in enumerate(self.interviews, 1):
                text_parts.append(f"\n#### Interview #{i}: {interview.agent_name}")
                text_parts.append(interview.to_text())
                text_parts.append("\n---")
        else:
            text_parts.append("(no interview records)\n\n---")

        text_parts.append("\n### Interview Summary and Key Perspectives")
        text_parts.append(self.summary or "(no summary)")

        return "\n".join(text_parts)


class ZepToolsService:
    """
    Zep retrieval tool service.

    Core retrieval tools:
    1. insight_forge      — most powerful; auto-generates sub-questions and
                            retrieves across multiple dimensions.
    2. panorama_search    — broad search that fetches the full picture,
                            including expired/historical content.
    3. quick_search       — fast, lightweight retrieval.
    4. interview_agents   — interviews simulated agents for multi-perspective views.

    Foundation tools:
    - search_graph         — graph semantic search
    - get_all_nodes        — fetch all nodes in the graph
    - get_all_edges        — fetch all edges (with temporal metadata)
    - get_node_detail      — fetch a single node's details
    - get_node_edges       — fetch edges related to a node
    - get_entities_by_type — fetch entities filtered by type label
    - get_entity_summary   — fetch a relationship summary for an entity
    """

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0
    
    def __init__(self, api_key: Optional[str] = None, llm_client: Optional[LLMClient] = None):
        self.api_key = api_key or Config.ZEP_API_KEY
        if not self.api_key:
            raise ValueError("ZEP_API_KEY is not configured")

        self.client = Zep(api_key=self.api_key)
        # LLM client used by InsightForge to generate sub-questions
        self._llm_client = llm_client
        logger.info(t("console.zepToolsInitialized"))
    
    @property
    def llm(self) -> LLMClient:
        """Lazily initialise the LLM client."""
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client
    
    def _call_with_retry(self, func, operation_name: str, max_retries: int = None):
        """API call with retry logic."""
        max_retries = max_retries or self.MAX_RETRIES
        last_exception = None
        delay = self.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(
                        t("console.zepRetryAttempt", operation=operation_name, attempt=attempt + 1, error=str(e)[:100], delay=f"{delay:.1f}")
                    )
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(t("console.zepAllRetriesFailed", operation=operation_name, retries=max_retries, error=str(e)))
        
        raise last_exception
    
    def search_graph(
        self,
        graph_id: str,
        query: str,
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        Graph semantic search.

        Uses hybrid search (semantic + BM25) to find relevant information in
        the graph.  Falls back to local keyword matching if the Zep Cloud
        search API is unavailable.

        Args:
            graph_id: Graph ID (Standalone Graph)
            query: Search query
            limit: Maximum number of results to return
            scope: Search scope — "edges" or "nodes"

        Returns:
            SearchResult
        """
        logger.info(t("console.graphSearch", graphId=graph_id, query=query[:50]))
        
        # Try the Zep Cloud Search API first
        try:
            search_results = self._call_with_retry(
                func=lambda: self.client.graph.search(
                    graph_id=graph_id,
                    query=query,
                    limit=limit,
                    scope=scope,
                    reranker="cross_encoder"
                ),
                operation_name=t("console.graphSearchOp", graphId=graph_id)
            )
            
            facts = []
            edges = []
            nodes = []
            
            # Parse edge search results
            if hasattr(search_results, 'edges') and search_results.edges:
                for edge in search_results.edges:
                    if hasattr(edge, 'fact') and edge.fact:
                        facts.append(edge.fact)
                    edges.append({
                        "uuid": getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', ''),
                        "name": getattr(edge, 'name', ''),
                        "fact": getattr(edge, 'fact', ''),
                        "source_node_uuid": getattr(edge, 'source_node_uuid', ''),
                        "target_node_uuid": getattr(edge, 'target_node_uuid', ''),
                    })
            
            # Parse node search results
            if hasattr(search_results, 'nodes') and search_results.nodes:
                for node in search_results.nodes:
                    nodes.append({
                        "uuid": getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                        "name": getattr(node, 'name', ''),
                        "labels": getattr(node, 'labels', []),
                        "summary": getattr(node, 'summary', ''),
                    })
                    # Node summaries are also treated as facts
                    if hasattr(node, 'summary') and node.summary:
                        facts.append(f"[{node.name}]: {node.summary}")
            
            logger.info(t("console.searchComplete", count=len(facts)))
            
            return SearchResult(
                facts=facts,
                edges=edges,
                nodes=nodes,
                query=query,
                total_count=len(facts)
            )
            
        except Exception as e:
            logger.warning(t("console.zepSearchApiFallback", error=str(e)))
            # Fallback: local keyword matching
            return self._local_search(graph_id, query, limit, scope)

    def _local_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10,
        scope: str = "edges"
    ) -> SearchResult:
        """
        Local keyword-matching search (fallback when Zep Search API is unavailable).

        Fetches all edges / nodes and matches them locally.

        Args:
            graph_id: Graph ID
            query: Search query
            limit: Maximum number of results
            scope: Search scope

        Returns:
            SearchResult
        """
        logger.info(t("console.usingLocalSearch", query=query[:30]))
        
        facts = []
        edges_result = []
        nodes_result = []
        
        # Extract query keywords (simple tokenisation)
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def match_score(text: str) -> int:
            """Compute how well a text matches the query."""
            if not text:
                return 0
            text_lower = text.lower()
            # Full query match
            if query_lower in text_lower:
                return 100
            # Keyword match
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 10
            return score

        try:
            if scope in ["edges", "both"]:
                # Fetch all edges and score them
                all_edges = self.get_all_edges(graph_id)
                scored_edges = []
                for edge in all_edges:
                    score = match_score(edge.fact) + match_score(edge.name)
                    if score > 0:
                        scored_edges.append((score, edge))
                
                # Sort by score
                scored_edges.sort(key=lambda x: x[0], reverse=True)
                
                for score, edge in scored_edges[:limit]:
                    if edge.fact:
                        facts.append(edge.fact)
                    edges_result.append({
                        "uuid": edge.uuid,
                        "name": edge.name,
                        "fact": edge.fact,
                        "source_node_uuid": edge.source_node_uuid,
                        "target_node_uuid": edge.target_node_uuid,
                    })
            
            if scope in ["nodes", "both"]:
                # Fetch all nodes and score them
                all_nodes = self.get_all_nodes(graph_id)
                scored_nodes = []
                for node in all_nodes:
                    score = match_score(node.name) + match_score(node.summary)
                    if score > 0:
                        scored_nodes.append((score, node))
                
                scored_nodes.sort(key=lambda x: x[0], reverse=True)
                
                for score, node in scored_nodes[:limit]:
                    nodes_result.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "labels": node.labels,
                        "summary": node.summary,
                    })
                    if node.summary:
                        facts.append(f"[{node.name}]: {node.summary}")
            
            logger.info(t("console.localSearchComplete", count=len(facts)))
            
        except Exception as e:
            logger.error(t("console.localSearchFailed", error=str(e)))
        
        return SearchResult(
            facts=facts,
            edges=edges_result,
            nodes=nodes_result,
            query=query,
            total_count=len(facts)
        )
    
    def get_all_nodes(self, graph_id: str) -> List[NodeInfo]:
        """
        Fetch all nodes in the graph (paginated).

        Args:
            graph_id: Graph ID

        Returns:
            List of NodeInfo objects
        """
        logger.info(t("console.fetchingAllNodes", graphId=graph_id))

        nodes = fetch_all_nodes(self.client, graph_id)

        result = []
        for node in nodes:
            node_uuid = getattr(node, 'uuid_', None) or getattr(node, 'uuid', None) or ""
            result.append(NodeInfo(
                uuid=str(node_uuid) if node_uuid else "",
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            ))

        logger.info(t("console.fetchedNodes", count=len(result)))
        return result

    def get_all_edges(self, graph_id: str, include_temporal: bool = True) -> List[EdgeInfo]:
        """
        Fetch all edges in the graph (paginated, with temporal metadata).

        Args:
            graph_id: Graph ID
            include_temporal: Whether to include temporal fields (default True)

        Returns:
            List of EdgeInfo objects (includes created_at, valid_at,
            invalid_at, expired_at)
        """
        logger.info(t("console.fetchingAllEdges", graphId=graph_id))

        edges = fetch_all_edges(self.client, graph_id)

        result = []
        for edge in edges:
            edge_uuid = getattr(edge, 'uuid_', None) or getattr(edge, 'uuid', None) or ""
            edge_info = EdgeInfo(
                uuid=str(edge_uuid) if edge_uuid else "",
                name=edge.name or "",
                fact=edge.fact or "",
                source_node_uuid=edge.source_node_uuid or "",
                target_node_uuid=edge.target_node_uuid or ""
            )

            # Populate temporal fields
            if include_temporal:
                edge_info.created_at = getattr(edge, 'created_at', None)
                edge_info.valid_at = getattr(edge, 'valid_at', None)
                edge_info.invalid_at = getattr(edge, 'invalid_at', None)
                edge_info.expired_at = getattr(edge, 'expired_at', None)

            result.append(edge_info)

        logger.info(t("console.fetchedEdges", count=len(result)))
        return result
    
    def get_node_detail(self, node_uuid: str) -> Optional[NodeInfo]:
        """
        Fetch detailed information for a single node.

        Args:
            node_uuid: Node UUID

        Returns:
            NodeInfo or None
        """
        logger.info(t("console.fetchingNodeDetail", uuid=node_uuid[:8]))
        
        try:
            node = self._call_with_retry(
                func=lambda: self.client.graph.node.get(uuid_=node_uuid),
                operation_name=t("console.fetchNodeDetailOp", uuid=node_uuid[:8])
            )
            
            if not node:
                return None
            
            return NodeInfo(
                uuid=getattr(node, 'uuid_', None) or getattr(node, 'uuid', ''),
                name=node.name or "",
                labels=node.labels or [],
                summary=node.summary or "",
                attributes=node.attributes or {}
            )
        except Exception as e:
            logger.error(t("console.fetchNodeDetailFailed", error=str(e)))
            return None
    
    def get_node_edges(self, graph_id: str, node_uuid: str) -> List[EdgeInfo]:
        """
        Fetch all edges related to a given node.

        Retrieves all graph edges and filters to those involving the node
        as either source or target.

        Args:
            graph_id: Graph ID
            node_uuid: Node UUID

        Returns:
            List of EdgeInfo objects
        """
        logger.info(t("console.fetchingNodeEdges", uuid=node_uuid[:8]))
        
        try:
            # Fetch all graph edges, then filter
            all_edges = self.get_all_edges(graph_id)

            result = []
            for edge in all_edges:
                # Keep edges where this node is either the source or the target
                if edge.source_node_uuid == node_uuid or edge.target_node_uuid == node_uuid:
                    result.append(edge)
            
            logger.info(t("console.foundNodeEdges", count=len(result)))
            return result
            
        except Exception as e:
            logger.warning(t("console.fetchNodeEdgesFailed", error=str(e)))
            return []
    
    def get_entities_by_type(
        self,
        graph_id: str,
        entity_type: str
    ) -> List[NodeInfo]:
        """
        Fetch all entities of a given type.

        Args:
            graph_id: Graph ID
            entity_type: Entity type label (e.g. "Student", "PublicFigure")

        Returns:
            List of matching NodeInfo objects
        """
        logger.info(t("console.fetchingEntitiesByType", type=entity_type))
        
        all_nodes = self.get_all_nodes(graph_id)
        
        filtered = []
        for node in all_nodes:
            # Keep nodes whose labels include the requested type
            if entity_type in node.labels:
                filtered.append(node)
        
        logger.info(t("console.foundEntitiesByType", count=len(filtered), type=entity_type))
        return filtered
    
    def get_entity_summary(
        self,
        graph_id: str,
        entity_name: str
    ) -> Dict[str, Any]:
        """
        Fetch a relationship summary for a named entity.

        Searches for all information related to the entity and assembles
        a summary dictionary.

        Args:
            graph_id: Graph ID
            entity_name: Entity name

        Returns:
            Entity summary dictionary
        """
        logger.info(t("console.fetchingEntitySummary", name=entity_name))
        
        # Search for information related to this entity
        search_result = self.search_graph(
            graph_id=graph_id,
            query=entity_name,
            limit=20
        )
        
        # Locate the entity node in the full node list
        all_nodes = self.get_all_nodes(graph_id)
        entity_node = None
        for node in all_nodes:
            if node.name.lower() == entity_name.lower():
                entity_node = node
                break
        
        related_edges = []
        if entity_node:
            related_edges = self.get_node_edges(graph_id, entity_node.uuid)
        
        return {
            "entity_name": entity_name,
            "entity_info": entity_node.to_dict() if entity_node else None,
            "related_facts": search_result.facts,
            "related_edges": [e.to_dict() for e in related_edges],
            "total_relations": len(related_edges)
        }
    
    def get_graph_statistics(self, graph_id: str) -> Dict[str, Any]:
        """
        Fetch summary statistics for the graph.

        Args:
            graph_id: Graph ID

        Returns:
            Statistics dictionary
        """
        logger.info(t("console.fetchingGraphStats", graphId=graph_id))
        
        nodes = self.get_all_nodes(graph_id)
        edges = self.get_all_edges(graph_id)
        
        # Count entity type distribution
        entity_types = {}
        for node in nodes:
            for label in node.labels:
                if label not in ["Entity", "Node"]:
                    entity_types[label] = entity_types.get(label, 0) + 1

        # Count relationship type distribution
        relation_types = {}
        for edge in edges:
            relation_types[edge.name] = relation_types.get(edge.name, 0) + 1
        
        return {
            "graph_id": graph_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "entity_types": entity_types,
            "relation_types": relation_types
        }
    
    def get_simulation_context(
        self,
        graph_id: str,
        simulation_requirement: str,
        limit: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch context information relevant to the simulation.

        Performs a comprehensive search for all information related to the
        simulation requirement.

        Args:
            graph_id: Graph ID
            simulation_requirement: Simulation requirement description
            limit: Maximum number of items per category

        Returns:
            Simulation context dictionary
        """
        logger.info(t("console.fetchingSimContext", requirement=simulation_requirement[:50]))
        
        # Search for information related to the simulation requirement
        search_result = self.search_graph(
            graph_id=graph_id,
            query=simulation_requirement,
            limit=limit
        )
        
        # Graph statistics
        stats = self.get_graph_statistics(graph_id)

        # All entity nodes
        all_nodes = self.get_all_nodes(graph_id)

        # Filter to nodes with a custom type label (non-generic Entity nodes)
        entities = []
        for node in all_nodes:
            custom_labels = [l for l in node.labels if l not in ["Entity", "Node"]]
            if custom_labels:
                entities.append({
                    "name": node.name,
                    "type": custom_labels[0],
                    "summary": node.summary
                })
        
        return {
            "simulation_requirement": simulation_requirement,
            "related_facts": search_result.facts,
            "graph_statistics": stats,
            "entities": entities[:limit],
            "total_entities": len(entities)
        }
    
    # ========== Core retrieval tools ==========

    def insight_forge(
        self,
        graph_id: str,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_sub_queries: int = 5
    ) -> InsightForgeResult:
        """
        InsightForge — deep-insight retrieval.

        The most powerful hybrid retrieval function; automatically decomposes
        a question and retrieves across multiple dimensions:
        1. Use LLM to break the question into sub-questions.
        2. Perform semantic search for each sub-question.
        3. Extract relevant entities and fetch their details.
        4. Trace relationship chains.
        5. Aggregate all results into a deep-insight report.

        Args:
            graph_id: Graph ID
            query: User question
            simulation_requirement: Simulation requirement description
            report_context: Report context (optional, improves sub-question generation)
            max_sub_queries: Maximum number of sub-questions

        Returns:
            InsightForgeResult
        """
        logger.info(t("console.insightForgeStart", query=query[:50]))
        
        result = InsightForgeResult(
            query=query,
            simulation_requirement=simulation_requirement,
            sub_queries=[]
        )
        
        # Step 1: Use LLM to generate sub-questions
        sub_queries = self._generate_sub_queries(
            query=query,
            simulation_requirement=simulation_requirement,
            report_context=report_context,
            max_queries=max_sub_queries
        )
        result.sub_queries = sub_queries
        logger.info(t("console.generatedSubQueries", count=len(sub_queries)))
        
        # Step 2: Semantic search for each sub-question
        all_facts = []
        all_edges = []
        seen_facts = set()
        
        for sub_query in sub_queries:
            search_result = self.search_graph(
                graph_id=graph_id,
                query=sub_query,
                limit=15,
                scope="edges"
            )
            
            for fact in search_result.facts:
                if fact not in seen_facts:
                    all_facts.append(fact)
                    seen_facts.add(fact)
            
            all_edges.extend(search_result.edges)
        
        # Also search the original question directly
        main_search = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=20,
            scope="edges"
        )
        for fact in main_search.facts:
            if fact not in seen_facts:
                all_facts.append(fact)
                seen_facts.add(fact)
        
        result.semantic_facts = all_facts
        result.total_facts = len(all_facts)
        
        # Step 3: Extract entity UUIDs from edges — fetch only those entities, not all nodes
        entity_uuids = set()
        for edge_data in all_edges:
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                if source_uuid:
                    entity_uuids.add(source_uuid)
                if target_uuid:
                    entity_uuids.add(target_uuid)
        
        # Fetch details for all relevant entities (complete, untruncated)
        entity_insights = []
        node_map = {}  # Used later for building relationship chains

        for uuid in list(entity_uuids):  # Process all entities, no truncation
            if not uuid:
                continue
            try:
                # Fetch each related node individually
                node = self.get_node_detail(uuid)
                if node:
                    node_map[uuid] = node
                    entity_type = next((l for l in node.labels if l not in ["Entity", "Node"]), "Entity")

                    # All facts that mention this entity (complete, untruncated)
                    related_facts = [
                        f for f in all_facts 
                        if node.name.lower() in f.lower()
                    ]
                    
                    entity_insights.append({
                        "uuid": node.uuid,
                        "name": node.name,
                        "type": entity_type,
                        "summary": node.summary,
                        "related_facts": related_facts  # complete, untruncated
                    })
            except Exception as e:
                logger.debug(f"Failed to fetch node {uuid}: {e}")
                continue

        result.entity_insights = entity_insights
        result.total_entities = len(entity_insights)

        # Step 4: Build all relationship chains (no truncation)
        relationship_chains = []
        for edge_data in all_edges:  # Process all edges, no truncation
            if isinstance(edge_data, dict):
                source_uuid = edge_data.get('source_node_uuid', '')
                target_uuid = edge_data.get('target_node_uuid', '')
                relation_name = edge_data.get('name', '')
                
                source_name = node_map.get(source_uuid, NodeInfo('', '', [], '', {})).name or source_uuid[:8]
                target_name = node_map.get(target_uuid, NodeInfo('', '', [], '', {})).name or target_uuid[:8]
                
                chain = f"{source_name} --[{relation_name}]--> {target_name}"
                if chain not in relationship_chains:
                    relationship_chains.append(chain)
        
        result.relationship_chains = relationship_chains
        result.total_relationships = len(relationship_chains)
        
        logger.info(t("console.insightForgeComplete", facts=result.total_facts, entities=result.total_entities, relationships=result.total_relationships))
        return result
    
    def _generate_sub_queries(
        self,
        query: str,
        simulation_requirement: str,
        report_context: str = "",
        max_queries: int = 5
    ) -> List[str]:
        """
        Use the LLM to generate sub-questions.

        Breaks a complex question into multiple independently searchable
        sub-questions.
        """
        system_prompt = (
            "You are an expert problem analyst. Your task is to break a complex question "
            "down into multiple sub-questions that can each be observed independently "
            "within the simulation world.\n\n"
            "Requirements:\n"
            "1. Each sub-question should be specific enough to find relevant Agent "
            "behaviour or events within the simulation world.\n"
            "2. Sub-questions should cover different dimensions of the original question "
            "(e.g. who, what, why, how, when, where).\n"
            "3. Sub-questions should be relevant to the simulation context.\n"
            '4. Return JSON format: {"sub_queries": ["sub-question 1", "sub-question 2", ...]}'
        )

        user_prompt = (
            f"Simulation context:\n{simulation_requirement}\n\n"
            + (f"Report context: {report_context[:500]}\n\n" if report_context else "")
            + f"Please break the following question into {max_queries} sub-questions:\n{query}\n\n"
            "Return the sub-questions as a JSON list."
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )

            sub_queries = response.get("sub_queries", [])
            # Ensure all entries are strings
            return [str(sq) for sq in sub_queries[:max_queries]]

        except Exception as e:
            logger.warning(t("console.generateSubQueriesFailed", error=str(e)))
            # Fallback: return variants of the original question
            return [
                query,
                f"Key participants in: {query}",
                f"Causes and effects of: {query}",
                f"How did this develop: {query}",
            ][:max_queries]
    
    def panorama_search(
        self,
        graph_id: str,
        query: str,
        include_expired: bool = True,
        limit: int = 50
    ) -> PanoramaResult:
        """
        PanoramaSearch — broad search.

        Retrieves the full picture, including all related content and
        historical / expired information:
        1. Fetch all relevant nodes.
        2. Fetch all edges (including expired / invalidated ones).
        3. Classify facts into active and historical buckets.

        Best suited for understanding the complete picture of an event or
        tracing how something evolved over time.

        Args:
            graph_id: Graph ID
            query: Search query (used for relevance sorting)
            include_expired: Whether to include expired content (default True)
            limit: Maximum number of results per bucket

        Returns:
            PanoramaResult
        """
        logger.info(t("console.panoramaSearchStart", query=query[:50]))
        
        result = PanoramaResult(query=query)
        
        # Fetch all nodes
        all_nodes = self.get_all_nodes(graph_id)
        node_map = {n.uuid: n for n in all_nodes}
        result.all_nodes = all_nodes
        result.total_nodes = len(all_nodes)

        # Fetch all edges with temporal metadata
        all_edges = self.get_all_edges(graph_id, include_temporal=True)
        result.all_edges = all_edges
        result.total_edges = len(all_edges)

        # Classify facts into active vs historical
        active_facts = []
        historical_facts = []

        for edge in all_edges:
            if not edge.fact:
                continue

            # Resolve entity names for the fact
            source_name = node_map.get(edge.source_node_uuid, NodeInfo('', '', [], '', {})).name or edge.source_node_uuid[:8]
            target_name = node_map.get(edge.target_node_uuid, NodeInfo('', '', [], '', {})).name or edge.target_node_uuid[:8]

            # Determine whether the edge is expired / invalidated
            is_historical = edge.is_expired or edge.is_invalid
            
            if is_historical:
                # Historical / expired fact — annotate with time range
                valid_at = edge.valid_at or "unknown"
                invalid_at = edge.invalid_at or edge.expired_at or "unknown"
                fact_with_time = f"[{valid_at} - {invalid_at}] {edge.fact}"
                historical_facts.append(fact_with_time)
            else:
                # Currently active fact
                active_facts.append(edge.fact)
        
        # Sort by query relevance
        query_lower = query.lower()
        keywords = [w.strip() for w in query_lower.replace(',', ' ').replace('，', ' ').split() if len(w.strip()) > 1]
        
        def relevance_score(fact: str) -> int:
            fact_lower = fact.lower()
            score = 0
            if query_lower in fact_lower:
                score += 100
            for kw in keywords:
                if kw in fact_lower:
                    score += 10
            return score
        
        # Sort and cap by limit
        active_facts.sort(key=relevance_score, reverse=True)
        historical_facts.sort(key=relevance_score, reverse=True)
        
        result.active_facts = active_facts[:limit]
        result.historical_facts = historical_facts[:limit] if include_expired else []
        result.active_count = len(active_facts)
        result.historical_count = len(historical_facts)
        
        logger.info(t("console.panoramaSearchComplete", active=result.active_count, historical=result.historical_count))
        return result
    
    def quick_search(
        self,
        graph_id: str,
        query: str,
        limit: int = 10
    ) -> SearchResult:
        """
        QuickSearch — simple, fast retrieval.

        Lightweight retrieval tool:
        1. Calls Zep semantic search directly.
        2. Returns the most relevant results.
        3. Best for simple, direct retrieval needs.

        Args:
            graph_id: Graph ID
            query: Search query
            limit: Maximum number of results

        Returns:
            SearchResult
        """
        logger.info(t("console.quickSearchStart", query=query[:50]))
        
        # Delegate directly to search_graph
        result = self.search_graph(
            graph_id=graph_id,
            query=query,
            limit=limit,
            scope="edges"
        )
        
        logger.info(t("console.quickSearchComplete", count=result.total_count))
        return result
    
    def interview_agents(
        self,
        simulation_id: str,
        interview_requirement: str,
        simulation_requirement: str = "",
        max_agents: int = 5,
        custom_questions: List[str] = None
    ) -> InterviewResult:
        """
        InterviewAgents — in-depth agent interviews.

        Calls the real OASIS interview API to interview agents that are
        currently running in the simulation:
        1. Auto-load persona files to learn about all simulated agents.
        2. Use LLM to analyse interview requirements and select the most
           relevant agents.
        3. Use LLM to generate interview questions.
        4. Call /api/simulation/interview/batch for real interviews
           (both platforms simultaneously).
        5. Aggregate all interview results into an interview report.

        IMPORTANT: Requires the simulation environment to be running
        (OASIS environment must not have been closed).

        Use cases:
        - Understanding an event from different role perspectives.
        - Collecting diverse opinions and viewpoints.
        - Obtaining real agent responses (not LLM-simulated).

        Args:
            simulation_id: Simulation ID (used to locate persona files and
                call the interview API)
            interview_requirement: Interview requirement description
                (free-form, e.g. "understand students' views on the event")
            simulation_requirement: Simulation background context (optional)
            max_agents: Maximum number of agents to interview
            custom_questions: Custom interview questions (optional; auto-generated
                if not provided)

        Returns:
            InterviewResult
        """
        from .simulation_runner import SimulationRunner
        
        logger.info(t("console.interviewAgentsStart", requirement=interview_requirement[:50]))
        
        result = InterviewResult(
            interview_topic=interview_requirement,
            interview_questions=custom_questions or []
        )
        
        # Step 1: Load persona files
        profiles = self._load_agent_profiles(simulation_id)
        
        if not profiles:
            logger.warning(t("console.profilesNotFound", simId=simulation_id))
            result.summary = "No agent persona files found."
            return result
        
        result.total_agents = len(profiles)
        logger.info(t("console.loadedProfiles", count=len(profiles)))
        
        # Step 2: Use LLM to select agents to interview (returns agent_id list)
        selected_agents, selected_indices, selection_reasoning = self._select_agents_for_interview(
            profiles=profiles,
            interview_requirement=interview_requirement,
            simulation_requirement=simulation_requirement,
            max_agents=max_agents
        )
        
        result.selected_agents = selected_agents
        result.selection_reasoning = selection_reasoning
        logger.info(t("console.selectedAgentsForInterview", count=len(selected_agents), indices=selected_indices))
        
        # Step 3: Generate interview questions if none were provided
        if not result.interview_questions:
            result.interview_questions = self._generate_interview_questions(
                interview_requirement=interview_requirement,
                simulation_requirement=simulation_requirement,
                selected_agents=selected_agents
            )
            logger.info(t("console.generatedInterviewQuestions", count=len(result.interview_questions)))
        
        # Combine questions into a single interview prompt
        combined_prompt = "\n".join([f"{i+1}. {q}" for i, q in enumerate(result.interview_questions)])

        # Add a prefix that constrains the agent's response format
        INTERVIEW_PROMPT_PREFIX = (
            "You are being interviewed. Drawing on your persona and all your past memories "
            "and actions, answer the following questions directly in plain text.\n"
            "Response requirements:\n"
            "1. Answer in natural language — do not call any tools.\n"
            "2. Do not return JSON format or tool-call format.\n"
            "3. Do not use Markdown headings (e.g. #, ##, ###).\n"
            "4. Answer each question in order by its number, starting each answer with "
            "\"Question X:\" (where X is the question number).\n"
            "5. Separate answers with a blank line.\n"
            "6. Give substantive answers — at least 2–3 sentences per question.\n\n"
        )
        optimized_prompt = f"{INTERVIEW_PROMPT_PREFIX}{combined_prompt}"
        
        # Step 4: Call the real interview API (no platform specified → dual-platform)
        try:
            # Build the batch interview list (no platform → both platforms)
            interviews_request = []
            for agent_idx in selected_indices:
                interviews_request.append({
                    "agent_id": agent_idx,
                    "prompt": optimized_prompt
                    # No platform specified — API interviews on both Twitter and Reddit
                })
            
            logger.info(t("console.callingBatchInterviewApi", count=len(interviews_request)))
            
            # Call SimulationRunner's batch interview method (no platform → dual-platform)
            api_result = SimulationRunner.interview_agents_batch(
                simulation_id=simulation_id,
                interviews=interviews_request,
                platform=None,  # No platform specified → interview on both platforms
                timeout=180.0   # Dual-platform requires a longer timeout
            )
            
            logger.info(t("console.interviewApiReturned", count=api_result.get('interviews_count', 0), success=api_result.get('success')))
            
            # Check whether the API call succeeded
            if not api_result.get("success", False):
                error_msg = api_result.get("error", "Unknown error")
                logger.warning(t("console.interviewApiReturnedFailure", error=error_msg))
                result.summary = f"Interview API call failed: {error_msg}. Please check the OASIS simulation environment status."
                return result

            # Step 5: Parse API results and build AgentInterview objects
            # Dual-platform format: {"twitter_0": {...}, "reddit_0": {...}, "twitter_1": {...}, ...}
            api_data = api_result.get("result", {})
            results_dict = api_data.get("results", {}) if isinstance(api_data, dict) else {}
            
            for i, agent_idx in enumerate(selected_indices):
                agent = selected_agents[i]
                agent_name = agent.get("realname", agent.get("username", f"Agent_{agent_idx}"))
                agent_role = agent.get("profession", "Unknown")
                agent_bio = agent.get("bio", "")
                
                # Fetch this agent's interview results from both platforms
                twitter_result = results_dict.get(f"twitter_{agent_idx}", {})
                reddit_result = results_dict.get(f"reddit_{agent_idx}", {})
                
                twitter_response = twitter_result.get("response", "")
                reddit_response = reddit_result.get("response", "")

                # Strip any tool-call JSON wrappers from responses
                twitter_response = self._clean_tool_call_response(twitter_response)
                reddit_response = self._clean_tool_call_response(reddit_response)

                # Always show dual-platform labels
                twitter_text = twitter_response if twitter_response else "(no response from this platform)"
                reddit_text = reddit_response if reddit_response else "(no response from this platform)"
                response_text = f"[Twitter]\n{twitter_text}\n\n[Reddit]\n{reddit_text}"

                # Extract key quotes from both platform responses
                import re
                combined_responses = f"{twitter_response} {reddit_response}"

                # Clean response text: strip markers, numbering, Markdown noise
                clean_text = re.sub(r'#{1,6}\s+', '', combined_responses)
                clean_text = re.sub(r'\{[^}]*tool_name[^}]*\}', '', clean_text)
                clean_text = re.sub(r'[*_`|>~\-]{2,}', '', clean_text)
                clean_text = re.sub(r'[Qq]uestion\s*\d+[：:]\s*|问题\d+[：:]\s*', '', clean_text)
                clean_text = re.sub(r'【[^】]+】', '', clean_text)

                # Strategy 1 (primary): Extract complete substantive sentences
                sentences = re.split(r'[。！？]', clean_text)
                meaningful = [
                    s.strip() for s in sentences
                    if 20 <= len(s.strip()) <= 150
                    and not re.match(r'^[\s\W，,；;：:、]+', s.strip())
                    and not s.strip().startswith(('{', 'Question', '问题'))
                ]
                meaningful.sort(key=len, reverse=True)
                key_quotes = [s + "。" for s in meaningful[:3]]

                # Strategy 2 (fallback): well-paired Chinese 「」 quotation marks
                if not key_quotes:
                    paired = re.findall(r'\u201c([^\u201c\u201d]{15,100})\u201d', clean_text)
                    paired += re.findall(r'\u300c([^\u300c\u300d]{15,100})\u300d', clean_text)
                    key_quotes = [q for q in paired if not re.match(r'^[，,；;：:、]', q)][:3]
                
                interview = AgentInterview(
                    agent_name=agent_name,
                    agent_role=agent_role,
                    agent_bio=agent_bio[:1000],  # Expanded bio length limit
                    question=combined_prompt,
                    response=response_text,
                    key_quotes=key_quotes[:5]
                )
                result.interviews.append(interview)
            
            result.interviewed_count = len(result.interviews)
            
        except ValueError as e:
            # Simulation environment is not running
            logger.warning(t("console.interviewApiCallFailed", error=e))
            result.summary = f"Interview failed: {str(e)}. The simulation environment may have been closed — ensure the OASIS environment is running."
            return result
        except Exception as e:
            logger.error(t("console.interviewApiCallException", error=e))
            import traceback
            logger.error(traceback.format_exc())
            result.summary = f"An error occurred during the interview: {str(e)}"
            return result

        # Step 6: Generate interview summary
        if result.interviews:
            result.summary = self._generate_interview_summary(
                interviews=result.interviews,
                interview_requirement=interview_requirement
            )
        
        logger.info(t("console.interviewAgentsComplete", count=result.interviewed_count))
        return result
    
    @staticmethod
    def _clean_tool_call_response(response: str) -> str:
        """Strip JSON tool-call wrappers from an agent response and extract the actual content."""
        if not response or not response.strip().startswith('{'):
            return response
        text = response.strip()
        if 'tool_name' not in text[:80]:
            return response
        import re as _re
        try:
            data = json.loads(text)
            if isinstance(data, dict) and 'arguments' in data:
                for key in ('content', 'text', 'body', 'message', 'reply'):
                    if key in data['arguments']:
                        return str(data['arguments'][key])
        except (json.JSONDecodeError, KeyError, TypeError):
            match = _re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            if match:
                return match.group(1).replace('\\n', '\n').replace('\\"', '"')
        return response

    def _load_agent_profiles(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Load agent persona files for the given simulation."""
        import os
        import csv

        # Build the path to the persona files
        sim_dir = os.path.join(
            os.path.dirname(__file__), 
            f'../../uploads/simulations/{simulation_id}'
        )
        
        profiles = []
        
        # Prefer the Reddit JSON format
        reddit_profile_path = os.path.join(sim_dir, "reddit_profiles.json")
        if os.path.exists(reddit_profile_path):
            try:
                with open(reddit_profile_path, 'r', encoding='utf-8') as f:
                    profiles = json.load(f)
                logger.info(t("console.loadedRedditProfiles", count=len(profiles)))
                return profiles
            except Exception as e:
                logger.warning(t("console.readRedditProfilesFailed", error=e))
        
        # Fall back to the Twitter CSV format
        twitter_profile_path = os.path.join(sim_dir, "twitter_profiles.csv")
        if os.path.exists(twitter_profile_path):
            try:
                with open(twitter_profile_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Normalise CSV row to unified profile format
                        profiles.append({
                            "realname": row.get("name", ""),
                            "username": row.get("username", ""),
                            "bio": row.get("description", ""),
                            "persona": row.get("user_char", ""),
                            "profession": "Unknown"
                        })
                logger.info(t("console.loadedTwitterProfiles", count=len(profiles)))
                return profiles
            except Exception as e:
                logger.warning(t("console.readTwitterProfilesFailed", error=e))
        
        return profiles
    
    def _select_agents_for_interview(
        self,
        profiles: List[Dict[str, Any]],
        interview_requirement: str,
        simulation_requirement: str,
        max_agents: int
    ) -> tuple:
        """
        Use the LLM to select agents for an interview.

        Returns:
            tuple: (selected_agents, selected_indices, reasoning)
                - selected_agents: Full profile info for selected agents
                - selected_indices: Index list of selected agents (used for API call)
                - reasoning: Explanation of the selection
        """

        # Build agent summary list
        agent_summaries = []
        for i, profile in enumerate(profiles):
            summary = {
                "index": i,
                "name": profile.get("realname", profile.get("username", f"Agent_{i}")),
                "profession": profile.get("profession", "Unknown"),
                "bio": profile.get("bio", "")[:200],
                "interested_topics": profile.get("interested_topics", [])
            }
            agent_summaries.append(summary)

        system_prompt = (
            "You are an expert interview planner. Your task is to select the most suitable "
            "interview subjects from the list of simulated Agents based on the interview "
            "requirements.\n\n"
            "Selection criteria:\n"
            "1. The agent's identity / profession is relevant to the interview topic.\n"
            "2. The agent is likely to hold a unique or valuable perspective.\n"
            "3. Aim for diverse viewpoints (e.g. proponents, opponents, neutral parties, "
            "experts, etc.).\n"
            "4. Prioritise roles directly related to the event.\n\n"
            "Return JSON format:\n"
            "{\n"
            '    "selected_indices": [list of selected agent indices],\n'
            '    "reasoning": "explanation of the selection"\n'
            "}"
        )

        user_prompt = (
            f"Interview requirement:\n{interview_requirement}\n\n"
            f"Simulation background:\n{simulation_requirement if simulation_requirement else 'Not provided'}\n\n"
            f"Available agents ({len(agent_summaries)} total):\n"
            f"{json.dumps(agent_summaries, ensure_ascii=False, indent=2)}\n\n"
            f"Please select up to {max_agents} agents best suited for this interview and explain your reasoning."
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )

            selected_indices = response.get("selected_indices", [])[:max_agents]
            reasoning = response.get("reasoning", "Selected automatically based on relevance")

            # Collect full profile info for the selected agents
            selected_agents = []
            valid_indices = []
            for idx in selected_indices:
                if 0 <= idx < len(profiles):
                    selected_agents.append(profiles[idx])
                    valid_indices.append(idx)
            
            return selected_agents, valid_indices, reasoning
            
        except Exception as e:
            logger.warning(t("console.llmSelectAgentFailed", error=e))
            # Fallback: select first N agents
            selected = profiles[:max_agents]
            indices = list(range(min(max_agents, len(profiles))))
            return selected, indices, "Using default selection strategy"

    def _generate_interview_questions(
        self,
        interview_requirement: str,
        simulation_requirement: str,
        selected_agents: List[Dict[str, Any]]
    ) -> List[str]:
        """Use the LLM to generate interview questions."""

        agent_roles = [a.get("profession", "Unknown") for a in selected_agents]

        system_prompt = (
            "You are a professional journalist / interviewer. Based on the interview "
            "requirements, generate 3–5 in-depth interview questions.\n\n"
            "Question requirements:\n"
            "1. Open-ended questions that encourage detailed answers.\n"
            "2. Questions that may elicit different answers from different roles.\n"
            "3. Cover multiple dimensions: facts, opinions, feelings.\n"
            "4. Natural language, like a real interview.\n"
            "5. Each question should be concise — under 50 words.\n"
            "6. Ask directly without background preamble or prefixes.\n\n"
            'Return JSON format: {"questions": ["Question 1", "Question 2", ...]}'
        )

        user_prompt = (
            f"Interview requirement: {interview_requirement}\n\n"
            f"Simulation background: {simulation_requirement if simulation_requirement else 'Not provided'}\n\n"
            f"Interviewee roles: {', '.join(agent_roles)}\n\n"
            "Please generate 3–5 interview questions."
        )

        try:
            response = self.llm.chat_json(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5
            )

            return response.get("questions", [f"What are your thoughts on {interview_requirement}?"])

        except Exception as e:
            logger.warning(t("console.generateInterviewQuestionsFailed", error=e))
            return [
                f"What is your view on {interview_requirement}?",
                "How has this affected you or the group you represent?",
                "What do you think should be done to address or improve this situation?",
            ]
    
    def _generate_interview_summary(
        self,
        interviews: List[AgentInterview],
        interview_requirement: str
    ) -> str:
        """Use the LLM to generate an interview summary."""

        if not interviews:
            return "No interviews completed."

        # Collect all interview content
        interview_texts = []
        for interview in interviews:
            interview_texts.append(f"[{interview.agent_name} ({interview.agent_role})]\n{interview.response[:500]}")

        system_prompt = (
            "You are a professional news editor. Please generate an interview summary "
            "based on the responses from multiple interviewees.\n\n"
            "Summary requirements:\n"
            "1. Summarise the main viewpoints of each party.\n"
            "2. Highlight areas of consensus and disagreement.\n"
            "3. Include valuable quotes.\n"
            "4. Objective and neutral — do not favour any side.\n"
            "5. Keep it under 1000 words.\n\n"
            "Formatting constraints (must follow):\n"
            "- Use plain text paragraphs, separated by blank lines.\n"
            "- Do not use Markdown headings (e.g. #, ##, ###).\n"
            "- Do not use dividers (e.g. ---, ***).\n"
            '- Use quotation marks "" when quoting interviewees.\n'
            "- You may use **bold** to highlight key terms, but no other Markdown syntax."
        )

        user_prompt = (
            f"Interview topic: {interview_requirement}\n\n"
            f"Interview content:\n{''.join(interview_texts)}\n\n"
            "Please generate the interview summary."
        )

        try:
            summary = self.llm.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            return summary

        except Exception as e:
            logger.warning(t("console.generateInterviewSummaryFailed", error=e))
            # Fallback: simple concatenation
            names = ", ".join([i.agent_name for i in interviews])
            return f"Interviewed {len(interviews)} respondents: {names}"
