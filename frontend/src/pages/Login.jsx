// frontend\src\pages\Login.jsx
import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  IconButton,
  InputAdornment,
  Divider,
} from '@mui/material';
import {
  Lock,
  Person,
  Visibility,
  VisibilityOff,
  Spa,
  Email,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [errors, setErrors] = useState({});

  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const from = location.state?.from?.pathname || '/';

  const validate = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    }
    
    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    setLoading(true);
    setErrors({});
    
    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        toast.success(`Bienvenue ${result.user.full_name || result.user.username}!`);
        navigate(from, { replace: true });
      } else {
        setErrors({ general: result.error });
        toast.error(result.error);
      }
    } catch (error) {
      setErrors({ general: 'Une erreur est survenue. Veuillez réessayer.' });
      toast.error('Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #8A2BE2 0%, #FF4081 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated background elements */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
        }}
      />
      
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, -180, -360],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          position: 'absolute',
          bottom: '10%',
          right: '10%',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
        }}
      />

      <Container maxWidth="sm">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper
            elevation={24}
            sx={{
              p: 4,
              borderRadius: 4,
              backdropFilter: 'blur(20px)',
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            {/* Logo and Title */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, type: 'spring' }}
              >
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #8A2BE2 0%, #FF4081 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px',
                    color: 'white',
                  }}
                >
                  <Spa sx={{ fontSize: 40 }} />
                </Box>
              </motion.div>
              
              <Typography
                variant="h4"
                fontWeight="bold"
                gutterBottom
                className="gradient-text"
              >
                Luxe Beauté
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Connectez-vous à votre espace de gestion
              </Typography>
            </Box>

            {/* Error Alert */}
            {errors.general && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {errors.general}
              </Alert>
            )}

            {/* Login Form */}
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Nom d'utilisateur ou Email"
                name="username"
                value={formData.username}
                onChange={handleChange}
                error={!!errors.username}
                helperText={errors.username}
                disabled={loading}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person color="action" />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                fullWidth
                label="Mot de passe"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                error={!!errors.password}
                helperText={errors.password}
                disabled={loading}
                sx={{ mb: 3 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Button
                  fullWidth
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{
                    mt: 2,
                    mb: 3,
                    py: 1.5,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #8A2BE2 0%, #FF4081 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #7B1FA2 0%, #C60055 100%)',
                    },
                  }}
                >
                  {loading ? 'Connexion...' : 'Se connecter'}
                </Button>
              </motion.div>

              <Divider sx={{ my: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  OU
                </Typography>
              </Divider>

              <Typography
                variant="body2"
                align="center"
                color="text.secondary"
                sx={{ mt: 3 }}
              >
                Version de démonstration - Utilisez les identifiants de test
              </Typography>
              <Typography
                variant="caption"
                align="center"
                color="text.secondary"
                sx={{ display: 'block', mt: 1 }}
              >
                <strong>Admin:</strong> admin / admin123
              </Typography>
            </Box>
          </Paper>
        </motion.div>

        {/* Footer */}
        <Typography
          variant="body2"
          align="center"
          sx={{ mt: 4, color: 'white' }}
        >
          © {new Date().getFullYear()} Luxe Beauté Management - Tous droits réservés
        </Typography>
      </Container>
    </Box>
  );
}