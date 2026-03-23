import React from 'react';
import { Button as MuiButton } from '@mui/material';
import { useTheme } from '@mui/material/styles';

/**
 * Bouton MUI sécurisé avec fallback pour les erreurs de thème
 */
const SafeMuiButton = React.forwardRef((props, ref) => {
  const theme = useTheme();
  
  // Fallback pour les couleurs si le thème n'est pas disponible
  const getSafeColor = () => {
    if (!theme.palette) {
      console.warn('Theme palette is not available, using fallback colors');
      return 'primary';
    }
    
    const color = props.color || 'primary';
    
    // Vérifier si la couleur existe dans le thème
    if (color && theme.palette[color]) {
      return color;
    }
    
    console.warn(`Color "${color}" not found in theme, falling back to primary`);
    return 'primary';
  };
  
  const safeProps = {
    ...props,
    color: getSafeColor(),
  };
  
  return <MuiButton ref={ref} {...safeProps} />;
});

SafeMuiButton.displayName = 'SafeMuiButton';

export default SafeMuiButton;