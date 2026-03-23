import streamlit as st
from datetime import datetime
import time

def show_footer():
    """Affiche le pied de page de l'application"""
    
    footer_css = """
    <style>
    .main-footer {
        background: linear-gradient(90deg, 
            #2C3E50 0%, 
            #34495E 50%, 
            #2C3E50 100%
        );
        color: white;
        padding: 2rem;
        margin-top: 3rem;
        border-radius: 20px 20px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .main-footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, 
            #FF6B9D 0%, 
            #9B59B6 50%, 
            #FF6B9D 100%
        );
    }
    
    .footer-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .footer-title {
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #FF6B9D;
    }
    
    .footer-links {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .footer-link {
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .footer-link:hover {
        color: #FF6B9D;
        transform: translateX(5px);
    }
    
    .footer-contact {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .contact-icon {
        font-size: 1.25rem;
        color: #FF6B9D;
    }
    
    .footer-social {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .social-link {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        color: white;
        text-decoration: none;
        transition: all 0.3s;
        font-size: 1.25rem;
    }
    
    .social-link:hover {
        background: #FF6B9D;
        transform: translateY(-3px);
    }
    
    .footer-bottom {
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .copyright {
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.875rem;
    }
    
    .footer-stats {
        display: flex;
        gap: 2rem;
        font-size: 0.875rem;
    }
    
    .stat {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .stat-value {
        font-weight: 600;
        color: #FF6B9D;
    }
    
    .back-to-top {
        position: absolute;
        right: 2rem;
        bottom: 2rem;
        background: #FF6B9D;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        font-size: 1.5rem;
        box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3);
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .back-to-top:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(255, 107, 157, 0.4);
    }
    
    /* Animation de flottement */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .floating {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .footer-content {
            grid-template-columns: 1fr;
        }
        
        .footer-bottom {
            flex-direction: column;
            text-align: center;
        }
        
        .footer-stats {
            justify-content: center;
        }
        
        .back-to-top {
            position: static;
            margin-top: 1rem;
            align-self: center;
        }
    }
    </style>
    """
    
    st.markdown(footer_css, unsafe_allow_html=True)
    
    # Informations dynamiques
    current_year = datetime.now().year
    app_start = st.session_state.get('app_start_time')

    # Sécurité PROD : si invalide, uptime = 0
    if not isinstance(app_start, (int, float)):
        uptime = 0
    else:
        uptime = max(0, time.time() - app_start)

    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    # Footer HTML
    footer_html = f"""
    <div class="main-footer">
        <div class="footer-content">
            <div class="footer-section">
                <div class="footer-title">💄 Luxe Beauté Management</div>
                <p style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                    Système de gestion premium pour instituts de beauté. 
                    Optimisez vos ventes, gérez votre stock et offrez une expérience 
                    exceptionnelle à vos clients.
                </p>
                <div class="footer-social">
                    <a href="#" class="social-link" title="Facebook">📘</a>
                    <a href="#" class="social-link" title="Instagram">📷</a>
                    <a href="#" class="social-link" title="Twitter">🐦</a>
                    <a href="#" class="social-link" title="LinkedIn">💼</a>
                </div>
            </div>
            
            <div class="footer-section">
                <div class="footer-title">🔗 Navigation rapide</div>
                <div class="footer-links">
                    <a href="#" class="footer-link" onclick="changePage('dashboard')">📊 Tableau de bord</a>
                    <a href="#" class="footer-link" onclick="changePage('produits')">💄 Catalogue produits</a>
                    <a href="#" class="footer-link" onclick="changePage('ventes')">💰 Nouvelle vente</a>
                    <a href="#" class="footer-link" onclick="changePage('clients')">👥 Gestion clients</a>
                    <a href="#" class="footer-link" onclick="changePage('rapports')">📈 Rapports avancés</a>
                </div>
            </div>
            
            <div class="footer-section">
                <div class="footer-title">📞 Contact & Support</div>
                <div class="footer-contact">
                    <div class="contact-item">
                        <span class="contact-icon">📧</span>
                        <span>support@luxebeauty.com</span>
                    </div>
                    <div class="contact-item">
                        <span class="contact-icon">📱</span>
                        <span>+225 07 07 07 07 07</span>
                    </div>
                    <div class="contact-item">
                        <span class="contact-icon">🏢</span>
                        <span>Abidjan, Côte d'Ivoire</span>
                    </div>
                    <div class="contact-item">
                        <span class="contact-icon">🕒</span>
                        <span>Lun - Ven: 8h - 18h</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer-bottom">
            <div class="copyright">
                © {current_year} Luxe Beauté Management. Tous droits réservés.<br>
                <small style="opacity: 0.6;">Version 2.0.0 • Système opérationnel depuis {hours}h {minutes}min</small>
            </div>
            
            <div class="footer-stats">
                <div class="stat">
                    <span>👥</span>
                    <span>Clients: <span class="stat-value">1,247</span></span>
                </div>
                <div class="stat">
                    <span>💰</span>
                    <span>Ventes: <span class="stat-value">12.5M</span></span>
                </div>
                <div class="stat">
                    <span>📦</span>
                    <span>Produits: <span class="stat-value">356</span></span>
                </div>
            </div>
        </div>
        
        <a href="#" class="back-to-top floating" onclick="scrollToTop()" title="Retour en haut">
            ⬆️
        </a>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)
    
    # JavaScript pour les interactions
    footer_script = r"""
    <script>
    function changePage(page) {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: page
        }, '*');
    }
    
    function scrollToTop() {
        window.parent.scrollTo({ top: 0, behavior: 'smooth' });
        return false;
    }
    
    // Mettre à jour le temps d'activité
    function updateUptime() {
        const uptimeElement = document.querySelector('.footer-bottom .copyright small');
        if (uptimeElement) {
            const text = uptimeElement.textContent;
            const matches = text.match(/(\d+)h (\d+)min/);
            if (matches) {
                let hours = parseInt(matches[1]);
                let minutes = parseInt(matches[2]);
                minutes++;
                if (minutes >= 60) {
                    hours++;
                    minutes = 0;
                }
                uptimeElement.textContent = text.replace(
                    /(\\d+)h (\\d+)min/, 
                    `${hours}h ${minutes}min`
                );
            }
        }
    }
    
    setInterval(updateUptime, 60000); // Mettre à jour chaque minute
    </script>
    """
    
    st.markdown(footer_script, unsafe_allow_html=True)