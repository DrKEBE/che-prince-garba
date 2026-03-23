import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  Card,
  CardContent,
  Grid,
  IconButton,
  Tooltip,
  Chip,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  Stack
} from '@mui/material';
import {
  Add,
  Refresh,
  Download,
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Receipt,
  Delete,
  Edit,
  Visibility,
  Assessment,
  Timeline,
  PieChart,
  AttachMoney,
  MoneyOff,
  SyncAlt,
  Print
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import frLocale from 'date-fns/locale/fr';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { motion } from 'framer-motion';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';

import { accountingService } from '../services/accounting';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import DataTable from '../components/common/DataTable';
import StatsCard from '../components/dashboard/StatsCard';
import ChartCard from '../components/dashboard/ChartCard';
import ConfirmationModal from '../components/common/ConfirmationModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { formatCurrency, formatDate, formatPercentage } from '../utils/formatters';

import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';

// ==================== CONSTANTES ====================
const EXPENSE_CATEGORIES = [
  'Loyer', 'Salaires', 'Électricité', 'Eau', 'Téléphone/Internet',
  'Marketing', 'Fournitures', 'Entretien', 'Transport', 'Assurance',
  'Impôts', 'Frais bancaires', 'Formation', 'Équipement', 'Autres'
];

const PAYMENT_METHODS = {
  CASH: 'Espèces',
  Saraly: 'Saraly',
  CARD: 'Carte bancaire',
  BANK_TRANSFER: 'Virement',
  CHECK: 'Chèque',
  CREDIT: 'Crédit',
  MOBILE_MONEY: 'Mobile Money'
};

const REPORT_TYPES = [
  { value: 'income_statement', label: 'Compte de résultat' },
  { value: 'balance_sheet', label: 'Bilan comptable' },
  { value: 'sales_summary', label: 'Résumé des ventes' }
];

// ==================== COMPOSANT PRINCIPAL ====================
export default function Accounting() {
  const { user, isAdmin, isManager } = useAuth();
  const queryClient = useQueryClient();

  // États des onglets
  const [tabIndex, setTabIndex] = useState(0);

  // États des filtres de dates
  const today = new Date();
  const [startDate, setStartDate] = useState(format(startOfMonth(today), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(endOfMonth(today), 'yyyy-MM-dd'));

  // États pour les modales
  const [expenseModalOpen, setExpenseModalOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [expenseToDelete, setExpenseToDelete] = useState(null);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [selectedReportType, setSelectedReportType] = useState('income_statement');
  const [reportData, setReportData] = useState(null);

  // ==================== REQUÊTES API ====================
  // Métriques financières
  const {
    data: metrics,
    isLoading: metricsLoading,
    refetch: refetchMetrics
  } = useQuery(
    'financial-metrics',
    () => accountingService.getFinancialMetrics(),
    { refetchInterval: 5 * 60 * 1000 } // toutes les 5 minutes
  );

  // Liste des dépenses
  const {
    data: expenses,
    isLoading: expensesLoading,
    refetch: refetchExpenses
  } = useQuery(
    ['expenses', { start_date: startDate, end_date: endDate }],
    () => accountingService.getExpenses({
      start_date: startDate,
      end_date: endDate,
      limit: 500
    })
  );

  // Analyse de profit
  const {
    data: profitAnalysis,
    isLoading: profitLoading,
    refetch: refetchProfit
  } = useQuery(
    ['profit-analysis', startDate, endDate],
    () => accountingService.getProfitAnalysis(startDate, endDate),
    { enabled: tabIndex === 2 } // ne charger que si onglet actif
  );

  // Flux de trésorerie
  const {
    data: cashFlow,
    isLoading: cashFlowLoading,
    refetch: refetchCashFlow
  } = useQuery(
    ['cash-flow', startDate, endDate],
    () => accountingService.getCashFlow(startDate, endDate),
    { enabled: tabIndex === 3 }
  );

  // Réconciliation
  const {
    data: reconciliation,
    isLoading: reconciliationLoading,
    refetch: refetchReconciliation
  } = useQuery(
    ['reconciliation', startDate, endDate],
    () => accountingService.reconcilePayments(startDate, endDate),
    { enabled: tabIndex === 5 }
  );

  // Mutations
  const deleteExpenseMutation = useMutation(
    (id) => accountingService.deleteExpense(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('expenses');
        queryClient.invalidateQueries('financial-metrics');
        setDeleteModalOpen(false);
        setExpenseToDelete(null);
      }
    }
  );

  // ==================== GESTIONNAIRES D'ÉVÉNEMENTS ====================
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  const handleDateChange = (type, value) => {
    if (value) {
      const formatted = format(value, 'yyyy-MM-dd');
      if (type === 'start') setStartDate(formatted);
      else setEndDate(formatted);
    }
  };

  const handleOpenExpenseModal = (expense = null) => {
    setSelectedExpense(expense);
    setExpenseModalOpen(true);
  };

  const handleCloseExpenseModal = (refetch = false) => {
    setExpenseModalOpen(false);
    setSelectedExpense(null);
    if (refetch) {
      refetchExpenses();
      refetchMetrics();
    }
  };

  const handleDeleteClick = (expense) => {
    setExpenseToDelete(expense);
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = () => {
    if (expenseToDelete) {
      deleteExpenseMutation.mutate(expenseToDelete.id);
    }
  };

  const handleGenerateReport = async () => {
    try {
      const data = await accountingService.getFinancialReport(
        selectedReportType,
        startDate,
        endDate
      );
      setReportData(data);
      setReportModalOpen(true);
    } catch (error) {
      console.error('Erreur lors de la génération du rapport', error);
    }
  };

  const handleExportExpenses = () => {
    // Implémentation simplifiée : télécharger en CSV
    if (!expenses) return;
    const headers = ['Date', 'Catégorie', 'Description', 'Montant', 'Méthode', 'Bénéficiaire'];
    const rows = expenses.map(e => [
      formatDate(e.expense_date, 'yyyy-MM-dd'),
      e.category,
      e.description,
      e.amount,
      PAYMENT_METHODS[e.payment_method] || e.payment_method,
      e.recipient || ''
    ]);
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `depenses_${startDate}_${endDate}.csv`;
    link.click();
  };

  // ==================== VÉRIFICATION DES PERMISSIONS ====================
  if (!isAdmin && !isManager) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Vous n'avez pas les permissions nécessaires pour accéder à cette page.
        </Alert>
      </Box>
    );
  }

  // ==================== RENDU ====================
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} locale={frLocale}>
      <Box sx={{ p: 3 }}>
        {/* En-tête */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Comptabilité
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Gérez vos finances, dépenses et rapports
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => {
                refetchMetrics();
                refetchExpenses();
                refetchProfit();
                refetchCashFlow();
                refetchReconciliation();
              }}
            >
              Actualiser
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => handleOpenExpenseModal()}
            >
              Nouvelle dépense
            </Button>
          </Box>
        </Box>

        {/* Sélecteurs de dates */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <DatePicker
                label="Date de début"
                value={new Date(startDate)}
                onChange={(date) => handleDateChange('start', date)}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <DatePicker
                label="Date de fin"
                value={new Date(endDate)}
                onChange={(date) => handleDateChange('end', date)}
                renderInput={(params) => <TextField {...params} fullWidth size="small" />}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                variant="outlined"
                onClick={() => {
                  setStartDate(format(startOfMonth(today), 'yyyy-MM-dd'));
                  setEndDate(format(endOfMonth(today), 'yyyy-MM-dd'));
                }}
              >
                Ce mois-ci
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Onglets */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabIndex} onChange={handleTabChange}>
            <Tab label="Tableau de bord" icon={<Assessment />} iconPosition="start" />
            <Tab label="Dépenses" icon={<Receipt />} iconPosition="start" />
            <Tab label="Analyse de profit" icon={<TrendingUp />} iconPosition="start" />
            <Tab label="Flux de trésorerie" icon={<Timeline />} iconPosition="start" />
            <Tab label="Rapports" icon={<PieChart />} iconPosition="start" />
            <Tab label="Réconciliation" icon={<SyncAlt />} iconPosition="start" />
          </Tabs>
        </Box>

        {/* Contenu dynamique selon onglet */}
        <motion.div
          key={tabIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Onglet 0 : Tableau de bord financier */}
          {tabIndex === 0 && (
            <DashboardTab
              metrics={metrics}
              loading={metricsLoading}
              onRefresh={refetchMetrics}
            />
          )}

          {/* Onglet 1 : Dépenses */}
          {tabIndex === 1 && (
            <ExpensesTab
              expenses={expenses}
              loading={expensesLoading}
              onEdit={handleOpenExpenseModal}
              onDelete={handleDeleteClick}
              onExport={handleExportExpenses}
              onRefresh={refetchExpenses}
            />
          )}

          {/* Onglet 2 : Analyse de profit */}
          {tabIndex === 2 && (
            <ProfitAnalysisTab
              data={profitAnalysis}
              loading={profitLoading}
              startDate={startDate}
              endDate={endDate}
            />
          )}

          {/* Onglet 3 : Flux de trésorerie */}
          {tabIndex === 3 && (
            <CashFlowTab
              data={cashFlow}
              loading={cashFlowLoading}
            />
          )}

          {/* Onglet 4 : Rapports */}
          {tabIndex === 4 && (
            <ReportsTab
              onGenerate={handleGenerateReport}
              selectedType={selectedReportType}
              setSelectedType={setSelectedReportType}
            />
          )}

          {/* Onglet 5 : Réconciliation */}
          {tabIndex === 5 && (
            <ReconciliationTab
              data={reconciliation}
              loading={reconciliationLoading}
            />
          )}
        </motion.div>

        {/* Modale de création/édition de dépense */}
        <ExpenseModal
          open={expenseModalOpen}
          onClose={handleCloseExpenseModal}
          expense={selectedExpense}
        />

        {/* Modale de confirmation de suppression */}
        <ConfirmationModal
          open={deleteModalOpen}
          onClose={() => setDeleteModalOpen(false)}
          onConfirm={handleConfirmDelete}
          title="Supprimer la dépense"
          message={`Êtes-vous sûr de vouloir supprimer la dépense "${expenseToDelete?.description}" ? Cette action est irréversible.`}
          severity="error"
          loading={deleteExpenseMutation.isLoading}
        />

        {/* Modale d'affichage du rapport */}
        <ReportModal
          open={reportModalOpen}
          onClose={() => setReportModalOpen(false)}
          data={reportData}
          type={selectedReportType}
        />
      </Box>
    </LocalizationProvider>
  );
}

