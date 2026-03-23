// frontend\src\utils\formatters.js
/**
 * Utility functions for formatting data
 */

export const formatCurrency = (value, currency = 'XOF') => {
  if (value === null || value === undefined) return '0 F';
  
  // Si currency n'est pas une chaîne de 3 lettres, on utilise 'XOF' (cas où Recharts passe un index)
  if (typeof currency !== 'string' || currency.length !== 3) {
    currency = 'XOF';
  }
  
  try {
    return new Intl.NumberFormat('fr-CI', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  } catch (e) {
    // Fallback sécurisé
    return `${value} F`;
  }
};

export const formatDate = (date, format = 'dd/MM/yyyy HH:mm') => {
  if (!date) return '';
  
  const dateObj = new Date(date);
  
  if (format === 'relative') {
    const now = new Date();
    const diffInSeconds = Math.floor((now - dateObj) / 1000);
    
    if (diffInSeconds < 60) return 'à l\'instant';
    if (diffInSeconds < 3600) return `il y a ${Math.floor(diffInSeconds / 60)} min`;
    if (diffInSeconds < 86400) return `il y a ${Math.floor(diffInSeconds / 3600)} h`;
    if (diffInSeconds < 604800) return `il y a ${Math.floor(diffInSeconds / 86400)} j`;
    
    return dateObj.toLocaleDateString('fr-FR');
  }
  
  if (format === 'short') {
    return dateObj.toLocaleDateString('fr-FR');
  }
  
  if (format === 'long') {
    return dateObj.toLocaleDateString('fr-FR', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
  
  return dateObj.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  
  // Remove all non-digits
  const cleaned = phone.replace(/\D/g, '');
  
  // Format based on length
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
  }
  
  if (cleaned.length === 8) {
    return cleaned.replace(/(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4');
  }
  
  return phone;
};

export const formatStockStatus = (stock, threshold) => {
  if (stock <= 0) {
    return { label: 'Rupture', color: 'error', severity: 'high' };
  }
  
  if (stock <= threshold) {
    return { label: 'Faible', color: 'warning', severity: 'medium' };
  }
  
  if (stock <= threshold * 2) {
    return { label: 'Normal', color: 'success', severity: 'low' };
  }
  
  return { label: 'Excédent', color: 'info', severity: 'low' };
};

export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) return '0%';

  const percentage = value <= 1 ? value * 100 : value;

  return `${percentage.toFixed(decimals)}%`;
};

export const truncateText = (text, maxLength = 50) => {
  if (!text) return '';
  
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const generateInvoiceNumber = () => {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
  
  return `FACT-${year}${month}${day}-${random}`;
};

export const calculateAge = (birthDate) => {
  if (!birthDate) return null;
  
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  
  return age;
};

export const formatDuration = (minutes) => {
  if (!minutes) return '0 min';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours === 0) return `${mins} min`;
  if (mins === 0) return `${hours} h`;
  
  return `${hours} h ${mins} min`;
};

export const slugify = (text) => {
  return text
    .toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)+/g, '');
};