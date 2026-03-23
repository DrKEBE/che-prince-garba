import streamlit as st

def apply_button_style():
    """Applique des styles personnalisés aux boutons"""
    button_style = """
    <style>
    div.stButton > button:first-child {
        background-color: #FF6B9D;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(255, 107, 157, 0.2);
    }
    
    div.stButton > button:first-child:hover {
        background-color: #E0558A;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 107, 157, 0.3);
    }
    
    div.stButton > button:first-child:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px rgba(255, 107, 157, 0.2);
    }
    
    /* Bouton secondaire */
    .secondary-button {
        background-color: #6C757D !important;
        color: white !important;
    }
    
    .secondary-button:hover {
        background-color: #5A6268 !important;
    }
    
    /* Bouton succès */
    .success-button {
        background-color: #28A745 !important;
    }
    
    .success-button:hover {
        background-color: #218838 !important;
    }
    
    /* Bouton danger */
    .danger-button {
        background-color: #DC3545 !important;
    }
    
    .danger-button:hover {
        background-color: #C82333 !important;
    }
    
    /* Bouton info */
    .info-button {
        background-color: #17A2B8 !important;
    }
    
    .info-button:hover {
        background-color: #138496 !important;
    }
    
    /* Bouton warning */
    .warning-button {
        background-color: #FFC107 !important;
        color: #212529 !important;
    }
    
    .warning-button:hover {
        background-color: #E0A800 !important;
    }
    
    /* Bouton outline */
    .outline-button {
        background-color: transparent !important;
        color: #FF6B9D !important;
        border: 2px solid #FF6B9D !important;
    }
    
    .outline-button:hover {
        background-color: #FF6B9D !important;
        color: white !important;
    }
    
    /* Taille des boutons */
    .btn-sm {
        padding: 0.25rem 1rem !important;
        font-size: 14px !important;
    }
    
    .btn-lg {
        padding: 0.75rem 3rem !important;
        font-size: 18px !important;
    }
    
    /* Bouton avec icône */
    .btn-icon {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }
    
    /* Bouton désactivé */
    div.stButton > button:disabled {
        background-color: #E9ECEF !important;
        color: #6C757D !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

def apply_card_style():
    """Applique des styles personnalisés aux cartes"""
    card_style = """
    <style>
    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #E9ECEF;
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .custom-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #F8F9FA;
    }
    
    .custom-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2C3E50;
        margin: 0;
    }
    
    .custom-card-subtitle {
        font-size: 0.875rem;
        color: #7F8C8D;
        margin-top: 0.25rem;
    }
    
    .custom-card-body {
        color: #495057;
    }
    
    .custom-card-footer {
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #E9ECEF;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Variantes de cartes */
    .card-primary {
        border-left: 4px solid #FF6B9D;
    }
    
    .card-success {
        border-left: 4px solid #28A745;
    }
    
    .card-warning {
        border-left: 4px solid #FFC107;
    }
    
    .card-danger {
        border-left: 4px solid #DC3545;
    }
    
    .card-info {
        border-left: 4px solid #17A2B8;
    }
    
    /* Carte statistique */
    .stat-card {
        text-align: center;
        padding: 1.5rem;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2C3E50;
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #7F8C8D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-change {
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    .stat-change.positive {
        color: #28A745;
    }
    
    .stat-change.negative {
        color: #DC3545;
    }
    
    /* Carte produit */
    .product-card {
        overflow: hidden;
    }
    
    .product-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .product-price {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FF6B9D;
    }
    
    .product-stock {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .stock-available {
        background-color: #D4EDDA;
        color: #155724;
    }
    
    .stock-low {
        background-color: #FFF3CD;
        color: #856404;
    }
    
    .stock-out {
        background-color: #F8D7DA;
        color: #721C24;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

def apply_form_style():
    """Applique des styles personnalisés aux formulaires"""
    form_style = """
    <style>
    /* Conteneur de formulaire */
    .form-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Groupes de champs */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #2C3E50;
    }
    
    /* Champs de saisie */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input {
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        padding: 0.625rem 1rem;
        font-size: 0.9375rem;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stTextArea > div > div > textarea:focus,
    .stDateInput > div > div > input:focus {
        border-color: #FF6B9D;
        box-shadow: 0 0 0 0.2rem rgba(255, 107, 157, 0.25);
        outline: none;
    }
    
    /* Validation */
    .invalid-feedback {
        color: #DC3545;
        font-size: 0.875rem;
        margin-top: 0.25rem;
        display: none;
    }
    
    .was-validated .invalid-feedback {
        display: block;
    }
    
    /* Checkbox et radio */
    .stCheckbox > label,
    .stRadio > label {
        color: #495057;
        font-weight: 400;
    }
    
    /* Section de formulaire */
    .form-section {
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #E9ECEF;
    }
    
    .form-section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Grille de formulaire */
    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* Actions de formulaire */
    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E9ECEF;
    }
    
    /* Champs obligatoires */
    .required::after {
        content: " *";
        color: #DC3545;
    }
    
    /* Aide de champ */
    .form-text {
        font-size: 0.875rem;
        color: #6C757D;
        margin-top: 0.25rem;
    }
    
    /* Téléchargement de fichiers */
    .stFileUploader > div {
        border: 2px dashed #DEE2E6;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        transition: all 0.2s;
    }
    
    .stFileUploader > div:hover {
        border-color: #FF6B9D;
        background-color: rgba(255, 107, 157, 0.02);
    }
    </style>
    """
    st.markdown(form_style, unsafe_allow_html=True)

def apply_table_style():
    """Applique des styles personnalisés aux tableaux"""
    table_style = """
    <style>
    /* Tableau principal */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* En-têtes de tableau */
    .dataframe thead th {
        background-color: #2C3E50 !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        border: none !important;
        padding: 1rem !important;
    }
    
    /* Cellules de tableau */
    .dataframe tbody td {
        padding: 0.75rem 1rem !important;
        border-bottom: 1px solid #E9ECEF !important;
        font-size: 0.875rem;
    }
    
    .dataframe tbody tr:hover {
        background-color: #F8F9FA !important;
    }
    
    /* Lignes alternées */
    .dataframe tbody tr:nth-child(even) {
        background-color: #F8F9FA !important;
    }
    
    /* Tableau compact */
    .table-sm .dataframe tbody td {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.8125rem;
    }
    
    .table-sm .dataframe thead th {
        padding: 0.75rem !important;
    }
    
    /* Tableau avec bordures */
    .table-bordered .dataframe {
        border: 1px solid #E9ECEF !important;
    }
    
    .table-bordered .dataframe th,
    .table-bordered .dataframe td {
        border: 1px solid #E9ECEF !important;
    }
    
    /* Tableau striped */
    .table-striped .dataframe tbody tr:nth-child(odd) {
        background-color: #F8F9FA !important;
    }
    
    /* Actions de tableau */
    .table-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .table-action-btn {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.75rem !important;
        border-radius: 4px !important;
        border: none !important;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .table-action-btn:hover {
        opacity: 0.8;
    }
    
    .btn-view {
        background-color: #17A2B8 !important;
        color: white !important;
    }
    
    .btn-edit {
        background-color: #FFC107 !important;
        color: #212529 !important;
    }
    
    .btn-delete {
        background-color: #DC3545 !important;
        color: white !important;
    }
    
    /* Badges dans les tableaux */
    .table-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        text-align: center;
        min-width: 80px;
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
    }
    
    .page-link {
        padding: 0.5rem 0.75rem;
        border: 1px solid #DEE2E6;
        background-color: white;
        color: #007BFF;
        text-decoration: none;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .page-link:hover {
        background-color: #E9ECEF;
        border-color: #DEE2E6;
    }
    
    .page-link.active {
        background-color: #007BFF;
        border-color: #007BFF;
        color: white;
    }
    
    .page-link.disabled {
        color: #6C757D;
        pointer-events: none;
        background-color: #E9ECEF;
        border-color: #DEE2E6;
    }
    </style>
    """
    st.markdown(table_style, unsafe_allow_html=True)

def apply_alert_style():
    """Applique des styles personnalisés aux alertes"""
    alert_style = """
    <style>
    /* Alertes personnalisées */
    .custom-alert {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .alert-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .alert-content {
        flex-grow: 1;
    }
    
    .alert-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .alert-message {
        margin: 0;
        line-height: 1.5;
    }
    
    .alert-dismiss {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.25rem;
        color: inherit;
        opacity: 0.7;
        transition: opacity 0.2s;
        padding: 0;
        margin: 0;
    }
    
    .alert-dismiss:hover {
        opacity: 1;
    }
    
    /* Types d'alertes */
    .alert-success {
        background-color: #D4EDDA;
        border-left-color: #28A745;
        color: #155724;
    }
    
    .alert-warning {
        background-color: #FFF3CD;
        border-left-color: #FFC107;
        color: #856404;
    }
    
    .alert-danger {
        background-color: #F8D7DA;
        border-left-color: #DC3545;
        color: #721C24;
    }
    
    .alert-info {
        background-color: #D1ECF1;
        border-left-color: #17A2B8;
        color: #0C5460;
    }
    
    .alert-primary {
        background-color: #D1E7FF;
        border-left-color: #0D6EFD;
        color: #084298;
    }
    
    /* Toast notifications */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .toast.fade-out {
        animation: slideOutRight 0.3s ease-in forwards;
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25em 0.75em;
        font-size: 0.75em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 20px;
    }
    
    .badge-pill {
        border-radius: 20px;
    }
    
    .badge-primary {
        background-color: #0D6EFD;
        color: white;
    }
    
    .badge-secondary {
        background-color: #6C757D;
        color: white;
    }
    
    .badge-success {
        background-color: #28A745;
        color: white;
    }
    
    .badge-danger {
        background-color: #DC3545;
        color: white;
    }
    
    .badge-warning {
        background-color: #FFC107;
        color: #212529;
    }
    
    .badge-info {
        background-color: #17A2B8;
        color: white;
    }
    
    .badge-light {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    .badge-dark {
        background-color: #212529;
        color: white;
    }
    </style>
    """
    st.markdown(alert_style, unsafe_allow_html=True)