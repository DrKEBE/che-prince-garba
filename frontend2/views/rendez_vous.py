import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

from config.style import create_header, COLORS, create_metric_card

API_BASE_URL = "http://localhost:8000/api/v1"

def show_appointments():
    """Interface de gestion des rendez-vous premium"""
    
    st.markdown(create_header("📅 Rendez-vous & Planning", 
                             "Gestion exclusive de votre agenda beauté", "💆‍♀️"), 
                unsafe_allow_html=True)
    
    # =============================
    # KPI RENDEZ-VOUS
    # =============================
    try:
        # Récupérer les stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Aujourd'hui
            today = datetime.now().date()
            today_appointments = 8
            st.markdown(create_metric_card(
                "Aujourd'hui",
                f"{today_appointments} RDV",
                icon="📅"
            ), unsafe_allow_html=True)
        
        with col2:
            # Cette semaine
            week_appointments = 42
            st.markdown(create_metric_card(
                "Cette semaine",
                f"{week_appointments} RDV",
                change=12,
                icon="📆"
            ), unsafe_allow_html=True)
        
        with col3:
            # Taux de remplissage
            capacity = 85
            occupied = 68
            fill_rate = (occupied / capacity * 100) if capacity > 0 else 0
            st.markdown(create_metric_card(
                "Taux remplissage",
                f"{fill_rate:.1f}%",
                change=5.2,
                icon="📊"
            ), unsafe_allow_html=True)
        
        with col4:
            # Annulations
            cancellations = 3
            st.markdown(create_metric_card(
                "Annulations",
                f"{cancellations}",
                change=-15,
                icon="⚠️"
            ), unsafe_allow_html=True)
    except:
        pass
    
    # =============================
    # TABS GESTION RDV
    # =============================
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗓️ Calendrier", 
        "✨ Nouveau RDV", 
        "👥 Équipe", 
        "📊 Analytics"
    ])
    
    with tab1:
        show_appointment_calendar()
    
    with tab2:
        show_new_appointment()
    
    with tab3:
        show_team_management()
    
    with tab4:
        show_appointment_analytics()

def show_appointment_calendar():
    """Calendrier interactif des rendez-vous"""
    st.markdown("""
    <div class="luxe-card">
        <h3 style="color: #d4af37; margin-bottom: 20px;">🗓️ Calendrier des Rendez-vous</h3>
    """, unsafe_allow_html=True)
    
    # Sélection de la vue
    view_option = st.radio(
        "Vue",
        ["Jour", "Semaine", "Mois"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # Navigation calendrier
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 2, 1, 1])
    
    with col_nav1:
        if st.button("◀️ Précédent"):
            st.session_state.calendar_offset = st.session_state.get('calendar_offset', 0) - 1
            st.rerun()
    
    with col_nav2:
        current_date = datetime.now() + timedelta(days=st.session_state.get('calendar_offset', 0))
        
        if view_option == "Jour":
            date_display = current_date.strftime("%A %d %B %Y")
        elif view_option == "Semaine":
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=6)
            date_display = f"Semaine {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}"
        else:
            date_display = current_date.strftime("%B %Y")
        
        st.markdown(f"<h4 style='text-align: center; color: #d4af37;'>{date_display}</h4>", unsafe_allow_html=True)
    
    with col_nav3:
        if st.button("Suivant ▶️"):
            st.session_state.calendar_offset = st.session_state.get('calendar_offset', 0) + 1
            st.rerun()
    
    with col_nav4:
        if st.button("Aujourd'hui"):
            st.session_state.calendar_offset = 0
            st.rerun()
    
    # Vue calendrier selon l'option
    if view_option == "Jour":
        show_day_view(current_date)
    elif view_option == "Semaine":
        show_week_view(current_date)
    else:
        show_month_view(current_date)
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_day_view(date):
    """Vue journalière"""
    st.markdown(f"### 📅 Planning du {date.strftime('%A %d %B %Y')}")
    
    # Créer les créneaux horaires
    time_slots = []
    for hour in range(9, 19):  # 9h à 18h
        for minute in [0, 30]:  # Créneaux de 30 minutes
            time_slots.append(f"{hour:02d}:{minute:02d}")
    
    # Données de démonstration
    appointments = [
        {"time": "09:00", "client": "Sophie Martin", "service": "Soin Visage Premium", "employee": "Marie", "duration": 60},
        {"time": "10:30", "client": "Emma Dubois", "service": "Massage Relaxant", "employee": "Julie", "duration": 90},
        {"time": "14:00", "client": "Camille Laurent", "service": "Épilation Laser", "employee": "Sophie", "duration": 45},
        {"time": "16:00", "client": "Julie Bernard", "service": "Manucure VIP", "employee": "Marie", "duration": 60},
    ]
    
    # Créer une grille
    for slot in time_slots:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.markdown(f"**{slot}**")
        
        with col2:
            # Vérifier si un RDV existe à cette heure
            appointment = next((a for a in appointments if a['time'] == slot), None)
            
            if appointment:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(184, 148, 31, 0.2));
                    padding: 10px;
                    border-radius: 8px;
                    border-left: 4px solid {COLORS['secondary']};
                    margin-bottom: 5px;
                ">
                    <div style="font-weight: 600; color: #d4af37;">{appointment['client']}</div>
                    <div style="color: #7f8c8d; font-size: 12px;">{appointment['service']}</div>
                    <div style="color: #fff; font-size: 11px; margin-top: 5px;">
                        👩‍⚕️ {appointment['employee']} • ⏱️ {appointment['duration']} min
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    padding: 10px;
                    border-radius: 8px;
                    color: #7f8c8d;
                    font-size: 14px;
                    text-align: center;
                ">
                    Disponible
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if appointment:
                col_action1, col_action2 = st.columns(2)
                with col_action1:
                    if st.button("✏️", key=f"edit_{slot}", help="Modifier"):
                        st.session_state.edit_appointment = appointment
                with col_action2:
                    if st.button("❌", key=f"cancel_{slot}", help="Annuler"):
                        st.warning(f"Annuler le RDV avec {appointment['client']} ?")
            else:
                if st.button("➕", key=f"add_{slot}", use_container_width=True):
                    st.session_state.new_appointment_time = slot

