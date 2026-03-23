import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
import streamlit as st

from config.theme import ThemeManager

class ChartManager:
    """Gestionnaire de graphiques pour l'application"""
    
    @staticmethod
    def create_sales_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
        """Crée un graphique de ventes élégant"""
        theme = ThemeManager.get_plotly_theme()
        
        fig = go.Figure()
        
        # Ligne principale
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='lines+markers',
            name='Ventes',
            line=dict(
                color=ThemeManager.get_color_palette()['primary'],
                width=3,
                shape='spline',
                smoothing=0.5
            ),
            marker=dict(
                size=8,
                color=ThemeManager.get_color_palette()['primary'],
                line=dict(width=2, color='white')
            ),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 157, 0.1)',
            hovertemplate='<b>%{x}</b><br>CA: %{y:,.0f} FCFA<extra></extra>'
        ))
        
        # Mise en forme
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color=theme['layout'].font.color),
                x=0.5
            ),
            xaxis=dict(
                title="Date",
                gridcolor=theme['layout'].xaxis.gridcolor,
                showline=True,
                linewidth=1,
                linecolor=theme['layout'].xaxis.linecolor,
                tickangle=45
            ),
            yaxis=dict(
                title="Chiffre d'affaires (FCFA)",
                gridcolor=theme['layout'].yaxis.gridcolor,
                showline=True,
                linewidth=1,
                linecolor=theme['layout'].yaxis.linecolor,
                tickformat=',.0f'
            ),
            hovermode='x unified',
            plot_bgcolor=theme['layout'].plot_bgcolor,
            paper_bgcolor=theme['layout'].paper_bgcolor,
            font=theme['layout'].font,
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=False
        )
        
        # Ajouter une annotation pour le pic
        if not data.empty:
            max_value = data[y_col].max()
            max_date = data.loc[data[y_col] == max_value, x_col].iloc[0]
            
            fig.add_annotation(
                x=max_date,
                y=max_value,
                text=f"Pic: {max_value:,.0f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=ThemeManager.get_color_palette()['status']['warning'],
                bgcolor="white",
                bordercolor=ThemeManager.get_color_palette()['status']['warning'],
                borderwidth=1,
                font=dict(size=10, color=ThemeManager.get_color_palette()['text']['primary'])
            )
        
        return fig
    
    @staticmethod
    def create_product_performance_chart(products_data: List[Dict]) -> go.Figure:
        """Crée un graphique de performance produit"""
        theme = ThemeManager.get_plotly_theme()
        
        df = pd.DataFrame(products_data)
        
        # Créer un graphique à bulles
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['total_sold'],
            y=df['total_revenue'],
            mode='markers',
            marker=dict(
                size=df['margin_percentage'] * 2,
                color=df['margin_percentage'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Marge %"),
                line=dict(width=2, color='white')
            ),
            text=df['name'],
            hovertemplate='<b>%{text}</b><br>'
                        'Vendus: %{x}<br>'
                        'CA: %{y:,.0f} FCFA<br>'
                        'Marge: %{marker.color:.1f}%<extra></extra>',
            name='Produits'
        ))
        
        fig.update_layout(
            title=dict(
                text="Performance des produits",
                font=dict(size=18, color=theme['layout'].font.color),
                x=0.5
            ),
            xaxis=dict(
                title="Quantité vendue",
                gridcolor=theme['layout'].xaxis.gridcolor
            ),
            yaxis=dict(
                title="Chiffre d'affaires (FCFA)",
                gridcolor=theme['layout'].yaxis.gridcolor,
                tickformat=',.0f'
            ),
            hovermode='closest',
            plot_bgcolor=theme['layout'].plot_bgcolor,
            paper_bgcolor=theme['layout'].paper_bgcolor,
            font=theme['layout'].font,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    @staticmethod
    def create_stock_distribution_chart(stock_data: List[Dict]) -> go.Figure:
        """Crée un graphique de distribution du stock"""
        theme = ThemeManager.get_plotly_theme()
        
        df = pd.DataFrame(stock_data)
        
        # Catégoriser les produits
        conditions = [
            df['current_stock'] <= 0,
            df['current_stock'] <= df['alert_threshold'],
            df['current_stock'] > df['alert_threshold']
        ]
        choices = ['Rupture', 'Faible', 'Normal']
        df['status'] = pd.Series(np.select(conditions, choices, default='Normal'))
        
        # Compter par statut
        status_counts = df['status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=.4,
            marker=dict(
                colors=['#E74C3C', '#F1C40F', '#2ECC71'],
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>%{label}</b><br>%{value} produits<br>%{percent}<extra></extra>',
            textinfo='label+percent',
            textposition='inside'
        )])
        
        fig.update_layout(
            title=dict(
                text="Distribution du stock",
                font=dict(size=18, color=theme['layout'].font.color),
                x=0.5
            ),
            showlegend=False,
            plot_bgcolor=theme['layout'].plot_bgcolor,
            paper_bgcolor=theme['layout'].paper_bgcolor,
            font=theme['layout'].font,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(actual: List[float], target: List[float], labels: List[str], title: str = "") -> go.Figure:
        """Crée un graphique de comparaison objectif/réel"""
        theme = ThemeManager.get_plotly_theme()
        
        fig = go.Figure()
        
        # Barres objectif (légèrement transparentes)
        fig.add_trace(go.Bar(
            name='Objectif',
            x=labels,
            y=target,
            marker_color='rgba(155, 89, 182, 0.6)',
            hovertemplate='<b>%{x}</b><br>Objectif: %{y:,.0f} FCFA<extra></extra>'
        ))
        
        # Barres réel (pleines)
        fig.add_trace(go.Bar(
            name='Réel',
            x=labels,
            y=actual,
            marker_color=ThemeManager.get_color_palette()['primary'],
            hovertemplate='<b>%{x}</b><br>Réel: %{y:,.0f} FCFA<extra></extra>'
        ))
        
        # Calculer les différences
        differences = [a - t for a, t in zip(actual, target)]
        
        # Ajouter des annotations pour les différences
        for i, (label, diff) in enumerate(zip(labels, differences)):
            color = '#2ECC71' if diff >= 0 else '#E74C3C'
            symbol = '+' if diff >= 0 else ''
            
            fig.add_annotation(
                x=label,
                y=max(actual[i], target[i]) + max(actual + target) * 0.05,
                text=f'{symbol}{diff:,.0f}',
                showarrow=False,
                font=dict(size=10, color=color, weight='bold'),
                bgcolor='white',
                bordercolor=color,
                borderwidth=1,
                borderpad=2
            )
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color=theme['layout'].font.color),
                x=0.5
            ),
            barmode='group',
            xaxis=dict(
                title="Période",
                gridcolor=theme['layout'].xaxis.gridcolor,
                tickangle=45
            ),
            yaxis=dict(
                title="Montant (FCFA)",
                gridcolor=theme['layout'].yaxis.gridcolor,
                tickformat=',.0f'
            ),
            hovermode='x unified',
            plot_bgcolor=theme['layout'].plot_bgcolor,
            paper_bgcolor=theme['layout'].paper_bgcolor,
            font=theme['layout'].font,
            margin=dict(l=50, r=50, t=80, b=50),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig

