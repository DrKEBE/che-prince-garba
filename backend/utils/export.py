"""
Module d'exportation de données (Excel, CSV, PDF)
"""
import csv
import json
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """
    Exporte des données en CSV
    """
    if not data:
        return ""
    
    # Créer le nom de fichier complet
    filepath = f"/tmp/{filename}.csv"
    
    # Déterminer les en-têtes
    headers = list(data[0].keys()) if data else []
    
    # Écrire le CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    return filepath

def export_to_excel(data: List[Dict[str, Any]], filename: str, sheet_name: str = "Données") -> str:
    """
    Exporte des données en Excel (XLSX)
    """
    if not HAS_PANDAS:
        # Fallback vers CSV si pandas n'est pas disponible
        return export_to_csv(data, filename)
    
    if not data:
        return ""
    
    # Créer le nom de fichier complet
    filepath = f"/tmp/{filename}.xlsx"
    
    # Convertir en DataFrame pandas
    df = pd.DataFrame(data)
    
    # Exporter vers Excel
    df.to_excel(filepath, sheet_name=sheet_name, index=False)
    
    return filepath

def export_to_pdf(data: List[Dict[str, Any]], filename: str, title: str = "Export") -> str:
    """
    Exporte des données en PDF
    """
    if not HAS_REPORTLAB:
        raise ImportError("ReportLab n'est pas installé. Installez-le avec: pip install reportlab")
    
    if not data:
        return ""
    
    # Créer le nom de fichier complet
    filepath = f"/tmp/{filename}.pdf"
    
    # Créer le document PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Titre
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espace
    
    # Préparer les données du tableau
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        
        for row in data:
            table_data.append([str(row.get(h, '')) for h in headers])
        
        # Créer le tableau
        table = Table(table_data)
        
        # Style du tableau
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
    
    # Générer le PDF
    doc.build(elements)
    
    return filepath

def export_to_json(data: List[Dict[str, Any]], filename: str) -> str:
    """
    Exporte des données en JSON
    """
    if not data:
        return ""
    
    # Créer le nom de fichier complet
    filepath = f"/tmp/{filename}.json"
    
    # Exporter en JSON
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=2, default=str)
    
    return filepath

def cleanup_old_exports(max_age_hours: int = 24):
    """
    Nettoie les anciens fichiers d'export
    """
    import glob
    import os
    import time
    
    tmp_dir = "/tmp"
    patterns = ["*.csv", "*.xlsx", "*.pdf", "*.json"]
    
    current_time = time.time()
    
    for pattern in patterns:
        for filepath in glob.glob(os.path.join(tmp_dir, pattern)):
            try:
                file_age_hours = (current_time - os.path.getctime(filepath)) / 3600
                if file_age_hours > max_age_hours:
                    os.remove(filepath)
            except (OSError, FileNotFoundError):
                pass