// ==================== SOUS-COMPOSANTS ====================

// ----- Onglet Tableau de bord -----
function DashboardTab({ metrics, loading, onRefresh }) {
  if (loading) return <LoadingSpinner />;

  const daily = metrics?.daily || {};
  const monthly = metrics?.monthly || {};
  const yearly = metrics?.yearly || {};
  const outstanding = metrics?.outstanding || {};

  return (
    <Box>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <StatsCard
            title="Aujourd'hui"
            value={formatCurrency(daily.revenue)}
            icon={<AttachMoney />}
            color="primary"
            subtitle={`Dépenses: ${formatCurrency(daily.expenses)}`}
            progress={(daily.profit / daily.revenue) * 100}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatsCard
            title="Ce mois"
            value={formatCurrency(monthly.revenue)}
            icon={<TrendingUp />}
            color="success"
            subtitle={`Profit: ${formatCurrency(monthly.profit)}`}
            trend={(monthly.profit / monthly.revenue) * 100}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatsCard
            title="Cette année"
            value={formatCurrency(yearly.revenue)}
            icon={<Assessment />}
            color="info"
            subtitle={`Dépenses: ${formatCurrency(yearly.expenses)}`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ChartCard title="Répartition mensuelle">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                { name: 'Revenus', value: monthly.revenue },
                { name: 'Dépenses', value: monthly.expenses },
                { name: 'Profit', value: monthly.profit }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis tickFormatter={(v) => formatCurrency(v, '')} />
                <RechartsTooltip formatter={(v) => formatCurrency(v)} />
                <Bar dataKey="value" fill="#8A2BE2" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <ChartCard title="En cours">
            <Box sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography>Dettes fournisseurs</Typography>
                  <Typography fontWeight="bold">{formatCurrency(outstanding.supplier_debts)}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography>Paiements en attente</Typography>
                  <Typography fontWeight="bold">{formatCurrency(outstanding.pending_payments)}</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography>Dépenses impayées</Typography>
                  <Typography fontWeight="bold">{formatCurrency(outstanding.pending_expenses)}</Typography>
                </Box>
                <Divider />
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="h6">Total</Typography>
                  <Typography variant="h6" color="error">{formatCurrency(outstanding.total)}</Typography>
                </Box>
              </Stack>
            </Box>
          </ChartCard>
        </Grid>
      </Grid>
    </Box>
  );
}

// ----- Onglet Dépenses -----
function ExpensesTab({ expenses, loading, onEdit, onDelete, onExport, onRefresh }) {
  const columns = [
    {
      field: 'date',
      headerName: 'Date',
      width: 100,
      renderCell: (params) => formatDate(params.row.expense_date, 'dd/MM/yyyy')
    },
    { field: 'category', headerName: 'Catégorie', width: 150 },
    { field: 'description', headerName: 'Description', flex: 1 },
    {
      field: 'amount',
      headerName: 'Montant',
      width: 120,
      renderCell: (params) => (
        <Typography fontWeight="bold" color="error.main">
          {formatCurrency(params.row.amount)}
        </Typography>
      )
    },
    {
      field: 'payment_method',
      headerName: 'Méthode',
      width: 120,
      renderCell: (params) => PAYMENT_METHODS[params.row.payment_method] || params.row.payment_method
    },
    { field: 'recipient', headerName: 'Bénéficiaire', width: 150 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Modifier">
            <IconButton size="small" onClick={() => onEdit(params.row)}>
              <Edit fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Supprimer">
            <IconButton size="small" color="error" onClick={() => onDelete(params.row)}>
              <Delete fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2, gap: 1 }}>
        <Button startIcon={<Download />} onClick={onExport} size="small">
          Exporter CSV
        </Button>
        <Button startIcon={<Refresh />} onClick={onRefresh} size="small">
          Rafraîchir
        </Button>
      </Box>
      <DataTable
        rows={expenses || []}
        columns={columns}
        loading={loading}
        getRowId={(row) => row.id}
        pageSize={10}
      />
    </Box>
  );
}

