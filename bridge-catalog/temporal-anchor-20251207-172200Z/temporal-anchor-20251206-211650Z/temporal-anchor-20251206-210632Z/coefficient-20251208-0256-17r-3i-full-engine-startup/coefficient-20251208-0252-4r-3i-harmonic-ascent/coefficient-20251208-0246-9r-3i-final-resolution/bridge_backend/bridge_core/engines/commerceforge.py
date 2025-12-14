"""
CommerceForge - Commerce and Trading Engine
Advanced economic modeling and trade analysis engine
Provides comprehensive market simulation, trade optimization, and economic analytics
"""

import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class MarketType(Enum):
    """Types of markets"""
    COMMODITY = "commodity"
    CURRENCY = "currency"
    EQUITY = "equity"
    BOND = "bond"
    DERIVATIVE = "derivative"
    CRYPTO = "crypto"


class TradeType(Enum):
    """Types of trades"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    SHORT = "short"
    HEDGE = "hedge"


class OrderType(Enum):
    """Types of orders"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class TradingAsset:
    """Trading asset data structure"""
    asset_id: str
    symbol: str
    name: str
    market_type: MarketType
    current_price: float
    price_history: List[Tuple[str, float]]  # (timestamp, price)
    volatility: float
    volume: float
    market_cap: float
    created_at: str


@dataclass
class TradeOrder:
    """Trade order data structure"""
    order_id: str
    asset_id: str
    trade_type: TradeType
    order_type: OrderType
    quantity: float
    target_price: float
    current_price: float
    status: str  # pending, filled, cancelled, partial
    created_at: str
    filled_at: Optional[str]
    profit_loss: float


@dataclass
class Portfolio:
    """Trading portfolio data structure"""
    portfolio_id: str
    name: str
    total_value: float
    cash_balance: float
    positions: Dict[str, Dict[str, Any]]  # asset_id -> position data
    performance_history: List[Dict[str, Any]]
    risk_level: str
    created_at: str


