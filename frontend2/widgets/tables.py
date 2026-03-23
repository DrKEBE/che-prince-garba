"""
Composants de tableaux avancés
"""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Callable
import json

from utils.formatters import format_currency, format_date, format_phone_number
from config.theme import ThemeManager

class TableComponents:
    """Composants de tableaux"""
    
    @staticmethod
    def create_data_table(
        data: List[Dict[str, Any]],
        columns: List[Dict[str, str]] = None,
        title: str = "",
        page_size: int = 10,
        show_search: bool = True,
        show_export: bool = True,
        show_actions: bool = True,
        row_actions: List[Dict[str, Any]] = None,
        selectable: bool = False,
        key: str = "table"
    ) -> None:
        """
        Crée un tableau de données interactif
        """
        if not data:
            st.info("Aucune donnée à afficher")
            return
        
        # Convertir en DataFrame
        df = pd.DataFrame(data)
        
        # Créer le conteneur
        with st.container():
            # En-tête du tableau
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                if title:
                    st.subheader(title)
            
            with col2:
                if show_search:
                    search_term = st.text_input(
                        "🔍 Rechercher",
                        placeholder="Rechercher...",
                        key=f"{key}_search"
                    )
                    
                    if search_term:
                        # Filtrer les données
                        mask = df.apply(
                            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
                            axis=1
                        )
                        df = df[mask]
            
            with col3:
                if show_export:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📥 CSV", key=f"{key}_csv"):
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Télécharger CSV",
                                data=csv,
                                file_name=f"export_{key}.csv",
                                mime="text/csv"
                            )
                    with col_b:
                        if st.button("📊 Excel", key=f"{key}_excel"):
                            # Dans une implémentation réelle, utiliser pandas.ExcelWriter
                            st.info("Export Excel à venir")
            
            # Tableau principal
            if selectable:
                # Ajouter une colonne de sélection
                df.insert(0, "select", False)
                
                # Afficher avec sélection
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "select": st.column_config.CheckboxColumn("Sélection")
                    },
                    hide_index=True,
                    use_container_width=True,
                    key=f"{key}_editor"
                )
                
                # Récupérer les lignes sélectionnées
                selected_rows = edited_df[edited_df["select"]]
                selected_ids = selected_rows.get("id", pd.Series()).tolist()
                
                if selected_ids:
                    st.caption(f"{len(selected_ids)} élément(s) sélectionné(s)")
            else:
                # Afficher sans sélection
                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True,
                    column_config=columns
                )
            
            # Pagination
            total_rows = len(df)
            if total_rows > page_size:
                current_page = st.session_state.get(f"{key}_page", 1)
                total_pages = (total_rows + page_size - 1) // page_size
                
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    st.caption(f"Page {current_page} sur {total_pages} • {total_rows} éléments")
                    
                    # Contrôles de pagination
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if st.button("⏮️", key=f"{key}_first"):
                            st.session_state[f"{key}_page"] = 1
                            st.rerun()
                    with col2:
                        if st.button("◀️", key=f"{key}_prev"):
                            if current_page > 1:
                                st.session_state[f"{key}_page"] = current_page - 1
                                st.rerun()
                    with col3:
                        page_input = st.number_input(
                            "Page",
                            min_value=1,
                            max_value=total_pages,
                            value=current_page,
                            key=f"{key}_input",
                            label_visibility="collapsed"
                        )
                        if page_input != current_page:
                            st.session_state[f"{key}_page"] = page_input
                            st.rerun()
                    with col4:
                        if st.button("▶️", key=f"{key}_next"):
                            if current_page < total_pages:
                                st.session_state[f"{key}_page"] = current_page + 1
                                st.rerun()
                    with col5:
                        if st.button("⏭️", key=f"{key}_last"):
                            st.session_state[f"{key}_page"] = total_pages
                            st.rerun()
            
            # Actions en masse
            if selectable and show_actions and selected_ids:
                st.divider()
                
                with st.expander("Actions sur les éléments sélectionnés"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📧 Envoyer email", key=f"{key}_email"):
                            st.info(f"Email à envoyer à {len(selected_ids)} client(s)")
                    
                    with col2:
                        if st.button("📊 Exporter sélection", key=f"{key}_export_sel"):
                            selected_data = [item for item in data if item.get('id') in selected_ids]
                            st.download_button(
                                "Télécharger JSON",
                                data=json.dumps(selected_data, indent=2),
                                file_name=f"selection_{key}.json"
                            )
                    
                    with col3:
                        if st.button("🗑️ Supprimer", type="secondary", key=f"{key}_delete"):
                            st.warning(f"Supprimer {len(selected_ids)} élément(s) ?")
                            if st.button("Confirmer", type="primary"):
                                st.success(f"{len(selected_ids)} élément(s) supprimé(s)")
    
    @staticmethod
    def create_products_table(products: List[Dict[str, Any]], **kwargs) -> None:
        """
        Tableau spécialisé pour les produits
        """
        # Configuration des colonnes
        column_config = {
            "id": st.column_config.TextColumn("ID", width="small"),
            "name": st.column_config.TextColumn("Nom", width="large"),
            "category": st.column_config.TextColumn("Catégorie", width="medium"),
            "selling_price": st.column_config.NumberColumn(
                "Prix de vente",
                format="%.2f FCFA"
            ),
            "current_stock": st.column_config.NumberColumn("Stock"),
            "stock_status": st.column_config.TextColumn("Statut", width="small"),
            "actions": st.column_config.Column("Actions", width="medium")
        }
        
        # Formater les données
        formatted_data = []
        for product in products:
            formatted = {
                "id": product.get("id", ""),
                "name": product.get("name", ""),
                "category": product.get("category", ""),
                "selling_price": float(product.get("selling_price", 0)),
                "current_stock": product.get("current_stock", 0),
                "stock_status": TableComponents._get_stock_status_badge(
                    product.get("current_stock", 0),
                    product.get("alert_threshold", 10)
                ),
                "actions": f"""
                <div style="display: flex; gap: 5px;">
                    <button onclick="editProduct('{product.get('id')}')" style="
                        padding: 2px 8px;
                        background: #FFC107;
                        color: #212529;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">✏️</button>
                    <button onclick="viewProduct('{product.get('id')}')" style="
                        padding: 2px 8px;
                        background: #17A2B8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">👁️</button>
                    <button onclick="deleteProduct('{product.get('id')}')" style="
                        padding: 2px 8px;
                        background: #DC3545;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">🗑️</button>
                </div>
                """
            }
            formatted_data.append(formatted)
        
        # Créer le tableau
        TableComponents.create_data_table(
            formatted_data,
            columns=column_config,
            title="📦 Liste des produits",
            **kwargs
        )
    
    @staticmethod
    def create_sales_table(sales: List[Dict[str, Any]], **kwargs) -> None:
        """
        Tableau spécialisé pour les ventes
        """
        # Configuration des colonnes
        column_config = {
            "invoice_number": st.column_config.TextColumn("Facture", width="medium"),
            "client_name": st.column_config.TextColumn("Client", width="medium"),
            "sale_date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY HH:mm"),
            "final_amount": st.column_config.NumberColumn("Montant", format="%.2f FCFA"),
            "payment_method": st.column_config.TextColumn("Paiement", width="small"),
            "payment_status": st.column_config.TextColumn("Statut", width="small"),
            "actions": st.column_config.Column("Actions", width="medium")
        }
        
        # Formater les données
        formatted_data = []
        for sale in sales:
            formatted = {
                "invoice_number": sale.get("invoice_number", ""),
                "client_name": sale.get("client_name", "Client non spécifié"),
                "sale_date": sale.get("sale_date"),
                "final_amount": float(sale.get("final_amount", 0)),
                "payment_method": sale.get("payment_method", ""),
                "payment_status": TableComponents._get_payment_status_badge(
                    sale.get("payment_status", "")
                ),
                "actions": f"""
                <div style="display: flex; gap: 5px;">
                    <button onclick="viewSale('{sale.get('id')}')" style="
                        padding: 2px 8px;
                        background: #17A2B8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">👁️</button>
                    <button onclick="printInvoice('{sale.get('id')}')" style="
                        padding: 2px 8px;
                        background: #28A745;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">🖨️</button>
                    <button onclick="refundSale('{sale.get('id')}')" style="
                        padding: 2px 8px;
                        background: #FFC107;
                        color: #212529;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">💸</button>
                </div>
                """
            }
            formatted_data.append(formatted)
        
        # Créer le tableau
        TableComponents.create_data_table(
            formatted_data,
            columns=column_config,
            title="💰 Liste des ventes",
            **kwargs
        )
    
    @staticmethod
    def create_clients_table(clients: List[Dict[str, Any]], **kwargs) -> None:
        """
        Tableau spécialisé pour les clients
        """
        # Configuration des colonnes
        column_config = {
            "full_name": st.column_config.TextColumn("Nom complet", width="large"),
            "phone": st.column_config.TextColumn("Téléphone", width="medium"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "client_type": st.column_config.TextColumn("Type", width="small"),
            "total_purchases": st.column_config.NumberColumn("Total achats", format="%.2f FCFA"),
            "last_purchase": st.column_config.DatetimeColumn("Dernier achat", format="DD/MM/YYYY"),
            "actions": st.column_config.Column("Actions", width="medium")
        }
        
        # Formater les données
        formatted_data = []
        for client in clients:
            formatted = {
                "full_name": client.get("full_name", ""),
                "phone": format_phone_number(client.get("phone", "")),
                "email": client.get("email", ""),
                "client_type": TableComponents._get_client_type_badge(
                    client.get("client_type", "")
                ),
                "total_purchases": float(client.get("total_purchases", 0)),
                "last_purchase": client.get("last_purchase"),
                "actions": f"""
                <div style="display: flex; gap: 5px;">
                    <button onclick="viewClient('{client.get('id')}')" style="
                        padding: 2px 8px;
                        background: #17A2B8;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">👁️</button>
                    <button onclick="editClient('{client.get('id')}')" style="
                        padding: 2px 8px;
                        background: #FFC107;
                        color: #212529;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">✏️</button>
                    <button onclick="newSaleForClient('{client.get('id')}')" style="
                        padding: 2px 8px;
                        background: #28A745;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 12px;
                    ">💰</button>
                </div>
                """
            }
            formatted_data.append(formatted)
        
        # Créer le tableau
        TableComponents.create_data_table(
            formatted_data,
            columns=column_config,
            title="👥 Liste des clients",
            **kwargs
        )
    
    @staticmethod
    def _get_stock_status_badge(stock: int, threshold: int = 10) -> str:
        """Crée un badge pour le statut du stock"""
        if stock <= 0:
            return "🔴 Rupture"
        elif stock <= threshold:
            return "🟡 Faible"
        else:
            return "🟢 Normal"
    
    @staticmethod
    def _get_payment_status_badge(status: str) -> str:
        """Crée un badge pour le statut de paiement"""
        status_map = {
            "PAID": "✅ Payé",
            "PENDING": "⏳ En attente",
            "PARTIAL": "💰 Partiel",
            "CANCELLED": "❌ Annulé",
            "REFUNDED": "💸 Remboursé"
        }
        return status_map.get(status, status)
    
    @staticmethod
    def _get_client_type_badge(client_type: str) -> str:
        """Crée un badge pour le type de client"""
        type_map = {
            "REGULAR": "🟢 Régulier",
            "VIP": "⭐ VIP",
            "FIDELITE": "👑 Fidélité",
            "WHOLESALER": "🏢 Grossiste"
        }
        return type_map.get(client_type, client_type)
    
    @staticmethod
    def create_summary_table(metrics: Dict[str, Any], title: str = "Résumé") -> None:
        """
        Crée un tableau de résumé des métriques
        """
        st.markdown(f"### {title}")
        
        # Créer un DataFrame à partir des métriques
        rows = []
        for key, value in metrics.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    rows.append({
                        "Métrique": f"{key} - {subkey}",
                        "Valeur": subvalue
                    })
            else:
                rows.append({
                    "Métrique": key.replace("_", " ").title(),
                    "Valeur": value
                })
        
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Métrique": st.column_config.TextColumn("Métrique", width="medium"),
                    "Valeur": st.column_config.TextColumn("Valeur", width="medium")
                }
            )
    
    @staticmethod
    def create_comparison_table(
        actual: Dict[str, Any],
        target: Dict[str, Any],
        title: str = "Comparaison Objectif vs Réel"
    ) -> None:
        """
        Crée un tableau de comparaison
        """
        st.markdown(f"### {title}")
        
        rows = []
        for key in set(actual.keys()) | set(target.keys()):
            actual_val = actual.get(key, 0)
            target_val = target.get(key, 0)
            
            # Calculer la différence et le pourcentage
            diff = actual_val - target_val
            if target_val != 0:
                percentage = (diff / target_val) * 100
            else:
                percentage = 0
            
            rows.append({
                "Indicateur": key.replace("_", " ").title(),
                "Objectif": target_val,
                "Réel": actual_val,
                "Différence": diff,
                "%": f"{percentage:.1f}%"
            })
        
        df = pd.DataFrame(rows)
        
        # Appliquer un style conditionnel
        def color_diff(val):
            if isinstance(val, (int, float)):
                if val > 0:
                    return 'color: #28A745; font-weight: bold;'
                elif val < 0:
                    return 'color: #DC3545; font-weight: bold;'
            return ''
        
        styled_df = df.style.applymap(color_diff, subset=['Différence'])
        
        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True
        )

# Fonctions d'export
def create_data_table(*args, **kwargs):
    """Crée un tableau de données (fonction d'export)"""
    return TableComponents.create_data_table(*args, **kwargs)

def create_products_table(*args, **kwargs):
    """Crée un tableau de produits (fonction d'export)"""
    return TableComponents.create_products_table(*args, **kwargs)

def create_sales_table(*args, **kwargs):
    """Crée un tableau de ventes (fonction d'export)"""
    return TableComponents.create_sales_table(*args, **kwargs)

def create_clients_table(*args, **kwargs):
    """Crée un tableau de clients (fonction d'export)"""
    return TableComponents.create_clients_table(*args, **kwargs)