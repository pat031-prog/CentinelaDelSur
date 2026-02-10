from typing import Any, Dict, List, Optional, Set, Tuple
from backend.utils.logger import logger


class NetworkAnalyzer:
    """Network analysis for actor relationships and dependency mapping.

    Implements graph algorithms for analyzing crisis actor networks
    and supply chain dependencies without NetworkX dependency.
    """

    def __init__(self):
        self.logger = logger.getChild("network_analysis")
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, attributes: Optional[Dict] = None):
        """Add a node to the network."""
        self.nodes[node_id] = attributes or {}

    def add_edge(self, source: str, target: str, weight: float = 1.0, edge_type: str = "default"):
        """Add a directed edge to the network."""
        self.edges.append({
            "source": source,
            "target": target,
            "weight": weight,
            "type": edge_type,
        })

    def get_adjacency(self) -> Dict[str, List[Tuple[str, float]]]:
        """Get adjacency list representation."""
        adj: Dict[str, List[Tuple[str, float]]] = {node: [] for node in self.nodes}
        for edge in self.edges:
            if edge["source"] in adj:
                adj[edge["source"]].append((edge["target"], edge["weight"]))
        return adj

    def calculate_degree_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for each node."""
        if not self.nodes:
            return {}

        in_degree: Dict[str, int] = {n: 0 for n in self.nodes}
        out_degree: Dict[str, int] = {n: 0 for n in self.nodes}

        for edge in self.edges:
            if edge["target"] in in_degree:
                in_degree[edge["target"]] += 1
            if edge["source"] in out_degree:
                out_degree[edge["source"]] += 1

        n = len(self.nodes)
        if n <= 1:
            return {node: 0.0 for node in self.nodes}

        return {
            node: round((in_degree[node] + out_degree[node]) / (2 * (n - 1)), 4)
            for node in self.nodes
        }

    def find_critical_nodes(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Find the most critical nodes in the network."""
        centrality = self.calculate_degree_centrality()
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        return [
            {"node": node, "centrality": score, **self.nodes.get(node, {})}
            for node, score in sorted_nodes[:top_n]
        ]

    def find_dependencies(self, node_id: str) -> Dict[str, List[str]]:
        """Find all dependencies (incoming) and dependents (outgoing) of a node."""
        dependencies = []
        dependents = []

        for edge in self.edges:
            if edge["target"] == node_id:
                dependencies.append(edge["source"])
            if edge["source"] == node_id:
                dependents.append(edge["target"])

        return {"dependencies": dependencies, "dependents": dependents}

    def simulate_cascade(self, failed_node: str, failure_threshold: float = 0.5) -> Dict[str, Any]:
        """Simulate cascade failure from a single node failure.

        Args:
            failed_node: The initially failing node
            failure_threshold: Fraction of dependencies that must fail to cause cascade

        Returns:
            Cascade analysis with affected nodes and propagation path
        """
        if failed_node not in self.nodes:
            return {"error": f"Node {failed_node} not found"}

        failed: Set[str] = {failed_node}
        cascade_path = [{"step": 0, "failed": [failed_node], "reason": "initial_failure"}]

        changed = True
        step = 0
        while changed:
            changed = False
            step += 1
            new_failures = []

            for node in self.nodes:
                if node in failed:
                    continue

                deps = self.find_dependencies(node)["dependencies"]
                if not deps:
                    continue

                failed_deps = sum(1 for d in deps if d in failed)
                if failed_deps / len(deps) >= failure_threshold:
                    new_failures.append(node)
                    changed = True

            if new_failures:
                failed.update(new_failures)
                cascade_path.append({
                    "step": step,
                    "failed": new_failures,
                    "reason": "dependency_cascade",
                })

        return {
            "initial_failure": failed_node,
            "total_affected": len(failed),
            "total_nodes": len(self.nodes),
            "impact_ratio": round(len(failed) / len(self.nodes), 4) if self.nodes else 0,
            "cascade_path": cascade_path,
            "surviving_nodes": [n for n in self.nodes if n not in failed],
        }

    def get_network_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the network."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "density": round(
                len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1))
                if len(self.nodes) > 1 else 0, 4
            ),
            "critical_nodes": self.find_critical_nodes(),
        }

    def clear(self):
        """Clear all nodes and edges."""
        self.nodes.clear()
        self.edges.clear()
