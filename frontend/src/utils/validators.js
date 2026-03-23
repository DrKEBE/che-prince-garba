// frontend\src\utils\validators.js
/**
 * Validation utility functions
 */

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePhone = (phone) => {
  const re = /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,3}[-\s.]?[0-9]{3,4}[-\s.]?[0-9]{3,4}$/;
  return re.test(phone);
};

export const validateRequired = (value) => {
  return value !== null && value !== undefined && value !== '';
};

export const validateMinLength = (value, min) => {
  return value.length >= min;
};

export const validateMaxLength = (value, max) => {
  return value.length <= max;
};

export const validateNumeric = (value) => {
  return !isNaN(parseFloat(value)) && isFinite(value);
};

export const validatePositiveNumber = (value) => {
  return validateNumeric(value) && parseFloat(value) >= 0;
};

export const validateNegativeNumber = (value) => {
  return validateNumeric(value) && parseFloat(value) < 0;
};

export const validatePercentage = (value) => {
  return validateNumeric(value) && parseFloat(value) >= 0 && parseFloat(value) <= 100;
};

export const validateDate = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  return dateObj instanceof Date && !isNaN(dateObj);
};

export const validateFutureDate = (date) => {
  if (!validateDate(date)) return false;
  
  const dateObj = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  return dateObj >= today;
};

export const validatePastDate = (date) => {
  if (!validateDate(date)) return false;
  
  const dateObj = new Date(date);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  return dateObj <= today;
};

export const validatePassword = (password) => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
  return re.test(password);
};

export const validateSKU = (sku) => {
  // Alphanumeric, 3-50 characters
  const re = /^[a-zA-Z0-9-_]{3,50}$/;
  return re.test(sku);
};

export const validateBarcode = (barcode) => {
  // Common barcode formats
  if (!barcode) return true;
  
  // EAN-13 (13 digits)
  if (/^\d{13}$/.test(barcode)) return true;
  
  // UPC-A (12 digits)
  if (/^\d{12}$/.test(barcode)) return true;
  
  // ISBN (10 or 13 digits with possible dashes)
  if (/^(\d{10}|\d{13}|\d{9}[0-9X])$/.test(barcode)) return true;
  
  // Generic: alphanumeric, 6-50 characters
  return /^[a-zA-Z0-9-_]{6,50}$/.test(barcode);
};

export const validateColorCode = (color) => {
  // HEX, RGB, or RGBA
  const hexRe = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
  const rgbRe = /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/;
  const rgbaRe = /^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(0|1|0?\.\d+)\s*\)$/;
  
  return hexRe.test(color) || rgbRe.test(color) || rgbaRe.test(color);
};

export const validateURL = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateFileType = (file, allowedTypes) => {
  if (!file) return true;
  
  const fileType = file.type;
  return allowedTypes.includes(fileType);
};

export const validateFileSize = (file, maxSizeMB) => {
  if (!file) return true;
  
  const maxSize = maxSizeMB * 1024 * 1024; // Convert MB to bytes
  return file.size <= maxSize;
};

export const validateQuantity = (quantity, availableStock) => {
  return validatePositiveNumber(quantity) && 
         parseInt(quantity) > 0 && 
         parseInt(quantity) <= availableStock;
};

export const validatePrice = (price) => {
  return validatePositiveNumber(price) && parseFloat(price) >= 0;
};

export const validateMargin = (purchasePrice, sellingPrice) => {
  if (!validatePrice(purchasePrice) || !validatePrice(sellingPrice)) {
    return false;
  }
  
  return parseFloat(sellingPrice) >= parseFloat(purchasePrice);
};