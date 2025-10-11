"""
Provider adapters for Env Steward
"""

from .render_adapter import RenderAdapter
from .netlify_adapter import NetlifyAdapter
from .github_adapter import GithubAdapter


def get_adapters(providers):
    """Get enabled adapters for the given providers"""
    adapters = []
    adapter_map = {
        "render": RenderAdapter,
        "netlify": NetlifyAdapter,
        "github": GithubAdapter
    }
    
    for provider in providers:
        if provider in adapter_map:
            adapter = adapter_map[provider]()
            if adapter.enabled():
                adapters.append(adapter)
    
    return adapters


__all__ = ["get_adapters", "RenderAdapter", "NetlifyAdapter", "GithubAdapter"]