def show_week_view(date):
    """Vue hebdomadaire"""
    # Calculer le début de la semaine
    week_start = date - timedelta(days=date.weekday())
    
    # Créer un tableau hebdomadaire
    days = []
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        days.append({
            "date": day_date,
            "day_name": day_date.strftime("%a"),
            "day_number": day_date.day
        })
    
    # Afficher l'en-tête
    cols = st.columns(7)
    for idx, col in enumerate(cols):
        with col:
            day = days[idx]
            is_today = day["date"].date() == datetime.now().date()
            
            day_style = f"""
            <div style="
                background: {'rgba(212, 175, 55, 0.2)' if is_today else 'rgba(255, 255, 255, 0.05)'};
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                border: {'2px solid #d4af37' if is_today else '1px solid rgba(255, 255, 255, 0.1)'};
                margin-bottom: 10px;
            ">
                <div style="font-size: 12px; color: #7f8c8d;">{day['day_name']}</div>
                <div style="font-size: 24px; font-weight: 600; color: #fff;">{day['day_number']}</div>
            </div>
            """
            st.markdown(day_style, unsafe_allow_html=True)
    
    # Afficher les créneaux
    time_slots = ["09:00", "11:00", "14:00", "16:00"]
    
    for slot in time_slots:
        st.markdown(f"#### {slot}")
        cols = st.columns(7)
        
        for idx, col in enumerate(cols):
            with col:
                # Simuler quelques RDV
                if idx % 3 == 0:  # Un RDV sur 3 pour l'exemple
                    st.markdown(f"""
                    <div style="
                        background: rgba(52, 152, 219, 0.2);
                        padding: 8px;
                        border-radius: 6px;
                        border-left: 3px solid #3498db;
                        margin-bottom: 5px;
                    ">
                        <div style="font-size: 12px; color: #fff;">M. Dupont</div>
                        <div style="font-size: 10px; color: #7f8c8d;">Soin visage</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.03);
                        padding: 8px;
                        border-radius: 6px;
                        text-align: center;
                        color: #7f8c8d;
                        font-size: 12px;
                    ">
                        Libre
                    </div>
                    """, unsafe_allow_html=True)

