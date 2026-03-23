import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

class ThemeManager:
    """Gestionnaire de thème pour l'application"""
    
    @staticmethod
    def get_color_palette(variant="light"):
        """Retourne la palette de couleurs selon le variant"""
        palettes = {
            "light": {
                "primary": "#FF6B9D",  # Rose chic
                "secondary": "#9B59B6",  # Violet
                "accent": "#FFE4E9",  # Rose très clair
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "text": {
                    "primary": "#2C3E50",
                    "secondary": "#7F8C8D",
                    "disabled": "#BDC3C7",
                    "inverse": "#FFFFFF"
                },
                "status": {
                    "success": "#2ECC71",
                    "warning": "#F1C40F",
                    "error": "#E74C3C",
                    "info": "#3498DB"
                },
                "border": "#E9ECEF",
                "shadow": "rgba(0, 0, 0, 0.08)",
                "hover": "rgba(255, 107, 157, 0.1)"
            },
            "dark": {
                "primary": "#FF6B9D",
                "secondary": "#9B59B6",
                "accent": "#2C3E50",
                "background": "#1A1A2E",
                "surface": "#16213E",
                "text": {
                    "primary": "#E2E8F0",
                    "secondary": "#94A3B8",
                    "disabled": "#64748B",
                    "inverse": "#1A1A2E"
                },
                "status": {
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444",
                    "info": "#3B82F6"
                },
                "border": "#334155",
                "shadow": "rgba(0, 0, 0, 0.3)",
                "hover": "rgba(255, 107, 157, 0.2)"
            }
        }
        return palettes.get(variant, palettes["light"])
    
    @staticmethod
    def get_typography():
        """Configuration de la typographie"""
        return {
            "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "font_sizes": {
                "h1": "2.5rem",
                "h2": "2rem",
                "h3": "1.75rem",
                "h4": "1.5rem",
                "h5": "1.25rem",
                "h6": "1rem",
                "body": "0.9375rem",
                "small": "0.875rem",
                "caption": "0.75rem"
            },
            "font_weights": {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            },
            "line_heights": {
                "tight": 1.25,
                "normal": 1.5,
                "relaxed": 1.75
            }
        }
    
    @staticmethod
    def get_spacing():
        """Configuration des espacements"""
        return {
            "xs": "0.25rem",    # 4px
            "sm": "0.5rem",     # 8px
            "md": "1rem",       # 16px
            "lg": "1.5rem",     # 24px
            "xl": "2rem",       # 32px
            "2xl": "3rem",      # 48px
            "3xl": "4rem",      # 64px
        }
    
    @staticmethod
    def get_border_radius():
        """Configuration des bordures arrondies"""
        return {
            "none": "0",
            "sm": "0.25rem",    # 4px
            "md": "0.5rem",     # 8px
            "lg": "0.75rem",    # 12px
            "xl": "1rem",       # 16px
            "full": "9999px"
        }
    
    @staticmethod
    def get_shadows():
        """Configuration des ombres"""
        return {
            "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
            "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
            "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
            "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"
        }
    
    @staticmethod
    def get_transitions():
        """Configuration des transitions"""
        return {
            "fast": "150ms",
            "normal": "300ms",
            "slow": "500ms"
        }
    
    @staticmethod
    def get_plotly_theme():
        """Configuration du thème Plotly"""
        colors = ThemeManager.get_color_palette()
        
        return {
            "layout": go.Layout(
                paper_bgcolor=colors["background"],
                plot_bgcolor=colors["background"],
                font=dict(
                    family=ThemeManager.get_typography()["font_family"],
                    color=colors["text"]["primary"]
                ),
                title=dict(
                    font=dict(
                        size=18,
                        color=colors["text"]["primary"]
                    ),
                    x=0.5
                ),
                xaxis=dict(
                    gridcolor=colors["border"],
                    zerolinecolor=colors["border"],
                    linecolor=colors["border"],
                    tickfont=dict(color=colors["text"]["secondary"])
                ),
                yaxis=dict(
                    gridcolor=colors["border"],
                    zerolinecolor=colors["border"],
                    linecolor=colors["border"],
                    tickfont=dict(color=colors["text"]["secondary"])
                ),
                colorway=[
                    colors["primary"],
                    colors["secondary"],
                    colors["status"]["success"],
                    colors["status"]["warning"],
                    colors["status"]["error"],
                    colors["status"]["info"]
                ],
                hovermode="x unified",
                showlegend=True,
                legend=dict(
                    bgcolor=colors["surface"],
                    bordercolor=colors["border"],
                    borderwidth=1,
                    font=dict(color=colors["text"]["primary"])
                ),
                margin=dict(l=50, r=50, t=50, b=50)
            ),
            "template": "plotly_white"
        }
    
    @staticmethod
    def apply_theme():
        """Applique le thème à l'application"""
        colors = ThemeManager.get_color_palette()
        
        theme_css = f"""
        <style>
        :root {{
            /* Couleurs */
            --color-primary: {colors['primary']};
            --color-secondary: {colors['secondary']};
            --color-accent: {colors['accent']};
            --color-background: {colors['background']};
            --color-surface: {colors['surface']};
            --color-text-primary: {colors['text']['primary']};
            --color-text-secondary: {colors['text']['secondary']};
            --color-text-disabled: {colors['text']['disabled']};
            --color-text-inverse: {colors['text']['inverse']};
            --color-success: {colors['status']['success']};
            --color-warning: {colors['status']['warning']};
            --color-error: {colors['status']['error']};
            --color-info: {colors['status']['info']};
            --color-border: {colors['border']};
            --color-shadow: {colors['shadow']};
            --color-hover: {colors['hover']};
            
            /* Typographie */
            --font-family: {ThemeManager.get_typography()['font_family']};
            --font-size-h1: {ThemeManager.get_typography()['font_sizes']['h1']};
            --font-size-h2: {ThemeManager.get_typography()['font_sizes']['h2']};
            --font-size-h3: {ThemeManager.get_typography()['font_sizes']['h3']};
            --font-size-h4: {ThemeManager.get_typography()['font_sizes']['h4']};
            --font-size-h5: {ThemeManager.get_typography()['font_sizes']['h5']};
            --font-size-h6: {ThemeManager.get_typography()['font_sizes']['h6']};
            --font-size-body: {ThemeManager.get_typography()['font_sizes']['body']};
            --font-size-small: {ThemeManager.get_typography()['font_sizes']['small']};
            --font-size-caption: {ThemeManager.get_typography()['font_sizes']['caption']};
            
            /* Espacements */
            --spacing-xs: {ThemeManager.get_spacing()['xs']};
            --spacing-sm: {ThemeManager.get_spacing()['sm']};
            --spacing-md: {ThemeManager.get_spacing()['md']};
            --spacing-lg: {ThemeManager.get_spacing()['lg']};
            --spacing-xl: {ThemeManager.get_spacing()['xl']};
            --spacing-2xl: {ThemeManager.get_spacing()['2xl']};
            --spacing-3xl: {ThemeManager.get_spacing()['3xl']};
            
            /* Bordures */
            --border-radius-none: {ThemeManager.get_border_radius()['none']};
            --border-radius-sm: {ThemeManager.get_border_radius()['sm']};
            --border-radius-md: {ThemeManager.get_border_radius()['md']};
            --border-radius-lg: {ThemeManager.get_border_radius()['lg']};
            --border-radius-xl: {ThemeManager.get_border_radius()['xl']};
            --border-radius-full: {ThemeManager.get_border_radius()['full']};
            
            /* Ombres */
            --shadow-sm: {ThemeManager.get_shadows()['sm']};
            --shadow-md: {ThemeManager.get_shadows()['md']};
            --shadow-lg: {ThemeManager.get_shadows()['lg']};
            --shadow-xl: {ThemeManager.get_shadows()['xl']};
            --shadow-2xl: {ThemeManager.get_shadows()['2xl']};
            --shadow-inner: {ThemeManager.get_shadows()['inner']};
            
            /* Transitions */
            --transition-fast: {ThemeManager.get_transitions()['fast']};
            --transition-normal: {ThemeManager.get_transitions()['normal']};
            --transition-slow: {ThemeManager.get_transitions()['slow']};
            
            /* Z-index */
            --z-dropdown: 1000;
            --z-sticky: 1020;
            --z-fixed: 1030;
            --z-modal-backdrop: 1040;
            --z-modal: 1050;
            --z-popover: 1060;
            --z-tooltip: 1070;
        }}
        
        /* Application du thème */
        .main {{
            background-color: var(--color-background);
            color: var(--color-text-primary);
            font-family: var(--font-family);
            font-size: var(--font-size-body);
            line-height: 1.5;
        }}
        
        h1 {{
            font-size: var(--font-size-h1);
            font-weight: 600;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-lg);
        }}
        
        h2 {{
            font-size: var(--font-size-h2);
            font-weight: 600;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-md);
        }}
        
        h3 {{
            font-size: var(--font-size-h3);
            font-weight: 600;
            color: var(--color-text-primary);
            margin-bottom: var(--spacing-sm);
        }}
        
        /* Boutons avec variables CSS */
        .stButton > button {{
            background-color: var(--color-primary);
            color: var(--color-text-inverse);
            border: none;
            border-radius: var(--border-radius-md);
            padding: var(--spacing-sm) var(--spacing-xl);
            font-weight: 500;
            transition: all var(--transition-normal);
            box-shadow: var(--shadow-sm);
        }}
        
        .stButton > button:hover {{
            background-color: color-mix(in srgb, var(--color-primary) 90%, black);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        /* Cartes avec variables CSS */
        .custom-card {{
            background: var(--color-surface);
            border-radius: var(--border-radius-lg);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--color-border);
            transition: all var(--transition-normal);
        }}
        
        .custom-card:hover {{
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
            border-color: var(--color-primary);
        }}
        
        /* Alertes avec variables CSS */
        .custom-alert {{
            background: var(--color-accent);
            border-left: 4px solid var(--color-primary);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }}
        
        /* Badges avec variables CSS */
        .badge {{
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--border-radius-full);
            font-size: var(--font-size-small);
            font-weight: 500;
        }}
        
        .badge-primary {{
            background-color: var(--color-primary);
            color: var(--color-text-inverse);
        }}
        
        .badge-success {{
            background-color: var(--color-success);
            color: white;
        }}
        
        .badge-warning {{
            background-color: var(--color-warning);
            color: var(--color-text-primary);
        }}
        
        .badge-danger {{
            background-color: var(--color-error);
            color: white;
        }}
        </style>
        """
        
        st.markdown(theme_css, unsafe_allow_html=True)
    
    @staticmethod
    def create_gradient_background():
        """Crée un fond avec dégradé élégant"""
        gradient_css = """
        <style>
        .gradient-bg {
            background: linear-gradient(135deg, 
                #FF6B9D 0%, 
                #FF8EB4 25%, 
                #FFC1D6 50%, 
                #FFE4E9 75%, 
                #FFFFFF 100%
            );
            min-height: 100vh;
        }
        
        .gradient-card {
            background: linear-gradient(135deg, 
                rgba(255, 107, 157, 0.1) 0%, 
                rgba(255, 142, 180, 0.1) 25%, 
                rgba(255, 193, 214, 0.1) 50%, 
                rgba(255, 228, 233, 0.1) 75%, 
                rgba(255, 255, 255, 0.1) 100%
            );
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .glass-effect {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        </style>
        """
        st.markdown(gradient_css, unsafe_allow_html=True)
    
    @staticmethod
    def get_seasonal_theme():
        """Retourne un thème saisonnier basé sur la date"""
        today = datetime.now()
        month = today.month
        
        seasonal_themes = {
            1: {"primary": "#9B59B6", "name": "Hiver Élégant"},  # Violet hivernal
            2: {"primary": "#FF6B9D", "name": "Saint-Valentin"},  # Rose romantique
            3: {"primary": "#2ECC71", "name": "Printemps Frais"},  # Vert printanier
            4: {"primary": "#FFB347", "name": "Printemps Doré"},  # Orange doré
            5: {"primary": "#3498DB", "name": "Ciel d'Été"},  # Bleu ciel
            6: {"primary": "#FF6B9D", "name": "Été Rose"},  # Rose d'été
            7: {"primary": "#E74C3C", "name": "Été Passionné"},  # Rouge passion
            8: {"primary": "#F1C40F", "name": "Soleil d'Été"},  # Jaune soleil
            9: {"primary": "#D35400", "name": "Automne Chaleureux"},  # Orange automnal
            10: {"primary": "#8B4513", "name": "Automne Profond"},  # Marron
            11: {"primary": "#2C3E50", "name": "Automne Sombre"},  # Gris foncé
            12: {"primary": "#1ABC9C", "name": "Noël Moderne"}  # Turquoise
        }
        
        return seasonal_themes.get(month, {"primary": "#FF6B9D", "name": "Classique"})
    
    @staticmethod
    def create_animated_background():
        """Crée un fond animé élégant"""
        animated_css = """
        <style>
        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-20px);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.7;
            }
        }
        
        @keyframes shimmer {
            0% {
                background-position: -200% center;
            }
            100% {
                background-position: 200% center;
            }
        }
        
        .float-animation {
            animation: float 3s ease-in-out infinite;
        }
        
        .pulse-animation {
            animation: pulse 2s ease-in-out infinite;
        }
        
        .shimmer-text {
            background: linear-gradient(90deg, 
                #FF6B9D 0%, 
                #FF8EB4 25%, 
                #FF6B9D 50%, 
                #FF8EB4 75%, 
                #FF6B9D 100%
            );
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 3s linear infinite;
        }
        
        .hover-grow {
            transition: transform 0.3s ease;
        }
        
        .hover-grow:hover {
            transform: scale(1.05);
        }
        
        .hover-rotate {
            transition: transform 0.3s ease;
        }
        
        .hover-rotate:hover {
            transform: rotate(5deg);
        }
        </style>
        """
        st.markdown(animated_css, unsafe_allow_html=True)