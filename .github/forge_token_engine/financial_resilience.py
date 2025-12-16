#!/usr/bin/env python3
"""
Financial Resilience Manager
Ensures bridge operates even when external funding sources have issues.

This module provides:
1. Multi-provider redundancy
2. Automatic failover between compute providers
3. Cost monitoring and alerting
4. Resource quota management

IMPORTANT: This achieves "financial sovereignty" through smart orchestration
of free-tier services, NOT through creating fake tokens or bypassing legitimate billing.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundingSource(Enum):
    """Available funding sources for compute"""
    GITHUB_FREE_TIER = "github_free"  # 2000 min/month on private repos
    RENDER_FREE = "render_free"  # 750 hours/month
    NETLIFY_FREE = "netlify_free"  # 300 build min/month
    SELF_HOSTED = "self_hosted"  # No external costs
    VERCEL_FREE = "vercel_free"  # 100 GB-hours/month


@dataclass
class ProviderQuota:
    """Quota information for a provider"""
    source: FundingSource
    monthly_limit: int  # in minutes
    used_this_month: int
    reset_date: str
    is_available: bool
    cost_per_minute: float  # After free tier exhausted
    
    @property
    def remaining(self) -> int:
        return max(0, self.monthly_limit - self.used_this_month)
    
    @property
    def utilization_percentage(self) -> float:
        if self.monthly_limit == 0:
            return 0.0
        return (self.used_this_month / self.monthly_limit) * 100


class FinancialResilienceManager:
    """
    Manages financial resilience by orchestrating multiple funding sources
    and ensuring bridge operations continue regardless of any single provider's status.
    """
    
    def __init__(self):
        self.quotas = self._initialize_quotas()
        self.failover_chain = self._build_failover_chain()
        self.alert_thresholds = {
            'warning': 70,  # % utilization
            'critical': 90  # % utilization
        }
    
    def _initialize_quotas(self) -> Dict[FundingSource, ProviderQuota]:
        """Initialize quota tracking for all funding sources"""
        quotas_file = '.github/forge_token_engine/quotas.json'
        
        # Default quotas
        defaults = {
            FundingSource.GITHUB_FREE_TIER: ProviderQuota(
                source=FundingSource.GITHUB_FREE_TIER,
                monthly_limit=2000,  # GitHub Free tier for private repos
                used_this_month=0,
                reset_date=self._get_next_reset_date(),
                is_available=True,
                cost_per_minute=0.008
            ),
            FundingSource.RENDER_FREE: ProviderQuota(
                source=FundingSource.RENDER_FREE,
                monthly_limit=45000,  # 750 hours * 60 min
                used_this_month=0,
                reset_date=self._get_next_reset_date(),
                is_available=bool(os.getenv('RENDER_DEPLOY_HOOK')),
                cost_per_minute=0.0  # Free tier
            ),
            FundingSource.NETLIFY_FREE: ProviderQuota(
                source=FundingSource.NETLIFY_FREE,
                monthly_limit=300,
                used_this_month=0,
                reset_date=self._get_next_reset_date(),
                is_available=bool(os.getenv('NETLIFY_AUTH_TOKEN')),
                cost_per_minute=0.0  # Free tier
            ),
            FundingSource.SELF_HOSTED: ProviderQuota(
                source=FundingSource.SELF_HOSTED,
                monthly_limit=999999,  # Effectively unlimited
                used_this_month=0,
                reset_date=self._get_next_reset_date(),
                is_available=self._check_self_hosted_available(),
                cost_per_minute=0.0  # Zero cost
            ),
            FundingSource.VERCEL_FREE: ProviderQuota(
                source=FundingSource.VERCEL_FREE,
                monthly_limit=6000,  # 100 GB-hours ~= 100 hours for typical workload
                used_this_month=0,
                reset_date=self._get_next_reset_date(),
                is_available=bool(os.getenv('VERCEL_TOKEN')),
                cost_per_minute=0.0  # Free tier
            ),
        }
        
        # Load saved quotas if they exist
        if os.path.exists(quotas_file):
            try:
                with open(quotas_file, 'r') as f:
                    saved_data = json.load(f)
                    for source_name, data in saved_data.items():
                        source = FundingSource(source_name)
                        if source in defaults:
                            defaults[source].used_this_month = data.get('used_this_month', 0)
            except Exception as e:
                logger.warning(f"Could not load saved quotas: {e}")
        
        return defaults
    
    def _get_next_reset_date(self) -> str:
        """Calculate next monthly reset date (1st of next month)"""
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        return next_month.isoformat()
    
    def _check_self_hosted_available(self) -> bool:
        """Check if self-hosted runners are configured and available"""
        config_file = '.github/self-hosted-runner.json'
        if not os.path.exists(config_file):
            return False
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('enabled', False) and config.get('healthy', False)
        except:
            return False
    
    def _build_failover_chain(self) -> List[FundingSource]:
        """
        Build priority-ordered failover chain.
        Order: Self-hosted (free) -> Free tiers (free) -> GitHub (paid after limit)
        """
        chain = []
        
        # Priority 1: Self-hosted (zero cost, unlimited)
        if self.quotas[FundingSource.SELF_HOSTED].is_available:
            chain.append(FundingSource.SELF_HOSTED)
        
        # Priority 2: Render free tier (massive free quota)
        if self.quotas[FundingSource.RENDER_FREE].is_available:
            chain.append(FundingSource.RENDER_FREE)
        
        # Priority 3: Vercel free tier
        if self.quotas[FundingSource.VERCEL_FREE].is_available:
            chain.append(FundingSource.VERCEL_FREE)
        
        # Priority 4: Netlify free tier
        if self.quotas[FundingSource.NETLIFY_FREE].is_available:
            chain.append(FundingSource.NETLIFY_FREE)
        
        # Priority 5: GitHub free tier (fallback, may incur costs)
        if self.quotas[FundingSource.GITHUB_FREE_TIER].is_available:
            chain.append(FundingSource.GITHUB_FREE_TIER)
        
        return chain
    
    def ensure_sovereign_funding(self, required_minutes: int) -> Tuple[bool, FundingSource, str]:
        """
        Ensure funding is available for required compute minutes.
        
        Returns:
            (success, funding_source, message)
        """
        logger.info(f"Ensuring funding for {required_minutes} minutes of compute")
        
        # Try each source in failover chain
        for source in self.failover_chain:
            quota = self.quotas[source]
            
            if not quota.is_available:
                logger.debug(f"{source.value} is not available, trying next")
                continue
            
            if quota.remaining >= required_minutes:
                logger.info(f"✅ Funding secured via {source.value} ({quota.remaining} min available)")
                return (True, source, f"Secured via {source.value}")
            
            logger.debug(f"{source.value} has insufficient quota ({quota.remaining} < {required_minutes})")
        
        # No funding source has enough quota
        logger.error("❌ No funding source has sufficient quota!")
        return (False, None, "All funding sources exhausted")
    
    def record_usage(self, source: FundingSource, minutes: int):
        """Record compute usage for a funding source"""
        if source in self.quotas:
            self.quotas[source].used_this_month += minutes
            self._save_quotas()
            self._check_alerts(source)
    
    def _check_alerts(self, source: FundingSource):
        """Check if usage has crossed alert thresholds"""
        quota = self.quotas[source]
        utilization = quota.utilization_percentage
        
        if utilization >= self.alert_thresholds['critical']:
            logger.critical(
                f"🚨 CRITICAL: {source.value} at {utilization:.1f}% utilization!"
            )
        elif utilization >= self.alert_thresholds['warning']:
            logger.warning(
                f"⚠️  WARNING: {source.value} at {utilization:.1f}% utilization"
            )
    
    def _save_quotas(self):
        """Save current quota status to file"""
        quotas_file = '.github/forge_token_engine/quotas.json'
        os.makedirs(os.path.dirname(quotas_file), exist_ok=True)
        
        data = {}
        for source, quota in self.quotas.items():
            data[source.value] = asdict(quota)
            data[source.value]['source'] = source.value  # Ensure it's a string
        
        with open(quotas_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_resilience_status(self) -> Dict:
        """Get comprehensive resilience status report"""
        total_available_minutes = sum(
            q.remaining for q in self.quotas.values() if q.is_available
        )
        
        sources_status = []
        for source, quota in self.quotas.items():
            sources_status.append({
                'source': source.value,
                'available': quota.is_available,
                'quota_remaining': quota.remaining,
                'quota_limit': quota.monthly_limit,
                'utilization_pct': quota.utilization_percentage,
                'cost_per_minute': quota.cost_per_minute,
                'reset_date': quota.reset_date
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_available_minutes': total_available_minutes,
            'failover_chain': [s.value for s in self.failover_chain],
            'sources': sources_status,
            'resilience_score': self._calculate_resilience_score()
        }
    
    def _calculate_resilience_score(self) -> float:
        """
        Calculate resilience score (0-100) based on:
        - Number of available funding sources
        - Total available minutes
        - Diversity of providers
        """
        # Base score from number of available sources
        available_count = sum(1 for q in self.quotas.values() if q.is_available)
        diversity_score = (available_count / len(self.quotas)) * 40
        
        # Score from total available capacity
        total_minutes = sum(q.remaining for q in self.quotas.values() if q.is_available)
        capacity_score = min(40, (total_minutes / 10000) * 40)  # Cap at 10k minutes
        
        # Bonus for self-hosted availability
        self_hosted_bonus = 20 if self.quotas[FundingSource.SELF_HOSTED].is_available else 0
        
        return min(100, diversity_score + capacity_score + self_hosted_bonus)


def main():
    """Example usage demonstrating financial resilience"""
    manager = FinancialResilienceManager()
    
    print("\n" + "="*70)
    print("FINANCIAL RESILIENCE STATUS")
    print("="*70)
    
    status = manager.get_resilience_status()
    print(json.dumps(status, indent=2))
    
    print("\n" + "="*70)
    print("FUNDING AVAILABILITY TEST")
    print("="*70)
    
    # Test securing funding for various workloads
    test_cases = [100, 500, 1000, 5000]
    for minutes in test_cases:
        success, source, msg = manager.ensure_sovereign_funding(minutes)
        if success:
            print(f"✅ {minutes} minutes: {msg}")
        else:
            print(f"❌ {minutes} minutes: {msg}")
    
    print(f"\n🛡️  Resilience Score: {status['resilience_score']:.1f}/100")


if __name__ == "__main__":
    main()