class CommerceForge:
    """
    Commerce and Trading Engine
    
    The CommerceForge provides advanced economic modeling and trading capabilities,
    allowing the system to simulate markets, execute trades, manage portfolios,
    and analyze economic patterns and opportunities.
    
    Key Rituals:
    - forge_asset: Create and track trading assets
    - execute_trade: Process trade orders
    - analyze_market: Perform market analysis
    - optimize_portfolio: Portfolio optimization
    """
    
    def __init__(self, max_assets: int = 1000, max_orders: int = 5000, 
                 max_portfolios: int = 100):
        self.max_assets = max_assets
        self.max_orders = max_orders
        self.max_portfolios = max_portfolios
        self.assets: Dict[str, TradingAsset] = {}
        self.orders: Dict[str, TradeOrder] = {}
        self.portfolios: Dict[str, Portfolio] = {}
        self.market_data: Dict[str, Dict[str, Any]] = {}
        self.economic_indicators: Dict[str, float] = {
            "inflation_rate": 2.5,
            "interest_rate": 3.0,
            "gdp_growth": 2.8,
            "unemployment_rate": 4.2,
            "market_sentiment": 0.6  # -1 to 1 scale
        }
        self.metrics = {
            "total_assets": 0,
            "total_orders": 0,
            "total_portfolios": 0,
            "total_trade_volume": 0.0,
            "successful_trades": 0,
            "average_profit_margin": 0.0
        }
        logger.info("💰 CommerceForge Engine initialized")
    
    def forge_asset(self, symbol: str, name: str, market_type: MarketType,
                   initial_price: float, volatility: float = 0.1) -> Dict[str, Any]:
        """
        Create and track trading assets
        
        Args:
            symbol: Asset symbol (e.g., "AAPL", "BTC", "EUR/USD")
            name: Full name of the asset
            market_type: Type of market the asset belongs to
            initial_price: Initial price of the asset
            volatility: Price volatility factor (0.0-1.0)
            
        Returns:
            Dict containing asset data and market analysis
        """
        start_time = datetime.now(timezone.utc)
        
        if len(self.assets) >= self.max_assets:
            logger.warning("⚠️ Maximum assets reached")
            return {"error": "Asset limit exceeded"}
        
        asset_id = f"asset_{symbol.lower()}_{int(start_time.timestamp() * 1000)}"
        
        # Generate initial market data
        volume = random.uniform(10000, 1000000)  # Random initial volume
        market_cap = initial_price * volume * random.uniform(10, 1000)
        
        # Create asset
        asset = TradingAsset(
            asset_id=asset_id,
            symbol=symbol,
            name=name,
            market_type=market_type,
            current_price=initial_price,
            price_history=[(start_time.isoformat(), initial_price)],
            volatility=volatility,
            volume=volume,
            market_cap=market_cap,
            created_at=start_time.isoformat()
        )
        
        self.assets[asset_id] = asset
        
        # Initialize market data
        self.market_data[asset_id] = {
            "support_level": initial_price * 0.95,
            "resistance_level": initial_price * 1.05,
            "moving_average_20": initial_price,
            "rsi": 50.0,  # Relative Strength Index
            "macd": 0.0,  # MACD indicator
            "trend": "neutral"
        }
        
        # Update metrics
        self._update_metrics()
        
        logger.info(f"🏭 Forged asset {symbol} ({name}) at ${initial_price}")
        
        return {
            "asset_id": asset_id,
            "symbol": symbol,
            "name": name,
            "market_type": market_type.value,
            "initial_price": initial_price,
            "volatility": volatility,
            "volume": volume,
            "market_cap": market_cap,
            "market_analysis": self.market_data[asset_id],
            "created_at": start_time.isoformat()
        }
    
    def execute_trade(self, asset_id: str, trade_type: TradeType, 
                     quantity: float, order_type: OrderType = OrderType.MARKET,
                     target_price: Optional[float] = None,
                     portfolio_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process trade orders
        
        Args:
            asset_id: ID of asset to trade
            trade_type: Type of trade (buy, sell, etc.)
            quantity: Quantity to trade
            order_type: Type of order (market, limit, etc.)
            target_price: Target price for limit orders
            portfolio_id: Portfolio to execute trade in
            
        Returns:
            Dict containing trade execution results
        """
        start_time = datetime.now(timezone.utc)
        
        if len(self.orders) >= self.max_orders:
            # Clean up old completed orders
            completed_orders = [oid for oid, order in self.orders.items() 
                              if order.status in ["filled", "cancelled"]]
            for oid in completed_orders[:100]:  # Remove oldest 100
                del self.orders[oid]
        
        if asset_id not in self.assets:
            return {"error": f"Asset {asset_id} not found"}
        
        asset = self.assets[asset_id]
        order_id = f"order_{trade_type.value}_{int(start_time.timestamp() * 1000)}"
        
        # Determine execution price
        current_price = asset.current_price
        execution_price = current_price
        
        if order_type == OrderType.LIMIT and target_price:
            execution_price = target_price
        elif order_type == OrderType.MARKET:
            # Add small slippage for market orders
            slippage = random.uniform(-0.01, 0.01) * current_price
            execution_price = current_price + slippage
        
        # Calculate trade value
        trade_value = quantity * execution_price
        
        # Check if order can be filled immediately
        can_fill = self._can_fill_order(trade_type, order_type, current_price, target_price)
        
        # Create trade order
        order = TradeOrder(
            order_id=order_id,
            asset_id=asset_id,
            trade_type=trade_type,
            order_type=order_type,
            quantity=quantity,
            target_price=target_price or execution_price,
            current_price=current_price,
            status="filled" if can_fill else "pending",
            created_at=start_time.isoformat(),
            filled_at=start_time.isoformat() if can_fill else None,
            profit_loss=0.0
        )
        
        self.orders[order_id] = order
        
        # Update asset volume
        if can_fill:
            asset.volume += quantity
            self._update_price_history(asset_id, execution_price)
            
            # Update portfolio if specified
            if portfolio_id and portfolio_id in self.portfolios:
                self._update_portfolio_position(portfolio_id, asset_id, trade_type, 
                                              quantity, execution_price)
        
        # Calculate fees (simplified)
        fee_rate = 0.001  # 0.1%
        trading_fee = trade_value * fee_rate
        
        result = {
            "order_id": order_id,
            "asset_id": asset_id,
            "symbol": asset.symbol,
            "trade_type": trade_type.value,
            "order_type": order_type.value,
            "quantity": quantity,
            "execution_price": execution_price,
            "trade_value": trade_value,
            "trading_fee": trading_fee,
            "net_value": trade_value - trading_fee,
            "status": order.status,
            "filled_at": order.filled_at,
            "created_at": start_time.isoformat(),
            "market_impact": self._calculate_market_impact(quantity, asset.volume)
        }
        
        # Update metrics
        if can_fill:
            self.metrics["successful_trades"] += 1
            self.metrics["total_trade_volume"] += trade_value
        
        logger.info(f"📈 Executed {trade_type.value} order for {quantity} {asset.symbol} at ${execution_price}")
        
        return result
    
    def analyze_market(self, asset_id: str, analysis_type: str = "technical") -> Dict[str, Any]:
        """
        Perform market analysis
        
        Args:
            asset_id: ID of asset to analyze
            analysis_type: Type of analysis (technical, fundamental, sentiment)
            
        Returns:
            Dict containing market analysis results
        """
        start_time = datetime.now(timezone.utc)
        
        if asset_id not in self.assets:
            return {"error": f"Asset {asset_id} not found"}
        
        asset = self.assets[asset_id]
        
        if analysis_type == "technical":
            results = self._technical_analysis(asset)
        elif analysis_type == "fundamental":
            results = self._fundamental_analysis(asset)
        elif analysis_type == "sentiment":
            results = self._sentiment_analysis(asset)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
        
        analysis_result = {
            "asset_id": asset_id,
            "symbol": asset.symbol,
            "analysis_type": analysis_type,
            "current_price": asset.current_price,
            "analysis_results": results,
            "recommendation": self._generate_recommendation(results, analysis_type),
            "confidence_level": self._calculate_confidence(results),
            "analyzed_at": start_time.isoformat()
        }
        
        # Update market data
        self.market_data[asset_id].update(results)
        
        logger.info(f"📊 Performed {analysis_type} analysis on {asset.symbol}")
        
        return analysis_result
    
    def optimize_portfolio(self, portfolio_id: str, 
                          optimization_goal: str = "maximize_return") -> Dict[str, Any]:
        """
        Portfolio optimization
        
        Args:
            portfolio_id: ID of portfolio to optimize
            optimization_goal: Goal (maximize_return, minimize_risk, balanced)
            
        Returns:
            Dict containing optimization recommendations
        """
        start_time = datetime.now(timezone.utc)
        
        if portfolio_id not in self.portfolios:
            return {"error": f"Portfolio {portfolio_id} not found"}
        
        portfolio = self.portfolios[portfolio_id]
        
        # Analyze current portfolio
        current_analysis = self._analyze_portfolio_performance(portfolio)
        
        # Generate optimization recommendations
        if optimization_goal == "maximize_return":
            recommendations = self._maximize_return_strategy(portfolio)
        elif optimization_goal == "minimize_risk":
            recommendations = self._minimize_risk_strategy(portfolio)
        elif optimization_goal == "balanced":
            recommendations = self._balanced_strategy(portfolio)
        else:
            return {"error": f"Unknown optimization goal: {optimization_goal}"}
        
        # Calculate expected outcomes
        expected_outcomes = self._calculate_expected_outcomes(portfolio, recommendations)
        
        result = {
            "portfolio_id": portfolio_id,
            "optimization_goal": optimization_goal,
            "current_analysis": current_analysis,
            "recommendations": recommendations,
            "expected_outcomes": expected_outcomes,
            "implementation_cost": self._calculate_implementation_cost(recommendations),
            "optimized_at": start_time.isoformat()
        }
        
        logger.info(f"🎯 Optimized portfolio {portfolio_id} for {optimization_goal}")
        
        return result
    
    def create_portfolio(self, name: str, initial_cash: float = 100000.0,
                        risk_level: str = "moderate") -> Dict[str, Any]:
        """Create a new trading portfolio"""
        start_time = datetime.now(timezone.utc)
        
        if len(self.portfolios) >= self.max_portfolios:
            logger.warning("⚠️ Maximum portfolios reached")
            return {"error": "Portfolio limit exceeded"}
        
        portfolio_id = f"portfolio_{int(start_time.timestamp() * 1000)}"
        
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name=name,
            total_value=initial_cash,
            cash_balance=initial_cash,
            positions={},
            performance_history=[{
                "timestamp": start_time.isoformat(),
                "total_value": initial_cash,
                "cash_balance": initial_cash,
                "positions_value": 0.0
            }],
            risk_level=risk_level,
            created_at=start_time.isoformat()
        )
        
        self.portfolios[portfolio_id] = portfolio
        self._update_metrics()
        
        logger.info(f"🏦 Created portfolio '{name}' with ${initial_cash}")
        
        return {
            "portfolio_id": portfolio_id,
            "name": name,
            "initial_cash": initial_cash,
            "risk_level": risk_level,
            "created_at": start_time.isoformat()
        }
    
    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get specific asset by ID"""
        if asset_id not in self.assets:
            return None
        
        asset = self.assets[asset_id]
        return {
            "asset_id": asset.asset_id,
            "symbol": asset.symbol,
            "name": asset.name,
            "market_type": asset.market_type.value,
            "current_price": asset.current_price,
            "price_change_24h": self._calculate_price_change(asset, 24),
            "volatility": asset.volatility,
            "volume": asset.volume,
            "market_cap": asset.market_cap,
            "market_data": self.market_data.get(asset_id, {}),
            "created_at": asset.created_at
        }
    
    def list_assets(self, market_type: Optional[MarketType] = None) -> List[Dict[str, Any]]:
        """List assets with optional filtering"""
        assets = []
        
        for asset in self.assets.values():
            if market_type and asset.market_type != market_type:
                continue
            
            assets.append({
                "asset_id": asset.asset_id,
                "symbol": asset.symbol,
                "name": asset.name,
                "market_type": asset.market_type.value,
                "current_price": asset.current_price,
                "price_change_24h": self._calculate_price_change(asset, 24),
                "volume": asset.volume,
                "market_cap": asset.market_cap,
                "created_at": asset.created_at
            })
        
        return sorted(assets, key=lambda x: x["market_cap"], reverse=True)
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """Get specific portfolio by ID"""
        if portfolio_id not in self.portfolios:
            return None
        
        portfolio = self.portfolios[portfolio_id]
        
        # Calculate current positions value
        positions_value = 0.0
        position_details = {}
        
        for asset_id, position in portfolio.positions.items():
            if asset_id in self.assets:
                current_price = self.assets[asset_id].current_price
                position_value = position["quantity"] * current_price
                positions_value += position_value
                
                position_details[asset_id] = {
                    "symbol": self.assets[asset_id].symbol,
                    "quantity": position["quantity"],
                    "average_price": position["average_price"],
                    "current_price": current_price,
                    "position_value": position_value,
                    "unrealized_pnl": position_value - (position["quantity"] * position["average_price"])
                }
        
        total_value = portfolio.cash_balance + positions_value
        
        return {
            "portfolio_id": portfolio.portfolio_id,
            "name": portfolio.name,
            "total_value": total_value,
            "cash_balance": portfolio.cash_balance,
            "positions_value": positions_value,
            "positions": position_details,
            "performance": self._calculate_portfolio_performance(portfolio),
            "risk_metrics": self._calculate_portfolio_risk(portfolio),
            "created_at": portfolio.created_at
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get CommerceForge engine metrics"""
        return {
            **self.metrics,
            "current_assets": len(self.assets),
            "max_assets": self.max_assets,
            "current_orders": len(self.orders),
            "max_orders": self.max_orders,
            "current_portfolios": len(self.portfolios),
            "max_portfolios": self.max_portfolios,
            "economic_indicators": self.economic_indicators,
            "market_types_tracked": list(set(asset.market_type.value for asset in self.assets.values()))
        }
    
    # Private helper methods
    def _update_metrics(self) -> None:
        """Update engine metrics"""
        self.metrics["total_assets"] = len(self.assets)
        self.metrics["total_orders"] = len(self.orders)
        self.metrics["total_portfolios"] = len(self.portfolios)
        
        # Calculate average profit margin
        profitable_trades = [order for order in self.orders.values() 
                           if order.status == "filled" and order.profit_loss > 0]
        if profitable_trades:
            self.metrics["average_profit_margin"] = sum(
                order.profit_loss for order in profitable_trades
            ) / len(profitable_trades)
    
    def _can_fill_order(self, trade_type: TradeType, order_type: OrderType,
                       current_price: float, target_price: Optional[float]) -> bool:
        """Check if order can be filled immediately"""
        if order_type == OrderType.MARKET:
            return True
        
        if order_type == OrderType.LIMIT and target_price:
            if trade_type == TradeType.BUY and current_price <= target_price:
                return True
            if trade_type == TradeType.SELL and current_price >= target_price:
                return True
        
        return False
    
    def _update_price_history(self, asset_id: str, new_price: float) -> None:
        """Update asset price history"""
        if asset_id in self.assets:
            asset = self.assets[asset_id]
            timestamp = datetime.now(timezone.utc).isoformat()
            asset.price_history.append((timestamp, new_price))
            asset.current_price = new_price
            
            # Keep only last 100 price points
            if len(asset.price_history) > 100:
                asset.price_history = asset.price_history[-100:]
    
    def _update_portfolio_position(self, portfolio_id: str, asset_id: str,
                                 trade_type: TradeType, quantity: float, price: float) -> None:
        """Update portfolio position after trade"""
        portfolio = self.portfolios[portfolio_id]
        
        if asset_id not in portfolio.positions:
            portfolio.positions[asset_id] = {
                "quantity": 0.0,
                "average_price": 0.0,
                "total_cost": 0.0
            }
        
        position = portfolio.positions[asset_id]
        
        if trade_type == TradeType.BUY:
            # Add to position
            new_total_cost = position["total_cost"] + (quantity * price)
            new_quantity = position["quantity"] + quantity
            position["quantity"] = new_quantity
            position["average_price"] = new_total_cost / new_quantity if new_quantity > 0 else 0
            position["total_cost"] = new_total_cost
            
            # Reduce cash balance
            portfolio.cash_balance -= quantity * price
            
        elif trade_type == TradeType.SELL:
            # Reduce position
            if position["quantity"] >= quantity:
                position["quantity"] -= quantity
                if position["quantity"] == 0:
                    position["average_price"] = 0
                    position["total_cost"] = 0
                else:
                    position["total_cost"] -= quantity * position["average_price"]
                
                # Increase cash balance
                portfolio.cash_balance += quantity * price
    
    def _calculate_price_change(self, asset: TradingAsset, hours: int) -> float:
        """Calculate price change over specified hours"""
        if len(asset.price_history) < 2:
            return 0.0
        
        # Find price from hours ago (simplified)
        target_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Use the oldest available price if not enough history
        old_price = asset.price_history[0][1]
        current_price = asset.current_price
        
        return ((current_price - old_price) / old_price) * 100 if old_price > 0 else 0.0
    
    def _calculate_market_impact(self, trade_quantity: float, total_volume: float) -> float:
        """Calculate market impact of trade"""
        if total_volume <= 0:
            return 0.0
        
        impact_ratio = trade_quantity / total_volume
        return min(impact_ratio * 100, 10.0)  # Cap at 10%
    
    def _technical_analysis(self, asset: TradingAsset) -> Dict[str, Any]:
        """Perform technical analysis"""
        prices = [price for _, price in asset.price_history]
        
        if len(prices) < 2:
            return {"error": "Insufficient price history"}
        
        # Moving averages
        ma_5 = sum(prices[-5:]) / min(len(prices), 5)
        ma_20 = sum(prices[-20:]) / min(len(prices), 20)
        
        # RSI calculation (simplified)
        if len(prices) >= 14:
            gains = []
            losses = []
            for i in range(1, min(15, len(prices))):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / max(len(gains), 1)
            avg_loss = sum(losses) / max(len(losses), 1)
            rs = avg_gain / max(avg_loss, 0.001)
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50.0
        
        # Trend analysis
        if ma_5 > ma_20:
            trend = "bullish"
        elif ma_5 < ma_20:
            trend = "bearish"
        else:
            trend = "neutral"
        
        return {
            "moving_average_5": ma_5,
            "moving_average_20": ma_20,
            "rsi": rsi,
            "trend": trend,
            "support_level": min(prices[-10:]) if len(prices) >= 10 else asset.current_price * 0.95,
            "resistance_level": max(prices[-10:]) if len(prices) >= 10 else asset.current_price * 1.05,
            "volatility_index": asset.volatility * 100
        }
    
    def _fundamental_analysis(self, asset: TradingAsset) -> Dict[str, Any]:
        """Perform fundamental analysis"""
        # Market cap analysis
        market_cap_category = "large" if asset.market_cap > 10000000 else "small"
        
        # Volume analysis
        volume_trend = "high" if asset.volume > 100000 else "low"
        
        # Price-to-volume ratio
        pv_ratio = asset.current_price / max(asset.volume / 1000, 1)
        
        return {
            "market_cap": asset.market_cap,
            "market_cap_category": market_cap_category,
            "volume": asset.volume,
            "volume_trend": volume_trend,
            "price_volume_ratio": pv_ratio,
            "liquidity_score": min(asset.volume / 10000, 10),  # 0-10 scale
            "market_dominance": asset.market_cap / 100000000 * 100  # Simplified
        }
    
    def _sentiment_analysis(self, asset: TradingAsset) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        # Simulate sentiment based on price movement and volatility
        recent_change = self._calculate_price_change(asset, 24)
        
        if recent_change > 5:
            sentiment = "very_bullish"
            sentiment_score = 0.8
        elif recent_change > 2:
            sentiment = "bullish"
            sentiment_score = 0.6
        elif recent_change < -5:
            sentiment = "very_bearish"
            sentiment_score = -0.8
        elif recent_change < -2:
            sentiment = "bearish"
            sentiment_score = -0.6
        else:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        # Factor in volatility
        volatility_factor = min(asset.volatility * 2, 1.0)
        uncertainty = volatility_factor * 0.5
        
        return {
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "uncertainty": uncertainty,
            "market_fear_greed": 50 + (sentiment_score * 30),  # 0-100 scale
            "social_mentions": random.randint(10, 1000),  # Simulated
            "news_sentiment": sentiment_score * 0.8
        }
    
    def _generate_recommendation(self, analysis_results: Dict[str, Any], 
                               analysis_type: str) -> str:
        """Generate trading recommendation based on analysis"""
        if analysis_type == "technical":
            rsi = analysis_results.get("rsi", 50)
            trend = analysis_results.get("trend", "neutral")
            
            if rsi < 30 and trend == "bullish":
                return "strong_buy"
            elif rsi < 30:
                return "buy"
            elif rsi > 70 and trend == "bearish":
                return "strong_sell"
            elif rsi > 70:
                return "sell"
            else:
                return "hold"
        
        elif analysis_type == "sentiment":
            sentiment_score = analysis_results.get("sentiment_score", 0)
            
            if sentiment_score > 0.6:
                return "buy"
            elif sentiment_score < -0.6:
                return "sell"
            else:
                return "hold"
        
        return "hold"
    
    def _calculate_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate confidence level in analysis"""
        # Simple confidence calculation based on data availability
        non_null_metrics = sum(1 for v in analysis_results.values() 
                              if v is not None and v != "unknown")
        total_metrics = len(analysis_results)
        
        return min(non_null_metrics / max(total_metrics, 1), 1.0)
    
    def _analyze_portfolio_performance(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Analyze portfolio performance"""
        if not portfolio.performance_history:
            return {"error": "No performance history"}
        
        initial_value = portfolio.performance_history[0]["total_value"]
        current_value = portfolio.total_value
        
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Calculate volatility from performance history
        if len(portfolio.performance_history) > 1:
            returns = []
            for i in range(1, len(portfolio.performance_history)):
                prev_val = portfolio.performance_history[i-1]["total_value"]
                curr_val = portfolio.performance_history[i]["total_value"]
                returns.append((curr_val - prev_val) / prev_val)
            
            avg_return = sum(returns) / len(returns)
            volatility = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns))
        else:
            volatility = 0.0
        
        return {
            "total_return": total_return,
            "volatility": volatility * 100,
            "sharpe_ratio": total_return / max(volatility * 100, 1),
            "max_drawdown": self._calculate_max_drawdown(portfolio.performance_history),
            "winning_positions": sum(1 for pos in portfolio.positions.values() 
                                   if pos.get("unrealized_pnl", 0) > 0),
            "total_positions": len(portfolio.positions)
        }
    
    def _calculate_max_drawdown(self, performance_history: List[Dict[str, Any]]) -> float:
        """Calculate maximum drawdown"""
        if len(performance_history) < 2:
            return 0.0
        
        peak = performance_history[0]["total_value"]
        max_drawdown = 0.0
        
        for record in performance_history[1:]:
            value = record["total_value"]
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    def _maximize_return_strategy(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Generate maximum return optimization strategy"""
        recommendations = []
        
        # Analyze current positions for high-growth potential
        for asset_id, position in portfolio.positions.items():
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                analysis = self._technical_analysis(asset)
                
                if analysis.get("trend") == "bullish" and analysis.get("rsi", 50) < 70:
                    recommendations.append({
                        "action": "increase_position",
                        "asset_id": asset_id,
                        "symbol": asset.symbol,
                        "current_weight": position["quantity"] * asset.current_price / portfolio.total_value,
                        "recommended_weight": 0.15,  # 15% allocation
                        "reason": "Strong bullish trend with room for growth"
                    })
        
        return recommendations
    
    def _minimize_risk_strategy(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Generate risk minimization strategy"""
        recommendations = []
        
        # Diversification recommendations
        total_positions = len(portfolio.positions)
        if total_positions < 5:
            recommendations.append({
                "action": "diversify",
                "reason": "Increase diversification to reduce concentration risk",
                "target_positions": 8,
                "current_positions": total_positions
            })
        
        # Reduce high-volatility positions
        for asset_id, position in portfolio.positions.items():
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                if asset.volatility > 0.3:  # High volatility
                    recommendations.append({
                        "action": "reduce_position",
                        "asset_id": asset_id,
                        "symbol": asset.symbol,
                        "reason": f"High volatility ({asset.volatility:.1%}) increases portfolio risk",
                        "recommended_reduction": 0.25  # Reduce by 25%
                    })
        
        return recommendations
    
    def _balanced_strategy(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Generate balanced optimization strategy"""
        return_recs = self._maximize_return_strategy(portfolio)
        risk_recs = self._minimize_risk_strategy(portfolio)
        
        # Combine and balance recommendations
        balanced_recs = []
        
        # Moderate the return recommendations
        for rec in return_recs[:3]:  # Take top 3 return recommendations
            if rec["action"] == "increase_position":
                rec["recommended_weight"] *= 0.7  # Reduce by 30%
                rec["reason"] += " (moderated for risk)"
            balanced_recs.append(rec)
        
        # Include some risk management
        for rec in risk_recs[:2]:  # Take top 2 risk recommendations
            balanced_recs.append(rec)
        
        return balanced_recs
    
    def _calculate_expected_outcomes(self, portfolio: Portfolio, 
                                   recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate expected outcomes of optimization"""
        # Simplified calculation
        current_return = self._analyze_portfolio_performance(portfolio).get("total_return", 0)
        current_risk = self._calculate_portfolio_risk(portfolio).get("overall_risk", 5)
        
        # Estimate impact of recommendations
        expected_return_change = len([r for r in recommendations if "increase" in r.get("action", "")]) * 2
        expected_risk_change = len([r for r in recommendations if "reduce" in r.get("action", "")]) * -1
        
        return {
            "current_return": current_return,
            "expected_return": current_return + expected_return_change,
            "current_risk": current_risk,
            "expected_risk": max(current_risk + expected_risk_change, 1),
            "implementation_timeline": "2-4 weeks",
            "confidence": 0.75
        }
    
    def _calculate_implementation_cost(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate cost of implementing recommendations"""
        # Simplified cost calculation
        num_trades = sum(1 for rec in recommendations if rec.get("action") in ["increase_position", "reduce_position"])
        
        return {
            "estimated_trades": num_trades,
            "trading_fees": num_trades * 50,  # $50 per trade
            "market_impact": num_trades * 0.1,  # 0.1% market impact per trade
            "total_cost": num_trades * 50 + (num_trades * 0.001 * 10000)  # Approximate total cost
        }
    
    def _calculate_portfolio_performance(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        return self._analyze_portfolio_performance(portfolio)
    
    def _calculate_portfolio_risk(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate portfolio risk metrics"""
        if not portfolio.positions:
            return {"overall_risk": 0, "concentration_risk": 0, "volatility_risk": 0}
        
        # Concentration risk
        total_value = portfolio.total_value
        position_weights = []
        volatility_weighted_risk = 0
        
        for asset_id, position in portfolio.positions.items():
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                position_value = position["quantity"] * asset.current_price
                weight = position_value / total_value
                position_weights.append(weight)
                volatility_weighted_risk += weight * asset.volatility
        
        # Calculate concentration (Herfindahl index)
        concentration_risk = sum(w ** 2 for w in position_weights) * 10  # Scale to 0-10
        
        # Overall risk score (0-10 scale)
        overall_risk = min((concentration_risk + volatility_weighted_risk * 5), 10)
        
        return {
            "overall_risk": overall_risk,
            "concentration_risk": concentration_risk,
            "volatility_risk": volatility_weighted_risk * 5,
            "diversification_score": 10 - concentration_risk
        }