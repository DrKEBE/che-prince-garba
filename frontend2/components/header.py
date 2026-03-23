import streamlit as st
from datetime import datetime
from config.constants import COLORS, APP_CONFIG
from config.theme import ThemeManager
import streamlit.components.v1 as components


def show_header():
    # Données utilisateur sécurisées
    user_info = st.session_state.get("user_info", {})
    full_name = user_info.get("full_name") or "Utilisateur"
    avatar_letter = full_name[0].upper()

    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    seasonal_theme = ThemeManager.get_seasonal_theme()

    header_html = f"""
    <html>
    <head>
    <style>
        .main-header {{
            background: linear-gradient(135deg, {seasonal_theme['primary']}, {COLORS['secondary']});
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo-icon {{
            font-size: 2rem;
        }}

        .user-info {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background: rgba(255,255,255,0.15);
            padding: 0.5rem 1rem;
            border-radius: 50px;
        }}

        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: white;
            color: {seasonal_theme['primary']};
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}

        .notification-btn {{
            background: none;
            border: none;
            font-size: 1.4rem;
            cursor: pointer;
            position: relative;
            color: white;
        }}

        .badge {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: red;
            color: white;
            font-size: 0.6rem;
            border-radius: 50%;
            padding: 2px 6px;
        }}
    </style>
    </head>

    <body>
        <div class="main-header">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">💄</div>
                    <div>
                        <strong>{APP_CONFIG['name']}</strong><br>
                        <small>Système de gestion premium</small>
                    </div>
                </div>

                <div style="display:flex;align-items:center;gap:1rem;">
                    <div id="time">{current_time}</div>

                    <button class="notification-btn" onclick="ringBell()">
                        🔔
                        <span class="badge">3</span>
                    </button>

                    <div class="user-info">
                        <div class="avatar">{avatar_letter}</div>
                        <div>
                            <div>{full_name}</div>
                            <small>{user_info.get('role', 'Administrateur')}</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function ringBell() {{
                const btn = document.querySelector('.notification-btn');
                btn.style.transform = "rotate(15deg)";
                setTimeout(() => btn.style.transform = "rotate(0)", 300);
            }}

            setInterval(() => {{
                const now = new Date();
                document.getElementById("time").innerText =
                    now.toLocaleDateString('fr-FR') + " " +
                    now.toLocaleTimeString('fr-FR');
            }}, 1000);
        </script>
    </body>
    </html>
    """

    components.html(header_html, height=180)
