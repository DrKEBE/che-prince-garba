// frontend\src\utils\helpers.js
/**
 * General helper functions
 */

/**
 * Debounce function to limit how often a function can be called
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function to limit function execution rate
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Deep clone an object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  
  if (obj instanceof Date) return new Date(obj.getTime());
  
  if (obj instanceof Array) {
    const copy = [];
    for (let i = 0; i < obj.length; i++) {
      copy[i] = deepClone(obj[i]);
    }
    return copy;
  }
  
  if (typeof obj === 'object') {
    const copy = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        copy[key] = deepClone(obj[key]);
      }
    }
    return copy;
  }
  
  return obj;
};

/**
 * Merge two objects deeply
 */
export const deepMerge = (target, source) => {
  const output = deepClone(target);
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!(key in target)) {
          Object.assign(output, { [key]: source[key] });
        } else {
          output[key] = deepMerge(target[key], source[key]);
        }
      } else {
        Object.assign(output, { [key]: source[key] });
      }
    });
  }
  
  return output;
};

/**
 * Check if value is an object
 */
export const isObject = (item) => {
  return item && typeof item === 'object' && !Array.isArray(item);
};

/**
 * Generate a unique ID
 */
export const generateId = () => {
  return 'id-' + Math.random().toString(36).substr(2, 9);
};

/**
 * Capitalize first letter of each word
 */
export const capitalize = (str) => {
  if (!str) return '';
  
  return str
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Convert object to query string
 */
export const objectToQueryString = (obj) => {
  if (!obj) return '';
  
  const params = new URLSearchParams();
  
  Object.keys(obj).forEach(key => {
    if (obj[key] !== null && obj[key] !== undefined && obj[key] !== '') {
      if (Array.isArray(obj[key])) {
        obj[key].forEach(value => {
          params.append(key, value);
        });
      } else {
        params.append(key, obj[key]);
      }
    }
  });
  
  return params.toString();
};

/**
 * Parse query string to object
 */
export const queryStringToObject = (queryString) => {
  if (!queryString) return {};
  
  const params = new URLSearchParams(queryString);
  const obj = {};
  
  for (const [key, value] of params.entries()) {
    if (obj[key]) {
      if (Array.isArray(obj[key])) {
        obj[key].push(value);
      } else {
        obj[key] = [obj[key], value];
      }
    } else {
      obj[key] = value;
    }
  }
  
  return obj;
};

/**
 * Format number with thousands separator
 */
export const formatNumber = (number, decimals = 0) => {
  if (number === null || number === undefined) return '0';
  
  return number.toLocaleString('fr-FR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

/**
 * Get initials from name
 */
export const getInitials = (name) => {
  if (!name) return '?';
  
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

/**
 * Calculate reading time for text
 */
export const calculateReadingTime = (text, wordsPerMinute = 200) => {
  if (!text) return 0;
  
  const words = text.trim().split(/\s+/).length;
  const minutes = words / wordsPerMinute;
  
  return Math.ceil(minutes);
};

/**
 * Download data as file
 */
export const downloadFile = (data, filename, type = 'text/plain') => {
  const blob = new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    
    try {
      document.execCommand('copy');
      return true;
    } catch (err) {
      return false;
    } finally {
      document.body.removeChild(textArea);
    }
  }
};

/**
 * Generate random color
 */
export const getRandomColor = () => {
  const colors = [
    '#8A2BE2', '#FF4081', '#3B82F6', '#10B981', '#F59E0B',
    '#6366F1', '#EC4899', '#14B8A6', '#F97316', '#8B5CF6',
  ];
  
  return colors[Math.floor(Math.random() * colors.length)];
};

/**
 * Sleep/wait for specified time
 */
export const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Check if running on mobile device
 */
export const isMobileDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
};

/**
 * Safe JSON parse
 */
export const safeJsonParse = (str, defaultValue = null) => {
  try {
    return JSON.parse(str);
  } catch {
    return defaultValue;
  }
};

/**
 * Group array by key
 */
export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const groupKey = item[key];
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {});
};

/**
 * Remove duplicates from array
 */
export const removeDuplicates = (array, key) => {
  if (!key) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
};