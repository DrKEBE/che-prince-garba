// frontend\src\components\clients\ClientCard.jsx
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Avatar,
  Chip,
  Button,
  IconButton,
  Stack,
  Box,
  Tooltip,
  Divider,
  Badge,
  LinearProgress,
  useTheme
} from '@mui/material';
import {
  Person as PersonIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Star as StarIcon,
  ShoppingBag as ShoppingIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Message as MessageIcon,
  History as HistoryIcon,
  Loyalty as LoyaltyIcon,
  Female as FemaleIcon,
  Male as MaleIcon,
  Cake as CakeIcon
} from '@mui/icons-material';
import { formatCurrency, formatDate } from '../../utils/formatters';
import { CLIENT_TYPES } from '../../constants/config';
import { clientService } from '../../services/clients';

const ClientCard = ({ client, onEdit, onDelete, onViewHistory, onMessage }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(client);

  // Détermine la couleur du type de client
  const getClientTypeColor = (type) => {
    switch (type) {
      case 'VIP': return 'error';
      case 'FIDELITE': return 'warning';
      case 'WHOLESALER': return 'info';
      default: return 'default';
    }
  };

  // Icône de genre
  const getGenderIcon = () => {
    switch (client.gender) {
      case 'F': return <FemaleIcon sx={{ fontSize: 18 }} />;
      case 'M': return <MaleIcon sx={{ fontSize: 18 }} />;
      default: return null;
    }
  };

  // Calcul de l'âge
  const calculateAge = () => {
    if (!client.birth_date) return null;
    const birthDate = new Date(client.birth_date);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  // Niveau de fidélité basé sur les achats
  const getLoyaltyLevel = () => {
    const total = client.total_purchases || 0;
    if (total > 500000) return { level: 'Platinum', color: '#E5E4E2' };
    if (total > 200000) return { level: 'Gold', color: '#FFD700' };
    if (total > 50000) return { level: 'Silver', color: '#C0C0C0' };
    return { level: 'Bronze', color: '#CD7F32' };
  };

  // Avatar avec initiales ou photo
  const getAvatarContent = () => {
    if (client.avatar) {
      return <Avatar src={client.avatar} sx={{ bgcolor: theme.palette.primary.light }} />;
    }
    const initials = client.full_name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
    return (
      <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
        {initials}
      </Avatar>
    );
  };

  const loyaltyLevel = getLoyaltyLevel();
  const age = calculateAge();

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        background: 'linear-gradient(145deg, #ffffff 0%, #f8f7ff 100%)',
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 3,
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: theme.shadows[8],
          borderColor: theme.palette.primary.light,
        }
      }}
    >
      {/* En-tête avec dégradé */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`,
          p: 2,
          color: 'white',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Éléments décoratifs */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 100,
            height: 100,
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.1)',
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            top: 30,
            right: 30,
            width: 60,
            height: 60,
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.05)',
          }}
        />

        <Stack direction="row" spacing={2} alignItems="center">
          <Badge
            overlap="circular"
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            badgeContent={
              client.client_type === 'VIP' ? (
                <StarIcon sx={{ fontSize: 20, color: '#FFD700' }} />
              ) : null
            }
          >
            {getAvatarContent()}
          </Badge>
          <Box flex={1}>
            <Typography variant="h6" fontWeight={600} noWrap>
              {client.full_name}
            </Typography>
            <Stack direction="row" spacing={1} alignItems="center">
              <Chip
                label={CLIENT_TYPES[client.client_type] || client.client_type}
                size="small"
                color={getClientTypeColor(client.client_type)}
                sx={{
                  color: 'white',
                  fontWeight: 600,
                  fontSize: '0.7rem',
                  height: 20
                }}
              />
              {loyaltyLevel && (
                <Chip
                  label={loyaltyLevel.level}
                  size="small"
                  sx={{
                    bgcolor: loyaltyLevel.color,
                    color: loyaltyLevel.level === 'Gold' ? '#000' : '#fff',
                    fontWeight: 600,
                    fontSize: '0.7rem',
                    height: 20
                  }}
                />
              )}
            </Stack>
          </Box>
        </Stack>
      </Box>

      <CardContent sx={{ flex: 1, p: 2.5 }}>
        {/* Informations de contact */}
        <Stack spacing={1.5} mb={2}>
          <Stack direction="row" spacing={1} alignItems="center">
            <PhoneIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
            <Typography variant="body2" color="text.secondary">
              {client.phone}
            </Typography>
          </Stack>
          
          {client.email && (
            <Stack direction="row" spacing={1} alignItems="center">
              <EmailIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
              <Typography variant="body2" color="text.secondary">
                {client.email}
              </Typography>
            </Stack>
          )}

          <Stack direction="row" spacing={1} alignItems="center">
            <LocationIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
            <Typography variant="body2" color="text.secondary" noWrap>
              {client.address}
            </Typography>
          </Stack>

          {/* Informations démographiques */}
          {(client.gender || client.birth_date) && (
            <Stack direction="row" spacing={2} mt={1}>
              {client.gender && (
                <Tooltip title="Genre">
                  <Chip
                    icon={getGenderIcon()}
                    label={client.gender === 'F' ? 'Femme' : 'Homme'}
                    size="small"
                    variant="outlined"
                  />
                </Tooltip>
              )}
              {age && (
                <Tooltip title="Âge">
                  <Chip
                    icon={<CakeIcon sx={{ fontSize: 16 }} />}
                    label={`${age} ans`}
                    size="small"
                    variant="outlined"
                  />
                </Tooltip>
              )}
            </Stack>
          )}
        </Stack>

        <Divider sx={{ my: 2 }} />

        {/* Statistiques */}
        <Stack spacing={2}>
          <Box>
            <Stack direction="row" justifyContent="space-between" mb={0.5}>
              <Typography variant="body2" fontWeight={600}>
                Total Achats
              </Typography>
              <Typography variant="body2" fontWeight={600} color="primary">
                {formatCurrency(client.total_purchases)}
              </Typography>
            </Stack>
            <LinearProgress
              variant="determinate"
              value={Math.min((client.total_purchases || 0) / 1000000 * 100, 100)}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: theme.palette.grey[200],
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #8A2BE2 0%, #FF4081 100%)',
                  borderRadius: 3,
                }
              }}
            />
          </Box>

          <Stack spacing={1}>
            <Stack direction="row" justifyContent="space-between">
              <Stack direction="row" spacing={1} alignItems="center">
                <LoyaltyIcon sx={{ fontSize: 18, color: '#FFD700' }} />
                <Typography variant="body2">Points fidélité</Typography>
              </Stack>
              <Typography variant="body2" fontWeight={600}>
                {client.loyalty_points || 0} pts
              </Typography>
            </Stack>

            <Stack direction="row" justifyContent="space-between">
              <Stack direction="row" spacing={1} alignItems="center">
                <ShoppingIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                <Typography variant="body2">Transactions</Typography>
              </Stack>
              <Typography variant="body2" fontWeight={600}>
                {client.total_transactions || 0}
              </Typography>
            </Stack>

            {client.last_purchase && (
              <Stack direction="row" justifyContent="space-between">
                <Stack direction="row" spacing={1} alignItems="center">
                  <CalendarIcon sx={{ fontSize: 18, color: theme.palette.text.secondary }} />
                  <Typography variant="body2">Dernier achat</Typography>
                </Stack>
                <Typography variant="body2" fontWeight={600}>
                  {formatDate(client.last_purchase, 'DD/MM/YYYY')}
                </Typography>
              </Stack>
            )}
          </Stack>
        </Stack>
      </CardContent>

      {/* Actions */}
      <CardActions sx={{ p: 2, pt: 1, borderTop: `1px solid ${theme.palette.divider}` }}>
        <Stack direction="row" spacing={1} width="100%" justifyContent="space-between">
          <Tooltip title="Modifier">
            <IconButton
              size="small"
              onClick={() => onEdit?.(client)}
              sx={{
                bgcolor: theme.palette.action.hover,
                '&:hover': { bgcolor: theme.palette.primary.light, color: 'white' }
              }}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Historique d'achat">
            <IconButton
              size="small"
              onClick={() => onViewHistory?.(client)}
              sx={{
                bgcolor: theme.palette.action.hover,
                '&:hover': { bgcolor: theme.palette.info.light, color: 'white' }
              }}
            >
              <HistoryIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Envoyer message">
            <IconButton
              size="small"
              onClick={() => onMessage?.(client)}
              sx={{
                bgcolor: theme.palette.action.hover,
                '&:hover': { bgcolor: theme.palette.success.light, color: 'white' }
              }}
            >
              <MessageIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Supprimer">
            <IconButton
              size="small"
              onClick={() => onDelete?.(client)}
              sx={{
                bgcolor: theme.palette.action.hover,
                '&:hover': { bgcolor: theme.palette.error.light, color: 'white' }
              }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </CardActions>
    </Card>
  );
};

// PropTypes
ClientCard.propTypes = {
  client: PropTypes.shape({
    id: PropTypes.string.isRequired,
    full_name: PropTypes.string.isRequired,
    phone: PropTypes.string.isRequired,
    email: PropTypes.string,
    address: PropTypes.string,
    city: PropTypes.string,
    client_type: PropTypes.string,
    loyalty_points: PropTypes.number,
    total_purchases: PropTypes.number,
    total_transactions: PropTypes.number,
    last_purchase: PropTypes.string,
    birth_date: PropTypes.string,
    gender: PropTypes.string,
    preferences: PropTypes.object,
    avatar: PropTypes.string,
  }).isRequired,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onViewHistory: PropTypes.func,
  onMessage: PropTypes.func,
};

export default ClientCard;