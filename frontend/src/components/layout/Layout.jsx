// frontend\src\components\layout\Layout.jsx
import React from 'react';
import { Outlet } from 'react-router-dom'; // AJOUTEZ CE IMPORT
import { Box, CssBaseline } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';
import { useSidebar } from "../../context/AppContext";

const Layout = () => { // RETIREZ { children }
  const theme = useTheme();
  const { open: sidebarOpen } = useSidebar();

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      <Navbar />
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: '64px',
          transition: theme.transitions.create(['margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          width: `calc(100% - ${sidebarOpen ? 240 : 0}px)`,
          minHeight: 'calc(100vh - 64px)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ flexGrow: 1 }}>
          <Outlet /> {/* REMPLACEZ children par Outlet */}
        </Box>
        <Footer />
      </Box>
    </Box>
  );
};

export default Layout;