// ----- Onglet Analyse de profit -----
function ProfitAnalysisTab({ data, loading, startDate, endDate }) {
  if (loading) return <LoadingSpinner />;
  if (!data) return <Alert severity="info">Aucune donnée pour cette période</Alert>;

  // Calcul des marges en pourcentage
  const grossMargin = data.total_revenue > 0 
    ? (data.gross_profit / data.total_revenue) * 100 
    : 0;
  const netMargin = data.total_revenue > 0 
    ? (data.net_profit / data.total_revenue) * 100 
    : 0;

  const pieData = [
    { name: 'COGS', value: data.cogs },
    { name: 'Dépenses', value: data.total_expenses },
    { name: 'Profit net', value: data.net_profit }
  ];
  const COLORS = ['#fb9af6', '#ff4b3ead', '#b3ea1a'];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Résumé</Typography>
            <Stack spacing={2}>
              <Box display="flex" justifyContent="space-between">
                <Typography color="text.secondary">Revenu total</Typography>
                <Typography fontWeight="bold">{formatCurrency(data.total_revenue)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography color="text.secondary">COGS</Typography>
                <Typography color="warning.main">{formatCurrency(data.cogs)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography color="text.secondary">Dépenses</Typography>
                <Typography color="error.main">{formatCurrency(data.total_expenses)}</Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between">
                <Typography variant="subtitle1">Profit brut</Typography>
                <Typography variant="subtitle1" color="success.main">{formatCurrency(data.gross_profit)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="subtitle1">Profit net</Typography>
                <Typography variant="subtitle1" color="primary.main">{formatCurrency(data.net_profit)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Marge brute</Typography>
                <Chip label={formatPercentage(grossMargin)} color="success" size="small" />
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Marge nette</Typography>
                <Chip label={formatPercentage(netMargin)} color="info" size="small" />
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={8}>
        <ChartCard title="Répartition des coûts">
          <ResponsiveContainer width="100%" height={300}>
            <RePieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${formatPercentage(entry.value / data.total_revenue * 100)}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
              <RechartsTooltip formatter={(value) => formatCurrency(value)} />
            </RePieChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>
    </Grid>
  );
}

// ----- Onglet Flux de trésorerie -----
function CashFlowTab({ data, loading }) {
  if (loading) return <LoadingSpinner />;
  if (!data) return <Alert severity="info">Aucune donnée</Alert>;

  const chartData = data.daily_balance?.map(item => ({
    date: format(new Date(item.date), 'dd/MM'),
    incoming: item.incoming,
    outgoing: item.outgoing,
    balance: item.balance
  })) || [];

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ChartCard title="Évolution quotidienne">
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <RechartsTooltip formatter={(value) => formatCurrency(value)} />
              <Legend />
              <Area type="monotone" dataKey="incoming" stackId="1" stroke="#10B981" fill="#10B981" fillOpacity={0.3} name="Entrées" />
              <Area type="monotone" dataKey="outgoing" stackId="1" stroke="#EF4444" fill="#EF4444" fillOpacity={0.3} name="Sorties" />
              <Line type="monotone" dataKey="balance" stroke="#8A2BE2" strokeWidth={2} name="Solde" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">Total entrées</Typography>
            <Typography variant="h5" color="success.main">{formatCurrency(data.total_incoming)}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">Total sorties</Typography>
            <Typography variant="h5" color="error.main">{formatCurrency(data.total_outgoing)}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">Flux net</Typography>
            <Typography variant="h5" color={data.net_cash_flow >= 0 ? 'success.main' : 'error.main'}>
              {formatCurrency(data.net_cash_flow)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

// ----- Onglet Rapports -----
function ReportsTab({ onGenerate, selectedType, setSelectedType }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Générer un rapport financier</Typography>
        <Grid container spacing={3} alignItems="flex-end">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Type de rapport</InputLabel>
              <Select
                value={selectedType}
                label="Type de rapport"
                onChange={(e) => setSelectedType(e.target.value)}
              >
                {REPORT_TYPES.map(rt => (
                  <MenuItem key={rt.value} value={rt.value}>{rt.label}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              startIcon={<Assessment />}
              onClick={onGenerate}
              fullWidth
            >
              Générer
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}

// ----- Onglet Réconciliation -----
function ReconciliationTab({ data, loading }) {
  if (loading) return <LoadingSpinner />;
  if (!data) return <Alert severity="info">Aucune donnée de réconciliation</Alert>;

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Réconciliation des paiements</Typography>
            <Stack spacing={2}>
              <Box display="flex" justifyContent="space-between">
                <Typography>Total enregistré</Typography>
                <Typography fontWeight="bold">{formatCurrency(data.recorded_payments?.total_amount)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Ventes sur la période</Typography>
                <Typography fontWeight="bold">{formatCurrency(data.sales_in_period?.total_amount)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Dépenses sur la période</Typography>
                <Typography fontWeight="bold" color="error.main">{formatCurrency(data.expenses_in_period?.total_amount)}</Typography>
              </Box>
              <Divider />
              <Box display="flex" justifyContent="space-between">
                <Typography>Attendu</Typography>
                <Typography>{formatCurrency(data.reconciliation?.expected_total)}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Différence</Typography>
                <Typography color={data.reconciliation?.difference >= 0 ? 'success.main' : 'error.main'}>
                  {formatCurrency(data.reconciliation?.difference)}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography>Statut</Typography>
                <Chip
                  label={data.reconciliation?.is_reconciled ? 'Réconcilié' : 'Écart détecté'}
                  color={data.reconciliation?.is_reconciled ? 'success' : 'warning'}
                />
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>Détail des paiements</Typography>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              {data.recorded_payments?.details?.map(payment => (
                <Box key={payment.id} sx={{ py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="body2">
                    {formatDate(payment.date, 'dd/MM/yyyy')} - {PAYMENT_METHODS[payment.method] || payment.method}
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(payment.amount)}
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

// ----- Modale de création/édition de dépense -----
function ExpenseModal({ open, onClose, expense }) {
  const isEditing = !!expense;
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    amount: '',
    payment_method: 'CASH',
    expense_date: format(new Date(), 'yyyy-MM-dd'),
    recipient: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (expense) {
      setFormData({
        category: expense.category || '',
        description: expense.description || '',
        amount: expense.amount || '',
        payment_method: expense.payment_method || 'CASH',
        expense_date: expense.expense_date ? expense.expense_date.split('T')[0] : format(new Date(), 'yyyy-MM-dd'),
        recipient: expense.recipient || '',
        notes: expense.notes || ''
      });
    } else {
      setFormData({
        category: '',
        description: '',
        amount: '',
        payment_method: 'CASH',
        expense_date: format(new Date(), 'yyyy-MM-dd'),
        recipient: '',
        notes: ''
      });
    }
  }, [expense]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (isEditing) {
        await accountingService.updateExpense(expense.id, formData);
      } else {
        await accountingService.createExpense(formData);
      }
      onClose(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={() => onClose(false)} maxWidth="sm" fullWidth>
      <DialogTitle>{isEditing ? 'Modifier la dépense' : 'Nouvelle dépense'}</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Catégorie"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
              >
                {EXPENSE_CATEGORIES.map(cat => (
                  <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Montant (FCFA)"
                name="amount"
                type="number"
                value={formData.amount}
                onChange={handleChange}
                required
                InputProps={{ inputProps: { min: 0 } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Méthode de paiement"
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
              >
                {Object.entries(PAYMENT_METHODS).map(([key, label]) => (
                  <MenuItem key={key} value={key}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                name="expense_date"
                type="date"
                value={formData.expense_date}
                onChange={handleChange}
                required
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Bénéficiaire"
                name="recipient"
                value={formData.recipient}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                name="notes"
                multiline
                rows={2}
                value={formData.notes}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onClose(false)}>Annuler</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : (isEditing ? 'Mettre à jour' : 'Créer')}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

// ----- Modale d'affichage de rapport -----
function ReportModal({ open, onClose, data, type }) {
  if (!data) return null;

  const renderContent = () => {
    if (type === 'income_statement') {
      return (
        <Box>
          <Typography variant="h6" gutterBottom>Compte de résultat</Typography>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Période du {data.period?.start} au {data.period?.end}
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Stack spacing={2}>
            <Box display="flex" justifyContent="space-between">
              <Typography>Revenu total</Typography>
              <Typography fontWeight="bold">{formatCurrency(data.summary?.total_revenue)}</Typography>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography>COGS</Typography>
              <Typography color="warning.main">{formatCurrency(data.summary?.cogs)}</Typography>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography>Dépenses totales</Typography>
              <Typography color="error.main">{formatCurrency(data.summary?.total_expenses)}</Typography>
            </Box>
            <Divider />
            <Box display="flex" justifyContent="space-between">
              <Typography variant="subtitle1">Profit brut</Typography>
              <Typography variant="subtitle1" color="success.main">{formatCurrency(data.summary?.gross_profit)}</Typography>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="subtitle1">Profit net</Typography>
              <Typography variant="subtitle1" color="primary.main">{formatCurrency(data.summary?.net_profit)}</Typography>
            </Box>
          </Stack>

          <Typography variant="h6" sx={{ mt: 3 }}>Revenus par catégorie</Typography>
          {data.revenue_by_category?.map(item => (
            <Box key={item.category} display="flex" justifyContent="space-between" sx={{ mt: 1 }}>
              <Typography>{item.category}</Typography>
              <Typography>{formatCurrency(item.revenue)}</Typography>
            </Box>
          ))}

          <Typography variant="h6" sx={{ mt: 3 }}>Dépenses par catégorie</Typography>
          {data.expenses_by_category?.map(item => (
            <Box key={item.category} display="flex" justifyContent="space-between" sx={{ mt: 1 }}>
              <Typography>{item.category}</Typography>
              <Typography color="error.main">{formatCurrency(item.amount)}</Typography>
            </Box>
          ))}
        </Box>
      );
    }

    if (type === 'balance_sheet') {
      return (
        <Box>
          <Typography variant="h6" gutterBottom>Bilan comptable</Typography>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Au {data.as_of_date}
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle1" gutterBottom>Actifs</Typography>
          {Object.entries(data.assets?.current_assets || {}).map(([key, value]) => (
            <Box key={key} display="flex" justifyContent="space-between">
              <Typography textTransform="capitalize">{key}</Typography>
              <Typography>{formatCurrency(value)}</Typography>
            </Box>
          ))}
          <Box display="flex" justifyContent="space-between" sx={{ mt: 1, fontWeight: 'bold' }}>
            <Typography>Total actifs courants</Typography>
            <Typography>{formatCurrency(data.assets?.total_current_assets)}</Typography>
          </Box>

          <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>Passifs</Typography>
          {Object.entries(data.liabilities?.current_liabilities || {}).map(([key, value]) => (
            <Box key={key} display="flex" justifyContent="space-between">
              <Typography textTransform="capitalize">{key}</Typography>
              <Typography>{formatCurrency(value)}</Typography>
            </Box>
          ))}
          <Box display="flex" justifyContent="space-between" sx={{ mt: 1, fontWeight: 'bold' }}>
            <Typography>Total passifs courants</Typography>
            <Typography>{formatCurrency(data.liabilities?.total_current_liabilities)}</Typography>
          </Box>

          <Typography variant="subtitle1" sx={{ mt: 3 }} gutterBottom>Capitaux propres</Typography>
          {Object.entries(data.equity || {}).map(([key, value]) => (
            <Box key={key} display="flex" justifyContent="space-between">
              <Typography textTransform="capitalize">{key}</Typography>
              <Typography>{formatCurrency(value)}</Typography>
            </Box>
          ))}
          <Box display="flex" justifyContent="space-between" sx={{ mt: 1, fontWeight: 'bold' }}>
            <Typography>Total capitaux propres</Typography>
            <Typography>{formatCurrency(data.total_equity)}</Typography>
          </Box>
        </Box>
      );
    }

    return <pre>{JSON.stringify(data, null, 2)}</pre>;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Rapport financier</DialogTitle>
      <DialogContent dividers>
        {renderContent()}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fermer</Button>
        <Button startIcon={<Print />}>Imprimer</Button>
      </DialogActions>
    </Dialog>
  );
}