def show_month_view(date):
    """Vue mensuelle"""
    # Générer le calendrier du mois
    cal = calendar.monthcalendar(date.year, date.month)
    
    # En-têtes des jours
    day_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    cols = st.columns(7)
    
    for idx, col in enumerate(cols):
        with col:
            st.markdown(f"<div style='text-align: center; color: #d4af37; font-weight: 600;'>{day_names[idx]}</div>", 
                       unsafe_allow_html=True)
    
    # Jours du mois
    for week in cal:
        cols = st.columns(7)
        for idx, col in enumerate(cols):
            with col:
                day = week[idx]
                if day != 0:
                    # Vérifier si c'est aujourd'hui
                    is_today = (date.year == datetime.now().year and 
                               date.month == datetime.now().month and 
                               day == datetime.now().day)
                    
                    # Simuler le nombre de RDV
                    appointment_count = day % 4  # Pour l'exemple
                    
                    day_style = f"""
                    <div style="
                        background: {'rgba(212, 175, 55, 0.2)' if is_today else 'rgba(255, 255, 255, 0.05)'};
                        border: {'2px solid #d4af37' if is_today else '1px solid rgba(255, 255, 255, 0.1)'};
                        border-radius: 8px;
                        padding: 8px;
                        text-align: center;
                        margin-bottom: 5px;
                        min-height: 60px;
                    ">
                        <div style="
                            font-size: 16px;
                            font-weight: 600;
                            color: {'#d4af37' if is_today else '#fff'};
                        ">
                            {day}
                        </div>
                    """
                    
                    if appointment_count > 0:
                        day_style += f"""
                        <div style="
                            font-size: 11px;
                            color: #2ecc71;
                            margin-top: 5px;
                        ">
                            📅 {appointment_count} RDV
                        </div>
                        """
                    
                    day_style += "</div>"
                    
                    st.markdown(day_style, unsafe_allow_html=True)

