// frontend\src\components\common\ErrorBoundary.jsx
import React from 'react';
import { Box, Typography, Button, Container } from '@mui/material';
import { ErrorOutline, Refresh } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
    
    // Log error to external service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
    
    // Optionally reset app state
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container maxWidth="md">
          <Box
            sx={{
              minHeight: '100vh',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              p: 3,
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                backgroundColor: 'error.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
              }}
            >
              <ErrorOutline sx={{ fontSize: 60, color: 'error.main' }} />
            </Box>

            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Oups ! Une erreur est survenue
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              Nous rencontrons des difficultés techniques. Veuillez réessayer ou contacter le support si le problème persiste.
            </Typography>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box
                sx={{
                  mt: 3,
                  p: 2,
                  backgroundColor: 'background.paper',
                  borderRadius: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  maxWidth: '100%',
                  overflow: 'auto',
                  textAlign: 'left',
                }}
              >
                <Typography variant="caption" color="text.secondary">
                  <strong>Erreur:</strong> {this.state.error.toString()}
                </Typography>
                {this.state.errorInfo && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                    <strong>Stack:</strong> {this.state.errorInfo.componentStack}
                  </Typography>
                )}
              </Box>
            )}

            <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleReset}
              >
                Réessayer
              </Button>
              
              <Button
                variant="outlined"
                onClick={() => window.location.reload()}
              >
                Recharger la page
              </Button>
              
              <Button
                variant="text"
                onClick={() => window.location.href = '/'}
              >
                Retour à l'accueil
              </Button>
            </Box>

            <Typography variant="caption" color="text.secondary" sx={{ mt: 4 }}>
              Code d'erreur: ERR_{Date.now().toString(36).toUpperCase()}
            </Typography>
          </Box>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// Functional component wrapper for easier use
export const withErrorBoundary = (Component, FallbackComponent) => {
  return (props) => (
    <ErrorBoundary FallbackComponent={FallbackComponent}>
      <Component {...props} />
    </ErrorBoundary>
  );
};