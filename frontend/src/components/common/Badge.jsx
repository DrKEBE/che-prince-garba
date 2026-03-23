// frontend\src\components\common\Badge.jsx
import React from 'react';

const Badge = ({ children, variant = "default", className = "", ...props }) => {
  const variantClasses = {
    default: "bg-gray-100 text-gray-800 border border-gray-200",
    primary: "bg-purple-100 text-purple-800 border border-purple-200",
    secondary: "bg-blue-100 text-blue-800 border border-blue-200",
    success: "bg-green-100 text-green-800 border border-green-200",
    warning: "bg-amber-100 text-amber-800 border border-amber-200",
    destructive: "bg-red-100 text-red-800 border border-red-200",
    outline: "border border-gray-300 text-gray-700"
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;