// frontend\src\components\layout\Footer.jsx
import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  IconButton,
  Divider,
  useTheme,
} from '@mui/material';
import {
  Facebook,
  Instagram,
  Twitter,
  LinkedIn,
  Email,
  Phone,
  LocationOn,
} from '@mui/icons-material';
import { APP_CONFIG, THEME_COLORS } from '../../constants/config';

const Footer = () => {
  const theme = useTheme();
  const currentYear = new Date().getFullYear();

  const companyInfo = {
    name: APP_CONFIG.NAME,
    address: "ATT Bougou en face de 320 logement",
    phone: "+223 78 20 28 08",
    email: "boubacarkebe663@gmail.com"
  };

  const quickLinks = [
    { label: 'Tableau de bord', path: '/' },
    { label: 'Produits', path: '/products' },
    { label: 'Ventes', path: '/sales' },
    { label: 'Clients', path: '/clients' },
    { label: 'Stock', path: '/stock' },
    { label: 'Comptabilité', path: '/accounting' },
  ];

  const resources = [
    { label: 'Documentation', path: '/docs' },
    { label: 'Support technique', path: '/support' },
    { label: 'FAQ', path: '/faq' },
    { label: 'Blog', path: '/blog' },
    { label: 'Formations', path: '/training' },
    { label: 'API', path: 'http://127.0.0.1:8000/docs#/' },
  ];

  const legalLinks = [
    { label: 'Mentions légales', path: '/legal' },
    { label: 'Politique de confidentialité', path: '/privacy' },
    { label: 'Conditions générales', path: '/terms' },
    { label: 'Cookies', path: '/cookies' },
  ];

  const socialLinks = [
    { icon: <Instagram />, label: 'Instagram', url: 'https://instagram.com' },
    { icon: <Facebook />, label: 'Facebook', url: 'https://facebook.com' },
    { icon: <Twitter />, label: 'Twitter', url: 'https://twitter.com' },
    { icon: <LinkedIn />, label: 'LinkedIn', url: 'https://linkedin.com' },
  ];

  return (
    <Box
      component="footer"
      sx={{
        background: `linear-gradient(135deg, ${THEME_COLORS.BACKGROUND} 0%, #FFFFFF 100%)`,
        borderTop: `1px solid ${theme.palette.divider}`,
        mt: 'auto',
        py: 6,
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  mb: 2,
                  background: `linear-gradient(45deg, ${THEME_COLORS.PRIMARY} 30%, ${THEME_COLORS.SECONDARY} 90%)`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                💄 {companyInfo.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Système complet de gestion pour institut luxe beauté CHEZ PRINCE GARBA. 
                Optimisez vos ventes, gérez votre stock et offrez une expérience 
                exceptionnelle à vos clients.
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn sx={{ color: THEME_COLORS.PRIMARY, fontSize: 20 }} />
                <Typography variant="body2" color="text.secondary">
                  {companyInfo.address}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Phone sx={{ color: THEME_COLORS.PRIMARY, fontSize: 20 }} />
                <Typography variant="body2" color="text.secondary">
                  {companyInfo.phone}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Email sx={{ color: THEME_COLORS.PRIMARY, fontSize: 20 }} />
                <Typography variant="body2" color="text.secondary">
                  {companyInfo.email}
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Quick Links */}
          <Grid item xs={6} md={2}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Navigation
            </Typography>
            <Box component="nav">
              {quickLinks.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  color="text.secondary"
                  underline="hover"
                  sx={{
                    display: 'block',
                    mb: 1,
                    transition: 'all 0.2s',
                    '&:hover': {
                      color: THEME_COLORS.PRIMARY,
                      transform: 'translateX(4px)',
                    },
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Box>
          </Grid>

          {/* Resources */}
          <Grid item xs={6} md={2}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Ressources
            </Typography>
            <Box component="nav">
              {resources.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  color="text.secondary"
                  underline="hover"
                  sx={{
                    display: 'block',
                    mb: 1,
                    transition: 'all 0.2s',
                    '&:hover': {
                      color: THEME_COLORS.PRIMARY,
                      transform: 'translateX(4px)',
                    },
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Box>
          </Grid>

          {/* Legal & Social */}
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Légal
            </Typography>
            <Box component="nav" sx={{ mb: 4 }}>
              {legalLinks.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  color="text.secondary"
                  underline="hover"
                  sx={{
                    display: 'inline-block',
                    mr: 2,
                    mb: 1,
                    fontSize: '0.875rem',
                    transition: 'all 0.2s',
                    '&:hover': {
                      color: THEME_COLORS.PRIMARY,
                    },
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </Box>

            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Suivez-nous
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  aria-label={social.label}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    bgcolor: alpha(THEME_COLORS.PRIMARY, 0.1),
                    color: THEME_COLORS.PRIMARY,
                    '&:hover': {
                      bgcolor: THEME_COLORS.PRIMARY,
                      color: 'white',
                      transform: 'translateY(-2px)',
                      boxShadow: `0 4px 12px ${alpha(THEME_COLORS.PRIMARY, 0.3)}`,
                    },
                    transition: 'all 0.3s',
                  }}
                >
                  {social.icon}
                </IconButton>
              ))}
            </Box>

            <Box sx={{ mt: 4, p: 2, bgcolor: alpha(THEME_COLORS.PRIMARY, 0.05), borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary" paragraph>
                📧 Abonnez-vous à notre newsletter
              </Typography>
              <Box component="form" sx={{ display: 'flex', gap: 1 }}>
                <input
                  type="email"
                  placeholder="Votre email"
                  style={{
                    flexGrow: 1,
                    padding: '8px 12px',
                    border: `1px solid ${theme.palette.divider}`,
                    borderRadius: theme.shape.borderRadius,
                    fontSize: '0.875rem',
                  }}
                />
                <button
                  type="submit"
                  style={{
                    padding: '8px 16px',
                    background: `linear-gradient(135deg, ${THEME_COLORS.PRIMARY} 0%, ${THEME_COLORS.SECONDARY} 100%)`,
                    color: 'white',
                    border: 'none',
                    borderRadius: theme.shape.borderRadius,
                    cursor: 'pointer',
                    fontWeight: 600,
                    transition: 'all 0.3s',
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 4px 12px rgba(138, 43, 226, 0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = 'none';
                  }}
                >
                  S'abonner
                </button>
              </Box>
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {currentYear} {companyInfo.name}. Tous droits réservés.
            <br />
            Version {APP_CONFIG.VERSION}
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <img
              src="https://img.shields.io/badge/Secure-Payment-green"
              alt="Secure Payment"
              style={{ height: 20 }}
            />
            <img
              src="https://img.shields.io/badge/GDPR-Compliant-blue"
              alt="GDPR Compliant"
              style={{ height: 20 }}
            />
            <img
              src="https://img.shields.io/badge/SSL-Encrypted-orange"
              alt="SSL Encrypted"
              style={{ height: 20 }}
            />
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

// Helper function for alpha colors
function alpha(color, opacity) {
  return color + Math.round(opacity * 255).toString(16).padStart(2, '0');
}

export default Footer;