def show_new_appointment():
    """Formulaire de création de rendez-vous"""
    st.markdown("""
    <div class="luxe-card">
        <h3 style="color: #d4af37; margin-bottom: 20px;">✨ Nouveau Rendez-vous</h3>
        <p style="color: #7f8c8d; margin-bottom: 30px;">
            Planifiez un nouveau rendez-vous pour un client
        </p>
    """, unsafe_allow_html=True)
    
    with st.form("new_appointment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Informations Client")
            
            # Sélection client
            try:
                clients_response = requests.get(f"{API_BASE_URL}/clients")
                if clients_response.status_code == 200:
                    clients = clients_response.json()
                    client_options = {c['id']: f"{c['full_name']} ({c['phone']})" for c in clients}
                    
                    client_id = st.selectbox(
                        "Client *",
                        options=[""] + list(client_options.keys()),
                        format_func=lambda x: "Sélectionnez un client" if x == "" else client_options[x]
                    )
                else:
                    st.error("Impossible de charger les clients")
                    client_id = ""
            except:
                st.error("Erreur de connexion")
                client_id = ""
            
            # Nouveau client option
            new_client = st.checkbox("Créer un nouveau client")
            
            if new_client:
                new_client_name = st.text_input("Nom du nouveau client")
                new_client_phone = st.text_input("Téléphone")
        
        with col2:
            st.markdown("#### 💆‍♀️ Détails du Service")
            
            # Services disponibles
            services = [
                "Soin Visage Premium",
                "Massage Relaxant",
                "Épilation Laser",
                "Manucure VIP",
                "Pédicure Luxe",
                "Maquillage Professionnel",
                "Extension Cils",
                "Bronzage Spray"
            ]
            
            service_type = st.selectbox("Service *", services)
            
            # Durée
            duration = st.selectbox("Durée", [30, 45, 60, 90, 120], format_func=lambda x: f"{x} minutes")
            
            # Esthéticienne
            employees = ["Marie", "Sophie", "Julie", "Emma", "Camille"]
            employee_id = st.selectbox("Esthéticienne *", employees)
        
        st.markdown("---")
        st.markdown("#### 📅 Date & Heure")
        
        col_date1, col_date2, col_date3 = st.columns(3)
        
        with col_date1:
            appointment_date = st.date_input("Date *", datetime.now())
        
        with col_date2:
            available_slots = [
                "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
            ]
            appointment_time = st.selectbox("Heure *", available_slots)
        
        with col_date3:
            # Vérification disponibilité
            st.markdown("#### 📋 Disponibilité")
            if st.button("🔍 Vérifier", use_container_width=True):
                st.info("Disponible ✓")
        
        st.markdown("---")
        st.markdown("#### 💰 Tarification")
        
        col_price1, col_price2 = st.columns(2)
        
        with col_price1:
            price = st.number_input("Prix (€) *", min_value=0.0, value=80.0, step=5.0, format="%.2f")
        
        with col_price2:
            paid_amount = st.number_input("Montant payé", min_value=0.0, value=0.0, step=5.0, format="%.2f")
        
        # Notes
        notes = st.text_area("Notes", placeholder="Informations supplémentaires, allergies, préférences...")
        
        # Options
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            send_reminder = st.checkbox("Envoyer rappel SMS", value=True)
            send_confirmation = st.checkbox("Envoyer confirmation", value=True)
        
        with col_opt2:
            requires_deposit = st.checkbox("Acompte requis")
            is_recurring = st.checkbox("Rendez-vous récurrent")
        
        # Boutons
        col_submit, col_cancel = st.columns([2, 1])
        
        with col_submit:
            submitted = st.form_submit_button("✨ Créer le Rendez-vous", type="primary", use_container_width=True)
        
        with col_cancel:
            if st.form_submit_button("🗑️ Annuler", use_container_width=True):
                st.rerun()
        
        if submitted:
            # Validation
            errors = []
            
            if not client_id and not new_client:
                errors.append("Veuillez sélectionner un client ou créer un nouveau client")
            
            if new_client and (not new_client_name or not new_client_phone):
                errors.append("Pour un nouveau client, le nom et le téléphone sont obligatoires")
            
            if not service_type or not employee_id or not appointment_date or not appointment_time:
                errors.append("Tous les champs obligatoires (*) doivent être remplis")
            
            if price <= 0:
                errors.append("Le prix doit être supérieur à 0")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                with st.spinner("Création du rendez-vous..."):
                    # Préparer les données
                    appointment_data = {
                        "client_id": client_id if not new_client else None,
                        "employee_id": employee_id,
                        "service_type": service_type,
                        "appointment_date": f"{appointment_date.isoformat()}T{appointment_time}:00",
                        "duration": duration,
                        "total_amount": price,
                        "paid_amount": paid_amount,
                        "notes": notes if notes else None
                    }
                    
                    # Envoyer à l'API
                    try:
                        response = requests.post(f"{API_BASE_URL}/appointments", json=appointment_data)
                        
                        if response.status_code == 201:
                            st.success("🎉 Rendez-vous créé avec succès !")
                            
                            # Confirmation visuelle
                            st.markdown("""
                            <script>
                            // Animation de confirmation
                            const confetti = () => {
                                const emojis = ['💆‍♀️', '💅', '✨', '🌟', '💎'];
                                for(let i = 0; i < 30; i++) {
                                    const confetti = document.createElement('div');
                                    confetti.style.cssText = `
                                        position: fixed;
                                        font-size: 24px;
                                        animation: confetti-fall ${1 + Math.random() * 2}s linear forwards;
                                        left: ${Math.random() * 100}vw;
                                        z-index: 9999;
                                    `;
                                    confetti.textContent = emojis[Math.floor(Math.random() * emojis.length)];
                                    document.body.appendChild(confetti);
                                    setTimeout(() => confetti.remove(), 3000);
                                }
                            }
                            confetti();
                            </script>
                            <style>
                            @keyframes confetti-fall {
                                0% { transform: translateY(-100px) rotate(0deg); opacity: 1; }
                                100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            # Réinitialiser le formulaire
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ Erreur {response.status_code}: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_team_management():
    """Gestion de l'équipe esthéticiennes"""
    st.markdown("""
    <div class="luxe-card">
        <h3 style="color: #d4af37; margin-bottom: 20px;">👥 Gestion de l'Équipe</h3>
        <p style="color: #7f8c8d; margin-bottom: 30px;">
            Gérez votre équipe d'esthéticiennes et leurs plannings
        </p>
    """, unsafe_allow_html=True)
    
    # Liste des esthéticiennes
    st.markdown("### 💁‍♀️ Esthéticiennes")
    
    employees = [
        {
            "id": 1,
            "name": "Marie Dubois",
            "role": "Esthéticienne Senior",
            "specialties": ["Soins Visage", "Massage"],
            "rating": 4.9,
            "clients": 42,
            "status": "🟢 Disponible"
        },
        {
            "id": 2,
            "name": "Sophie Martin",
            "role": "Maquilleuse Pro",
            "specialties": ["Maquillage", "Extension Cils"],
            "rating": 4.8,
            "clients": 38,
            "status": "🟡 En pause"
        },
        {
            "id": 3,
            "name": "Julie Bernard",
            "role": "Esthéticienne",
            "specialties": ["Manucure", "Pédicure"],
            "rating": 4.7,
            "clients": 35,
            "status": "🟢 Disponible"
        },
        {
            "id": 4,
            "name": "Emma Laurent",
            "role": "Épilatrice",
            "specialties": ["Épilation Laser", "Cire"],
            "rating": 4.9,
            "clients": 28,
            "status": "🔴 Absente"
        },
    ]
    
    # Affichage en grille
    cols = st.columns(2)
    for idx, employee in enumerate(employees):
        with cols[idx % 2]:
            render_employee_card(employee)
    
    # Planning par esthéticienne
    st.markdown("### 📋 Planning Hebdomadaire")
    
    selected_employee = st.selectbox(
        "Sélectionner une esthéticienne",
        [e['name'] for e in employees],
        index=0
    )
    
    # Graphique de planning
    days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
    hours = ["9h-11h", "11h-13h", "14h-16h", "16h-18h"]
    
    # Créer une heatmap
    data = np.random.randint(0, 3, size=(len(hours), len(days)))
    
    fig = px.imshow(
        data,
        x=days,
        y=hours,
        color_continuous_scale=['rgba(255,255,255,0.1)', COLORS['accent'], COLORS['secondary']],
        labels=dict(x="Jour", y="Créneau", color="RDV"),
        aspect="auto"
    )
    
    fig.update_layout(
        title=f"Planning de {selected_employee}",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['light'])
    )
    
    fig.update_xaxes(side="top")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques équipe
    st.markdown("### 📊 Statistiques de l'Équipe")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #d4af37;">👩‍⚕️</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">{}</div>
            <div style="color: #7f8c8d; font-size: 14px;">Esthéticiennes</div>
        </div>
        """.format(len(employees)), unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #2ecc71;">⭐</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">4.8</div>
            <div style="color: #7f8c8d; font-size: 14px;">Note moyenne</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        total_clients = sum(e['clients'] for e in employees)
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #3498db;">👥</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">{}</div>
            <div style="color: #7f8c8d; font-size: 14px;">Clients actifs</div>
        </div>
        """.format(total_clients), unsafe_allow_html=True)
    
    with col_stat4:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #f39c12;">💼</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">85%</div>
            <div style="color: #7f8c8d; font-size: 14px;">Taux occupation</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_employee_card(employee):
    """Affiche une carte esthéticienne"""
    st.markdown(f"""
    <div class="luxe-card" style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; margin-bottom: 15px;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(248, 200, 220, 0.2));
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-right: 15px;
            ">
                👩‍⚕️
            </div>
            <div>
                <h4 style="color: #d4af37; margin: 0 0 5px 0;">{employee['name']}</h4>
                <div style="color: #7f8c8d; font-size: 12px;">{employee['role']}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <div style="color: #7f8c8d; font-size: 12px; margin-bottom: 5px;">Spécialités</div>
            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                {''.join([f'<span style="background: rgba(52, 152, 219, 0.2); color: #3498db; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{spec}</span>' for spec in employee['specialties']])}
            </div>
        </div>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <div>
                <div style="color: #7f8c8d; font-size: 12px;">Note</div>
                <div style="color: #f39c12; font-weight: 600;">{"⭐" * int(employee['rating'])} {employee['rating']}</div>
            </div>
            <div>
                <div style="color: #7f8c8d; font-size: 12px;">Clients</div>
                <div style="color: #fff; font-weight: 600;">{employee['clients']}</div>
            </div>
            <div>
                <div style="color: #7f8c8d; font-size: 12px;">Status</div>
                <div style="color: {'#2ecc71' if 'Disponible' in employee['status'] else '#f39c12' if 'pause' in employee['status'] else '#e74c3c'}; font-weight: 600;">
                    {employee['status']}
                </div>
            </div>
        </div>
        
        <div style="display: flex; gap: 10px;">
            <button style="
                background: rgba(212, 175, 55, 0.2);
                color: #d4af37;
                border: 1px solid rgba(212, 175, 55, 0.3);
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                flex: 1;
            ">
                📅 Planning
            </button>
            <button style="
                background: rgba(52, 152, 219, 0.2);
                color: #3498db;
                border: 1px solid rgba(52, 152, 219, 0.3);
                padding: 6px 12px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 12px;
                flex: 1;
            ">
                📊 Stats
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_appointment_analytics():
    """Analytics des rendez-vous"""
    st.markdown("""
    <div class="luxe-card">
        <h3 style="color: #d4af37; margin-bottom: 20px;">📊 Analytics Rendez-vous</h3>
    """, unsafe_allow_html=True)
    
    # Métriques
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    
    with col_met1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #d4af37;">📅</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">342</div>
            <div style="color: #7f8c8d; font-size: 14px;">RDV ce mois</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met2:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #2ecc71;">💰</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">28,450€</div>
            <div style="color: #7f8c8d; font-size: 14px;">Revenus RDV</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met3:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #3498db;">⏰</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">94%</div>
            <div style="color: #7f8c8d; font-size: 14px;">Ponctualité</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met4:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 32px; color: #f39c12;">🔄</div>
            <div style="font-size: 24px; font-weight: 600; margin: 10px 0;">4.2</div>
            <div style="color: #7f8c8d; font-size: 14px;">RDV/client</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques
    st.markdown("### 📈 Tendances des Rendez-vous")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Évolution mensuelle
        months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun"]
        appointments = [280, 295, 310, 342, 325, 360]
        revenue = [22500, 23800, 25200, 28450, 26200, 29800]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=months,
            y=appointments,
            name='Nombre de RDV',
            marker_color=COLORS['secondary'],
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=months,
            y=revenue,
            name='Revenus (€)',
            mode='lines+markers',
            line=dict(color='#2ecc71', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Évolution Mensuelle",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['light']),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(
                title='Nombre de RDV',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis2=dict(
                title='Revenus (€)',
                overlaying='y',
                side='right',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            legend=dict(font=dict(color=COLORS['light']))
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        # Répartition par service
        services = {
            "Soins Visage": 85,
            "Massage": 72,
            "Épilation": 58,
            "Manucure": 45,
            "Maquillage": 38,
            "Autres": 44
        }
        
        fig = px.pie(
            values=list(services.values()),
            names=list(services.keys()),
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Gold
        )
        
        fig.update_layout(
            title="Répartition par Service",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['light'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des annulations
    st.markdown("### ⚠️ Analyse des Annulations")
    
    cancellation_data = {
        "Raison": ["Client", "Client", "Boutique", "Client", "Boutique"],
        "Détail": ["Empêchement", "Maladie", "Problème personnel", "Changement d'horaire", "Problème technique"],
        "Nombre": [12, 8, 5, 7, 3],
        "Taux": ["35%", "24%", "15%", "21%", "9%"]
    }
    
    df_cancellations = pd.DataFrame(cancellation_data)
    
    fig = px.bar(
        df_cancellations,
        x='Raison',
        y='Nombre',
        color='Raison',
        color_discrete_sequence=['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#34495e'],
        text='Taux'
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['light']),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Satisfaction clients
    st.markdown("### 😊 Satisfaction Clients")
    
    col_sat1, col_sat2 = st.columns(2)
    
    with col_sat1:
        # Notes
        ratings = {
            "5 ⭐": 65,
            "4 ⭐": 25,
            "3 ⭐": 7,
            "2 ⭐": 2,
            "1 ⭐": 1
        }
        
        fig = px.bar(
            x=list(ratings.keys()),
            y=list(ratings.values()),
            color=list(ratings.values()),
            color_continuous_scale=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        )
        
        fig.update_layout(
            title="Distribution des Notes",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['light']),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_sat2:
        # Commentaires
        st.markdown("#### 💬 Derniers Commentaires")
        
        comments = [
            {"client": "Sophie M.", "comment": "Service exceptionnel, je reviendrai !", "rating": 5},
            {"client": "Marie D.", "comment": "Très professionnelle, résultat parfait", "rating": 5},
            {"client": "Emma L.", "comment": "Un peu d'attente mais service de qualité", "rating": 4},
            {"client": "Julie B.", "comment": "Personnel très attentionné", "rating": 5},
        ]
        
        for comment in comments:
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 10px;
                border-left: 4px solid {'#2ecc71' if comment['rating'] >= 4 else '#f39c12' if comment['rating'] == 3 else '#e74c3c'};
            ">
                <div style="display: flex; justify-content: space-between;">
                    <strong style="color: #d4af37;">{comment['client']}</strong>
                    <span style="color: #f39c12;">{"⭐" * comment['rating']}</span>
                </div>
                <div style="color: #7f8c8d; font-size: 14px; margin-top: 5px;">
                    "{comment['comment']}"
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)