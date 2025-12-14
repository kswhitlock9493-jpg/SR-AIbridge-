"""
HXO Merkle Tree Implementation
Content-addressed aggregation and proof generation
"""

import logging
from typing import Dict, List, Optional
import hashlib

from .models import ShardResult, MerkleNode, MerkleProof

logger = logging.getLogger(__name__)


class MerkleTree:
    """
    Merkle tree for shard result aggregation.
    Provides integrity proofs and verification.
    """
    
    def __init__(self, plan_id: str):
        self.plan_id = plan_id
        self.leaves: List[MerkleNode] = []
        self.nodes: Dict[str, MerkleNode] = {}
        self.root_hash: Optional[str] = None
    
    def add_leaf(self, shard_result: ShardResult):
        """Add a shard result as a leaf node"""
        leaf_hash = MerkleNode.leaf_hash(shard_result)
        node_id = f"leaf_{shard_result.cas_id}"
        
        node = MerkleNode(
            node_id=node_id,
            hash_value=leaf_hash,
            is_leaf=True
        )
        
        self.leaves.append(node)
        self.nodes[node_id] = node
        
        # Invalidate root (needs recomputation)
        self.root_hash = None
    
    def compute_root(self) -> str:
        """
        Compute Merkle root hash.
        Builds the tree bottom-up from leaves.
        """
        if self.root_hash:
            return self.root_hash
        
        if not self.leaves:
            # Empty tree
            self.root_hash = hashlib.sha256(b"empty").hexdigest()
            return self.root_hash
        
        if len(self.leaves) == 1:
            # Single leaf
            self.root_hash = self.leaves[0].hash_value
            return self.root_hash
        
        # Build tree level by level
        current_level = self.leaves[:]
        level_num = 0
        
        while len(current_level) > 1:
            next_level = []
            
            # Pair up nodes
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    # Odd number of nodes - duplicate last one
                    right = left
                
                # Create parent node
                parent_hash = MerkleNode.branch_hash(left.hash_value, right.hash_value)
                parent_id = f"branch_{level_num}_{i // 2}"
                
                parent = MerkleNode(
                    node_id=parent_id,
                    left=left.node_id,
                    right=right.node_id,
                    hash_value=parent_hash,
                    is_leaf=False
                )
                
                self.nodes[parent_id] = parent
                next_level.append(parent)
            
            current_level = next_level
            level_num += 1
        
        # Root is the last remaining node
        self.root_hash = current_level[0].hash_value
        logger.debug(f"[Merkle] Computed root for {self.plan_id}: {self.root_hash[:16]}...")
        return self.root_hash
    
    def generate_proof(self, cas_id: str) -> Optional[MerkleProof]:
        """
        Generate Merkle proof for a specific shard.
        
        Args:
            cas_id: Content-addressed shard ID
            
        Returns:
            Merkle proof or None if shard not found
        """
        # Find leaf node
        leaf_node_id = f"leaf_{cas_id}"
        if leaf_node_id not in self.nodes:
            return None
        
        leaf = self.nodes[leaf_node_id]
        
        # Build path to root
        path = []
        current_id = leaf_node_id
        
        # Traverse up the tree
        for node in self.nodes.values():
            if not node.is_leaf:
                if node.left == current_id:
                    # Current node is left child
                    if node.right and node.right in self.nodes:
                        sibling = self.nodes[node.right]
                        path.append({"side": "right", "hash": sibling.hash_value})
                    current_id = node.node_id
                elif node.right == current_id:
                    # Current node is right child
                    if node.left and node.left in self.nodes:
                        sibling = self.nodes[node.left]
                        path.append({"side": "left", "hash": sibling.hash_value})
                    current_id = node.node_id
        
        root = self.compute_root()
        
        return MerkleProof(
            leaf_cas_id=cas_id,
            leaf_hash=leaf.hash_value,
            path=path,
            root_hash=root
        )
    
    def verify_proof(self, proof: MerkleProof) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            proof: Merkle proof to verify
            
        Returns:
            True if proof is valid
        """
        current_hash = proof.leaf_hash
        
        # Traverse path and recompute hashes
        for step in proof.path:
            if step["side"] == "left":
                current_hash = MerkleNode.branch_hash(step["hash"], current_hash)
            else:
                current_hash = MerkleNode.branch_hash(current_hash, step["hash"])
        
        # Check if computed hash matches root
        return current_hash == proof.root_hash
    
    def sample_proofs(self, sample_size: int = 10) -> List[MerkleProof]:
        """
        Generate sample proofs for verification.
        Uses reservoir sampling for uniform distribution.
        
        Args:
            sample_size: Number of proofs to sample
            
        Returns:
            List of Merkle proofs
        """
        import random
        
        if not self.leaves:
            return []
        
        # Sample leaves
        sample = random.sample(self.leaves, min(sample_size, len(self.leaves)))
        
        # Generate proofs
        proofs = []
        for leaf in sample:
            # Extract CAS ID from node_id (format: "leaf_{cas_id}")
            cas_id = leaf.node_id.replace("leaf_", "")
            proof = self.generate_proof(cas_id)
            if proof:
                proofs.append(proof)
        
        return proofs