# Fonctions de compatibilité
def create_line_chart(data: pd.DataFrame, x: str, y: str, title: str = "", color: str = None) -> go.Figure:
    """Crée un graphique linéaire simple"""
    return ChartManager.create_sales_chart(data, x, y, title)

def create_bar_chart(data: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    """Crée un graphique à barres"""
    theme = ThemeManager.get_plotly_theme()
    
    fig = px.bar(
        data, 
        x=x, 
        y=y,
        title=title,
        color_discrete_sequence=[ThemeManager.get_color_palette()['primary']]
    )
    
    fig.update_layout(
        plot_bgcolor=theme['layout'].plot_bgcolor,
        paper_bgcolor=theme['layout'].paper_bgcolor,
        font=theme['layout'].font
    )
    
    return fig

def create_pie_chart(data: Dict, title: str = "", colors: List[str] = None) -> go.Figure:
    """Crée un graphique en secteur"""
    if colors is None:
        colors = ['#FF6B9D', '#9B59B6', '#3498DB', '#2ECC71', '#F1C40F']
    
    theme = ThemeManager.get_plotly_theme()
    
    fig = go.Figure(data=[go.Pie(
        labels=list(data.keys()),
        values=list(data.values()),
        hole=.3,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='inside'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color=theme['layout'].font.color),
            x=0.5
        ),
        showlegend=False,
        plot_bgcolor=theme['layout'].plot_bgcolor,
        paper_bgcolor=theme['layout'].paper_bgcolor,
        font=theme['layout'].font
    )
    
    return fig