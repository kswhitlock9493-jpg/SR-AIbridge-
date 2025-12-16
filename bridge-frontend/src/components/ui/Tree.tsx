/**
 * Tree Component - Hierarchical task visualization
 * Displays task dependencies and status in a tree structure
 */
import React, { useState } from 'react';

interface TreeNode {
  id: string;
  label: string;
  children?: TreeNode[];
  status?: string;
  expanded?: boolean;
}

interface TreeProps {
  nodes: TreeNode[];
  onNodeClick?: (node: TreeNode) => void;
}

const TreeNodeComponent: React.FC<{
  node: TreeNode;
  level: number;
  onNodeClick?: (node: TreeNode) => void;
}> = ({ node, level, onNodeClick }) => {
  const [expanded, setExpanded] = useState(node.expanded ?? true);
  const hasChildren = node.children && node.children.length > 0;

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'done':
        return 'text-green-600';
      case 'running':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      case 'queued':
        return 'text-yellow-600';
      case 'skipped':
        return 'text-gray-500';
      default:
        return 'text-gray-700';
    }
  };

  return (
    <div className="tree-node">
      <div
        className={`flex items-center gap-2 py-1 px-2 hover:bg-gray-100 rounded cursor-pointer ${getStatusColor(node.status)}`}
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={() => {
          if (hasChildren) setExpanded(!expanded);
          if (onNodeClick) onNodeClick(node);
        }}
      >
        {hasChildren && (
          <span className="text-xs">
            {expanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && <span className="text-xs opacity-0">▶</span>}
        <span className="font-mono text-sm">{node.label}</span>
      </div>
      {hasChildren && expanded && (
        <div className="tree-children">
          {node.children!.map((child) => (
            <TreeNodeComponent
              key={child.id}
              node={child}
              level={level + 1}
              onNodeClick={onNodeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default function Tree({ nodes, onNodeClick }: TreeProps) {
  return (
    <div className="tree-container border border-gray-300 rounded p-2 bg-white">
      {nodes.map((node) => (
        <TreeNodeComponent
          key={node.id}
          node={node}
          level={0}
          onNodeClick={onNodeClick}
        />
      ))}
    </div>
  );
}
