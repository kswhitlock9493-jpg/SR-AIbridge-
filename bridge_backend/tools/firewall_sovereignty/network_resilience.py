#!/usr/bin/env python3
"""
Network Resilience Layer
Sovereign control over network connections with retry, fallback, and healing mechanisms
"""

import socket
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json


class NetworkResilienceLayer:
    """
    Network Resilience and Connection Management
    
    Provides sovereign control over:
    - Connection retry mechanisms
    - DNS resolution with fallback
    - Network health monitoring
    - Automatic healing for network failures
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.connection_stats = {
            "successful_connections": 0,
            "failed_connections": 0,
            "retries_performed": 0,
            "dns_resolutions": 0,
            "dns_fallbacks": 0
        }
        
        # DNS servers
        self.primary_dns = self.config.get("dns_resolution", {}).get("primary", ["8.8.8.8", "8.8.4.4"])
        self.fallback_dns = self.config.get("dns_resolution", {}).get("fallback", ["1.1.1.1", "1.0.0.1"])
        
        # Retry configuration
        self.max_retries = self.config.get("retry_policy", {}).get("max_retries", 3)
        self.backoff_multiplier = self.config.get("retry_policy", {}).get("backoff_multiplier", 2)
        self.initial_delay = self.config.get("retry_policy", {}).get("initial_delay_ms", 1000) / 1000.0
        
        # Timeout configuration
        self.connection_timeout = self.config.get("timeout_policy", {}).get("connection_timeout_s", 10)
        self.read_timeout = self.config.get("timeout_policy", {}).get("read_timeout_s", 30)
        self.total_timeout = self.config.get("timeout_policy", {}).get("total_timeout_s", 60)
    
    def _default_config(self) -> Dict[str, Any]:
        """Default resilience configuration"""
        return {
            "dns_resolution": {
                "primary": ["8.8.8.8", "8.8.4.4"],
                "fallback": ["1.1.1.1", "1.0.0.1"]
            },
            "retry_policy": {
                "max_retries": 3,
                "backoff_multiplier": 2,
                "initial_delay_ms": 1000
            },
            "timeout_policy": {
                "connection_timeout_s": 10,
                "read_timeout_s": 30,
                "total_timeout_s": 60
            }
        }
    
    def resolve_dns(self, hostname: str, use_fallback: bool = False) -> Optional[str]:
        """
        Resolve DNS with primary and fallback support
        
        Args:
            hostname: The hostname to resolve
            use_fallback: Whether to use fallback DNS servers
        
        Returns:
            IP address or None if resolution fails
        """
        try:
            # Standard DNS resolution
            ip_address = socket.gethostbyname(hostname)
            self.connection_stats["dns_resolutions"] += 1
            return ip_address
        except socket.gaierror:
            if use_fallback:
                # Attempt custom DNS resolution (simplified)
                self.connection_stats["dns_fallbacks"] += 1
                # In production, this would use dnspython or similar
                # For now, return None to indicate fallback was attempted
                return None
            return None
    
    def test_connection(self, url: str, method: str = "GET", timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Test connection to a URL with proper timeout handling
        
        Args:
            url: The URL to test
            method: HTTP method to use
            timeout: Override timeout value
        
        Returns:
            Connection result with status and details
        """
        timeout = timeout or self.connection_timeout
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                allow_redirects=True
            )
            
            self.connection_stats["successful_connections"] += 1
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "url": url
            }
        except requests.exceptions.Timeout:
            self.connection_stats["failed_connections"] += 1
            return {
                "success": False,
                "error": "timeout",
                "url": url
            }
        except requests.exceptions.ConnectionError as e:
            self.connection_stats["failed_connections"] += 1
            return {
                "success": False,
                "error": "connection_error",
                "details": str(e),
                "url": url
            }
        except Exception as e:
            self.connection_stats["failed_connections"] += 1
            return {
                "success": False,
                "error": "unknown",
                "details": str(e),
                "url": url
            }
    
    def resilient_request(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retry and fallback mechanisms
        
        Args:
            url: The URL to request
            method: HTTP method to use
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            Response data or error information
        """
        delay = self.initial_delay
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Set timeouts if not provided
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = (self.connection_timeout, self.read_timeout)
                
                response = requests.request(method=method, url=url, **kwargs)
                
                if response.status_code < 500:
                    # Success or client error (don't retry client errors)
                    self.connection_stats["successful_connections"] += 1
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": response.text,
                        "headers": dict(response.headers),
                        "attempts": attempt + 1
                    }
                else:
                    # Server error - will retry
                    last_error = f"Server error: {response.status_code}"
            
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
            except Exception as e:
                last_error = f"Unknown error: {str(e)}"
            
            # Retry logic
            if attempt < self.max_retries:
                self.connection_stats["retries_performed"] += 1
                time.sleep(delay)
                delay *= self.backoff_multiplier
        
        # All retries exhausted
        self.connection_stats["failed_connections"] += 1
        return {
            "success": False,
            "error": last_error,
            "attempts": self.max_retries + 1,
            "url": url
        }
    
    def batch_health_check(self, urls: List[str]) -> Dict[str, Any]:
        """
        Perform health checks on multiple URLs
        
        Args:
            urls: List of URLs to check
        
        Returns:
            Health check results
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checked": len(urls),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for url in urls:
            check_result = self.test_connection(url)
            
            if check_result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(check_result)
        
        return results
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        total_attempts = self.connection_stats["successful_connections"] + self.connection_stats["failed_connections"]
        success_rate = (
            self.connection_stats["successful_connections"] / total_attempts * 100
            if total_attempts > 0 else 0
        )
        
        return {
            **self.connection_stats,
            "total_attempts": total_attempts,
            "success_rate_percent": round(success_rate, 2)
        }
    
    def reset_stats(self) -> None:
        """Reset connection statistics"""
        self.connection_stats = {
            "successful_connections": 0,
            "failed_connections": 0,
            "retries_performed": 0,
            "dns_resolutions": 0,
            "dns_fallbacks": 0
        }
    
    def export_health_report(self, output_file: str, health_results: Dict[str, Any]) -> None:
        """Export health check results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "health_check_results": health_results,
            "connection_stats": self.get_connection_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)


def main():
    """Main execution for network resilience testing"""
    print("🌐 Network Resilience Layer - Sovereign Edition")
    print("=" * 70)
    
    resilience = NetworkResilienceLayer()
    
    # Test critical endpoints
    critical_urls = [
        "https://api.netlify.com",
        "https://api.github.com",
        "https://pypi.org",
        "https://registry.npmjs.org"
    ]
    
    print("\n🔍 Performing health checks on critical endpoints...")
    health_results = resilience.batch_health_check(critical_urls)
    
    print(f"\n📊 Health Check Results:")
    print(f"  Total Checked: {health_results['total_checked']}")
    print(f"  Successful: {health_results['successful']}")
    print(f"  Failed: {health_results['failed']}")
    
    print("\n📋 Individual Results:")
    for detail in health_results['details']:
        status = "✅" if detail['success'] else "❌"
        url = detail.get('url', 'unknown')
        if detail['success']:
            response_time = detail.get('response_time_ms', 0)
            print(f"  {status} {url} ({response_time:.0f}ms)")
        else:
            error = detail.get('error', 'unknown')
            print(f"  {status} {url} (error: {error})")
    
    # Export results
    output_file = "bridge_backend/diagnostics/network_health_report.json"
    resilience.export_health_report(output_file, health_results)
    print(f"\n💾 Health report exported to: {output_file}")
    
    # Display connection statistics
    stats = resilience.get_connection_stats()
    print(f"\n📈 Connection Statistics:")
    print(f"  Total Attempts: {stats['total_attempts']}")
    print(f"  Success Rate: {stats['success_rate_percent']}%")
    print(f"  Retries Performed: {stats['retries_performed']}")
    print(f"  DNS Resolutions: {stats['dns_resolutions']}")
    
    print("\n" + "=" * 70)
    print("✅ Network Resilience Testing Complete")


if __name__ == "__main__":
    main()
