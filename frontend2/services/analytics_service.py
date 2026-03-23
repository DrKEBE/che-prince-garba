"""
Service d'analyse et de statistiques avancées
"""
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from services.api_client import APIClient
from config.constants import COLORS
from utils.formatters import format_currency, format_number, format_percentage
from utils.session_state import get_session_state, update_session_state
from utils.cache import CacheManager

class AnalyticsService:
    """Service d'analyse de données pour le dashboard"""
    
    def __init__(self):
        self.api = APIClient()
        self.cache = CacheManager()
    
    def get_dashboard_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Récupère les statistiques du dashboard"""
        cache_key = "dashboard_stats"
        
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        try:
            data = self.api.get_dashboard_stats()
            self.cache.set(cache_key, data, ttl_seconds=60)
            return data
        except Exception as e:
            st.error(f"Erreur récupération stats: {str(e)}")
            return self._get_fallback_stats()
    
    def get_sales_trend(self, days: int = 30, group_by: str = "day") -> Dict[str, Any]:
        """Analyse des tendances de ventes"""
        cache_key = f"sales_trend_{days}_{group_by}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            data = self.api.get_sales_trend(days, group_by)
            analysis = self._analyze_sales_trend(data)
            self.cache.set(cache_key, analysis, ttl_seconds=300)
            return analysis
        except Exception as e:
            st.error(f"Erreur analyse tendances: {str(e)}")
            return self._get_empty_trend()
    
    def get_top_products_analysis(self, limit: int = 10, days: int = 30) -> Dict[str, Any]:
        """Analyse détaillée des meilleurs produits"""
        cache_key = f"top_products_analysis_{limit}_{days}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            products = self.api.get_top_products(limit, days)
            analysis = self._analyze_top_products(products)
            self.cache.set(cache_key, analysis, ttl_seconds=300)
            return analysis
        except Exception as e:
            st.error(f"Erreur analyse produits: {str(e)}")
            return {"products": [], "summary": {}, "categories": []}
    
    def get_client_insights(self, days: int = 90) -> Dict[str, Any]:
        """Analyse des comportements clients"""
        try:
            data = self.api.get_dashboard_stats()  # À adapter quand l'endpoint spécifique sera disponible
            return self._analyze_client_behavior(data)
        except Exception as e:
            st.error(f"Erreur analyse clients: {str(e)}")
            return {"segmentation": {}, "loyalty": {}, "retention": {}}
    
    def get_inventory_health(self) -> Dict[str, Any]:
        """Analyse de la santé des stocks"""
        try:
            alerts = self.api.get_stock_alerts()
            products = self.api.get_products()
            return self._analyze_inventory_health(alerts, products)
        except Exception as e:
            st.error(f"Erreur analyse stocks: {str(e)}")
            return {"status": "ERROR", "metrics": {}, "alerts": []}
    
    def get_profit_analysis(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Analyse de profitabilité"""
        cache_key = f"profit_analysis_{start_date}_{end_date}"
        cached = self.cache.get(cache_key)
        
        if cached:
            return cached
        
        try:
            data = self.api.get_profit_analysis(start_date, end_date)
            enhanced_data = self._enhance_profit_analysis(data)
            self.cache.set(cache_key, enhanced_data, ttl_seconds=300)
            return enhanced_data
        except Exception as e:
            st.error(f"Erreur analyse profit: {str(e)}")
            return self._get_empty_profit_analysis()
    
    def get_performance_metrics(self, period: str = "month") -> Dict[str, Any]:
        """Métriques de performance globale"""
        try:
            dashboard_data = self.api.get_dashboard_stats()
            return self._calculate_performance_metrics(dashboard_data, period)
        except Exception as e:
            st.error(f"Erreur métriques performance: {str(e)}")
            return {"kpis": {}, "trends": {}, "benchmarks": {}}
    
    def create_sales_forecast(self, historical_days: int = 90, forecast_days: int = 30) -> Dict[str, Any]:
        """Crée une prévision des ventes"""
        try:
            # Récupérer les données historiques
            sales_data = self.get_sales_trend(historical_days, "day")
            
            # Créer la prévision (version simplifiée)
            forecast = self._calculate_sales_forecast(sales_data, forecast_days)
            return forecast
        except Exception as e:
            st.error(f"Erreur prévision: {str(e)}")
            return {"forecast": [], "accuracy": 0, "confidence_interval": {}}
    
    # =========================
    # MÉTHODES PRIVÉES D'ANALYSE
    # =========================
    
    def _analyze_sales_trend(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyse les tendances de ventes"""
        if not data:
            return self._get_empty_trend()
        
        df = pd.DataFrame(data)
        
        # Calculer les métriques
        total_revenue = df['amount'].sum()
        total_profit = df['profit'].sum()
        avg_daily_sales = df['sales_count'].mean()
        growth_rate = self._calculate_growth_rate(df['amount'].tolist())
        
        # Identifier les patterns
        patterns = self._identify_sales_patterns(df)
        
        return {
            "period_summary": {
                "total_revenue": total_revenue,
                "total_profit": total_profit,
                "avg_daily_sales": avg_daily_sales,
                "growth_rate": growth_rate,
                "peak_day": df.loc[df['amount'].idxmax()]['period'] if not df.empty else None,
                "lowest_day": df.loc[df['amount'].idxmin()]['period'] if not df.empty else None
            },
            "data": data,
            "patterns": patterns,
            "recommendations": self._generate_sales_recommendations(df)
        }
    
    def _analyze_top_products(self, products: List[Dict]) -> Dict[str, Any]:
        """Analyse détaillée des meilleurs produits"""
        if not products:
            return {"products": [], "summary": {}, "categories": []}
        
        df = pd.DataFrame(products)
        
        # Analyse par catégorie
        category_analysis = df.groupby('category').agg({
            'total_revenue': 'sum',
            'total_profit': 'sum',
            'total_sold': 'sum'
        }).reset_index()
        
        # Identifier les opportunités
        opportunities = self._identify_product_opportunities(df)
        
        return {
            "products": products,
            "summary": {
                "total_revenue": df['total_revenue'].sum(),
                "total_profit": df['total_profit'].sum(),
                "total_units": df['total_sold'].sum(),
                "avg_margin": df['margin_percentage'].mean() if 'margin_percentage' in df.columns else 0
            },
            "categories": category_analysis.to_dict('records'),
            "opportunities": opportunities
        }
    
    def _analyze_client_behavior(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse du comportement client"""
        return {
            "segmentation": {
                "vip_clients": data.get('vip_clients', 0),
                "new_clients": data.get('new_clients_month', 0),
                "inactive_clients": data.get('inactive_clients', 0),
                "total_clients": data.get('total_clients', 0)
            },
            "loyalty": {
                "avg_purchase_frequency": data.get('conversion_rate', 0) / 100 if data.get('conversion_rate') else 0,
                "avg_ticket": data.get('avg_ticket', 0),
                "lifetime_value": self._estimate_client_lifetime_value(data)
            },
            "retention": {
                "retention_rate": self._calculate_retention_rate(data),
                "churn_rate": self._estimate_churn_rate(data),
                "repeat_purchase_rate": data.get('conversion_rate', 0) / 100 if data.get('conversion_rate') else 0
            }
        }
    
    def _analyze_inventory_health(self, alerts: Dict, products: List[Dict]) -> Dict[str, Any]:
        """Analyse la santé des stocks"""
        if not products:
            return {"status": "NO_DATA", "metrics": {}, "alerts": []}
        
        df = pd.DataFrame(products)
        
        # Calculer les métriques
        total_products = len(df)
        out_of_stock = len(alerts.get('out_of_stock', []))
        low_stock = len(alerts.get('low_stock', []))
        stock_value = self._calculate_inventory_value(df)
        turnover_rate = self._calculate_turnover_rate(df)
        
        # Évaluer la santé
        health_score = self._calculate_inventory_health_score(out_of_stock, low_stock, total_products)
        
        return {
            "status": self._get_inventory_status(health_score),
            "metrics": {
                "health_score": health_score,
                "total_products": total_products,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock,
                "stock_value": stock_value,
                "turnover_rate": turnover_rate,
                "stock_coverage": self._calculate_stock_coverage(df)
            },
            "alerts": alerts,
            "recommendations": self._generate_inventory_recommendations(alerts, df)
        }
    
    def _enhance_profit_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit l'analyse de profit"""
        if not data:
            return self._get_empty_profit_analysis()
        
        # Calculer des ratios additionnels
        gross_margin = (data.get('gross_profit', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0
        net_margin = (data.get('net_profit', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0
        
        return {
            **data,
            "ratios": {
                "gross_margin": gross_margin,
                "net_margin": net_margin,
                "expense_ratio": (data.get('total_expenses', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0,
                "cogs_ratio": (data.get('cogs', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0
            },
            "benchmarks": self._get_profit_benchmarks(data),
            "trend_analysis": self._analyze_profit_trends(data)
        }
    
    def _calculate_performance_metrics(self, data: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Calcule les métriques de performance"""
        return {
            "kpis": {
                "revenue_growth": data.get('revenue_trend', 0),
                "profit_margin": data.get('profit_margin', 0),
                "conversion_rate": data.get('conversion_rate', 0),
                "client_acquisition_cost": self._estimate_cac(data),
                "client_lifetime_value": self._estimate_clv(data),
                "inventory_turnover": data.get('total_sales', 0) / data.get('total_products', 1) if data.get('total_products') else 0
            },
            "trends": {
                "revenue": data.get('monthly_revenue', 0),
                "profit": data.get('monthly_profit', 0),
                "clients": data.get('new_clients_month', 0),
                "efficiency": self._calculate_operational_efficiency(data)
            },
            "benchmarks": self._get_industry_benchmarks(period)
        }
    
    # =========================
    # MÉTHODES UTILITAIRES
    # =========================
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calcule le taux de croissance"""
        if len(values) < 2:
            return 0
        return ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
    
    def _identify_sales_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identifie les patterns de vente"""
        if df.empty:
            return {}
        
        patterns = {}
        
        # Pattern hebdomadaire
        if 'period' in df.columns and len(df) >= 7:
            df['day_of_week'] = pd.to_datetime(df['period']).dt.dayofweek
            weekly_pattern = df.groupby('day_of_week')['amount'].mean()
            patterns['weekly'] = weekly_pattern.to_dict()
        
        # Tendances
        df['trend'] = df['amount'].rolling(window=7, min_periods=1).mean()
        patterns['trend'] = df['trend'].tolist()[-30:]  # Derniers 30 jours
        
        return patterns
    
    def _generate_sales_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Génère des recommandations basées sur les ventes"""
        recommendations = []
        
        if df.empty:
            return ["Pas assez de données pour des recommandations"]
        
        # Vérifier les jours faibles
        avg_sales = df['sales_count'].mean()
        low_days = df[df['sales_count'] < avg_sales * 0.7]
        
        if len(low_days) > len(df) * 0.3:  # Plus de 30% des jours sont faibles
            recommendations.append("Considérer des promotions pour stimuler les ventes les jours faibles")
        
        # Vérifier la variance
        sales_std = df['amount'].std()
        sales_mean = df['amount'].mean()
        
        if sales_std > sales_mean * 0.5:  # Forte variance
            recommendations.append("Les ventes sont très variables - explorer la cause")
        
        return recommendations
    
    def _identify_product_opportunities(self, df: pd.DataFrame) -> List[Dict]:
        """Identifie les opportunités produits"""
        opportunities = []
        
        if df.empty:
            return opportunities
        
        # Produits avec marge élevée mais faible volume
        high_margin = df[df['margin_percentage'] > df['margin_percentage'].quantile(0.75)]
        low_volume = high_margin[high_margin['total_sold'] < df['total_sold'].median()]
        
        for _, product in low_volume.iterrows():
            opportunities.append({
                "type": "HIGH_MARGIN_LOW_VOLUME",
                "product_id": product.get('id'),
                "name": product.get('name'),
                "margin": product.get('margin_percentage'),
                "volume": product.get('total_sold'),
                "recommendation": "Augmenter la visibilité et le marketing"
            })
        
        # Produits avec volume élevé mais marge faible
        high_volume = df[df['total_sold'] > df['total_sold'].quantile(0.75)]
        low_margin = high_volume[high_volume['margin_percentage'] < df['margin_percentage'].median()]
        
        for _, product in low_margin.iterrows():
            opportunities.append({
                "type": "HIGH_VOLUME_LOW_MARGIN",
                "product_id": product.get('id'),
                "name": product.get('name'),
                "margin": product.get('margin_percentage'),
                "volume": product.get('total_sold'),
                "recommendation": "Revoir la stratégie de prix"
            })
        
        return opportunities
    
    def _estimate_client_lifetime_value(self, data: Dict) -> float:
        """Estime la valeur du cycle de vie client"""
        avg_ticket = data.get('avg_ticket', 0)
        purchase_frequency = (data.get('conversion_rate', 0) / 100) if data.get('conversion_rate') else 0.5
        client_lifespan = 12  # Estimation en mois
        
        return avg_ticket * purchase_frequency * client_lifespan
    
    def _calculate_retention_rate(self, data: Dict) -> float:
        """Calcule le taux de rétention"""
        total_clients = data.get('total_clients', 0)
        active_clients = data.get('vip_clients', 0) + data.get('new_clients_month', 0)
        
        if total_clients == 0:
            return 0
        
        return (active_clients / total_clients) * 100
    
    def _estimate_churn_rate(self, data: Dict) -> float:
        """Estime le taux de perte de clients"""
        return max(0, 100 - self._calculate_retention_rate(data))
    
    def _calculate_inventory_value(self, df: pd.DataFrame) -> float:
        """Calcule la valeur du stock"""
        if 'purchase_price' in df.columns and 'current_stock' in df.columns:
            return (df['purchase_price'] * df['current_stock']).sum()
        return 0
    
    def _calculate_turnover_rate(self, df: pd.DataFrame) -> float:
        """Calcule le taux de rotation des stocks"""
        if 'total_sold' in df.columns and 'current_stock' in df.columns:
            total_sold = df['total_sold'].sum()
            avg_stock = df['current_stock'].mean()
            return total_sold / avg_stock if avg_stock > 0 else 0
        return 0
    
    def _calculate_inventory_health_score(self, out_of_stock: int, low_stock: int, total_products: int) -> float:
        """Calcule un score de santé des stocks"""
        if total_products == 0:
            return 0
        
        out_of_stock_penalty = (out_of_stock / total_products) * 50
        low_stock_penalty = (low_stock / total_products) * 25
        
        return max(0, 100 - out_of_stock_penalty - low_stock_penalty)
    
    def _get_inventory_status(self, score: float) -> str:
        """Détermine le statut des stocks"""
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "FAIR"
        else:
            return "POOR"
    
    def _calculate_stock_coverage(self, df: pd.DataFrame) -> int:
        """Calcule la couverture de stock en jours"""
        avg_daily_sales = 10  # Valeur par défaut, à adapter
        if 'current_stock' in df.columns and avg_daily_sales > 0:
            total_stock = df['current_stock'].sum()
            return int(total_stock / avg_daily_sales)
        return 0
    
    def _generate_inventory_recommendations(self, alerts: Dict, df: pd.DataFrame) -> List[str]:
        """Génère des recommandations pour les stocks"""
        recommendations = []
        
        out_of_stock = alerts.get('out_of_stock', [])
        low_stock = alerts.get('low_stock', [])
        
        if out_of_stock:
            recommendations.append(f"Commander d'urgence {len(out_of_stock)} produits en rupture")
        
        if low_stock:
            recommendations.append(f"Revoir les niveaux de stock pour {len(low_stock)} produits")
        
        # Vérifier les produits qui ne se vendent pas
        if 'total_sold' in df.columns and 'current_stock' in df.columns:
            slow_movers = df[(df['total_sold'] == 0) & (df['current_stock'] > 0)]
            if len(slow_movers) > 5:
                recommendations.append(f"Considérer des promotions pour {len(slow_movers)} produits qui ne se vendent pas")
        
        return recommendations
    
    def _get_profit_benchmarks(self, data: Dict) -> Dict:
        """Retourne des benchmarks pour le profit"""
        industry_avg = {
            "gross_margin": 50.0,  # Moyenne secteur beauté
            "net_margin": 15.0,
            "expense_ratio": 35.0
        }
        
        actual = {
            "gross_margin": (data.get('gross_profit', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0,
            "net_margin": (data.get('net_profit', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0,
            "expense_ratio": (data.get('total_expenses', 0) / data.get('total_revenue', 1)) * 100 if data.get('total_revenue') else 0
        }
        
        return {
            "industry_avg": industry_avg,
            "actual": actual,
            "vs_industry": {k: actual.get(k, 0) - industry_avg.get(k, 0) for k in industry_avg}
        }
    
    def _analyze_profit_trends(self, data: Dict) -> Dict:
        """Analyse les tendances de profit"""
        return {
            "profitability": "HIGH" if data.get('net_margin', 0) > 20 else "MEDIUM" if data.get('net_margin', 0) > 10 else "LOW",
            "efficiency": "HIGH" if data.get('gross_margin', 0) > 60 else "MEDIUM" if data.get('gross_margin', 0) > 40 else "LOW",
            "trend": "IMPROVING" if data.get('net_margin', 0) > 0 else "STABLE" if data.get('net_margin', 0) == 0 else "DECLINING"
        }
    
    def _estimate_cac(self, data: Dict) -> float:
        """Estime le coût d'acquisition client"""
        marketing_cost = data.get('monthly_expenses', 0) * 0.3  # Estimation: 30% des dépenses sont marketing
        new_clients = data.get('new_clients_month', 1)
        
        return marketing_cost / new_clients if new_clients > 0 else 0
    
    def _estimate_clv(self, data: Dict) -> float:
        """Estime la valeur du cycle de vie client"""
        avg_ticket = data.get('avg_ticket', 0)
        purchase_frequency = 1.5  # Estimation
        lifespan = 24  # Estimation en mois
        
        return avg_ticket * purchase_frequency * lifespan
    
    def _calculate_operational_efficiency(self, data: Dict) -> float:
        """Calcule l'efficacité opérationnelle"""
        revenue = data.get('monthly_revenue', 0)
        expenses = data.get('monthly_expenses', 0)
        
        if revenue == 0:
            return 0
        
        return (revenue - expenses) / revenue * 100
    
    def _get_industry_benchmarks(self, period: str) -> Dict:
        """Retourne les benchmarks de l'industrie"""
        benchmarks = {
            "day": {"sales": 10, "revenue": 5000, "profit_margin": 15},
            "week": {"sales": 70, "revenue": 35000, "profit_margin": 15},
            "month": {"sales": 300, "revenue": 150000, "profit_margin": 15},
            "quarter": {"sales": 900, "revenue": 450000, "profit_margin": 15}
        }
        
        return benchmarks.get(period, benchmarks["month"])
    
    def _calculate_sales_forecast(self, sales_data: Dict, forecast_days: int) -> Dict:
        """Calcule une prévision de ventes"""
        if not sales_data.get('data'):
            return {"forecast": [], "accuracy": 0, "confidence_interval": {}}
        
        df = pd.DataFrame(sales_data['data'])
        
        # Méthode simple: moyenne mobile
        forecast = []
        last_values = df['amount'].tail(7).tolist()  # Dernière semaine
        
        for i in range(forecast_days):
            predicted = sum(last_values[-7:]) / min(7, len(last_values)) if last_values else 0
            forecast.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "predicted_amount": predicted,
                "lower_bound": predicted * 0.8,
                "upper_bound": predicted * 1.2
            })
            last_values.append(predicted)
        
        return {
            "forecast": forecast,
            "accuracy": 85,  # Estimation
            "confidence_interval": {"lower": 0.8, "upper": 1.2}
        }
    
    def _get_fallback_stats(self) -> Dict:
        """Retourne des stats de secours"""
        return {
            "total_products": 0,
            "total_clients": 0,
            "total_sales": 0,
            "daily_revenue": 0,
            "monthly_revenue": 0,
            "out_of_stock": 0,
            "low_stock": 0,
            "total_profit": 0,
            "daily_profit": 0,
            "monthly_profit": 0,
            "pending_appointments": 0
        }
    
    def _get_empty_trend(self) -> Dict:
        """Retourne une structure vide pour les tendances"""
        return {
            "period_summary": {
                "total_revenue": 0,
                "total_profit": 0,
                "avg_daily_sales": 0,
                "growth_rate": 0
            },
            "data": [],
            "patterns": {},
            "recommendations": []
        }
    
    def _get_empty_profit_analysis(self) -> Dict:
        """Retourne une structure vide pour l'analyse de profit"""
        return {
            "total_revenue": 0,
            "total_expenses": 0,
            "cogs": 0,
            "gross_profit": 0,
            "net_profit": 0,
            "gross_margin": 0,
            "net_margin": 0,
            "ratios": {},
            "benchmarks": {},
            "trend_analysis": {}
        }
    
    def create_sales_chart(self, trend_data: Dict, chart_type: str = "line") -> go.Figure:
        """Crée un graphique de ventes"""
        if not trend_data.get('data'):
            return self._create_empty_chart()
        
        df = pd.DataFrame(trend_data['data'])
        
        if chart_type == "line":
            fig = px.line(
                df, 
                x='period', 
                y=['amount', 'profit'],
                title="Tendance des Ventes",
                labels={'value': 'Montant (FCFA)', 'period': 'Période'},
                color_discrete_sequence=[COLORS['primary'], COLORS['success']]
            )
        elif chart_type == "bar":
            fig = px.bar(
                df,
                x='period',
                y='amount',
                title="Ventes par Période",
                labels={'amount': 'Montant (FCFA)', 'period': 'Période'},
                color_discrete_sequence=[COLORS['primary']]
            )
        else:
            fig = px.area(
                df,
                x='period',
                y='amount',
                title="Évolution des Ventes",
                labels={'amount': 'Montant (FCFA)', 'period': 'Période'},
                color_discrete_sequence=[COLORS['primary']]
            )
        
        fig.update_layout(
            template="plotly_white",
            hovermode="x unified",
            showlegend=True,
            height=400
        )
        
        return fig
    
    def create_product_performance_chart(self, products_data: Dict) -> go.Figure:
        """Crée un graphique de performance des produits"""
        if not products_data.get('products'):
            return self._create_empty_chart()
        
        df = pd.DataFrame(products_data['products']).head(10)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Revenu par Produit", "Marge par Produit"),
            vertical_spacing=0.15
        )
        
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['total_revenue'],
                name="Revenu",
                marker_color=COLORS['primary']
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=df['name'],
                y=df['margin_percentage'],
                name="Marge %",
                marker_color=COLORS['secondary']
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            height=600
        )
        
        return fig
    
    def _create_empty_chart(self) -> go.Figure:
        """Crée un graphique vide"""
        fig = go.Figure()
        fig.update_layout(
            title="Aucune donnée disponible",
            xaxis_title="",
            yaxis_title="",
            height=400,
            template="plotly_white"
        )
        return fig


# Instance globale du service
analytics_service = AnalyticsService()