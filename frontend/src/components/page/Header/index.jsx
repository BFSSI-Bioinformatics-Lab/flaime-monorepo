import React, { useEffect, useState } from 'react'
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import PageContainer from '../PageContainer';
import { logout } from '../../../api/services/authService';

const Header = () => {
    const [anchorEl, setAnchorEl] = React.useState(null);
    const [anchorEl2, setAnchorEl2] = React.useState(null);
    const [anchorEl3, setAnchorEl3] = React.useState(null);
    const [anchorElUser, setAnchorElUser] = React.useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userData, setUserData] = useState(null);

    // Check authentication status on mount and when 'auth-change' event is triggered
    const checkAuthStatus = () => {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        if (token) {
            setIsAuthenticated(true);
            if (user) {
                setUserData(JSON.parse(user));
            }
        } else {
            setIsAuthenticated(false);
            setUserData(null);
        }
    };

    // Initial check and event listener setup
    useEffect(() => {
        checkAuthStatus();

        window.addEventListener('auth-change', checkAuthStatus);

        return () => {
            window.removeEventListener('auth-change', checkAuthStatus);
        };
    }, []);

    const handleClose = () => {
        setAnchorEl(null);
        setAnchorEl2(null);
        setAnchorEl3(null);
        setAnchorElUser(null);
    };

    let navigate = useNavigate();
    const routeHome = () => {
        let path = '/';
        navigate(path);
    }

    const handleLogout = () => {
        logout();
        handleClose();
        navigate('/login');
    };

    return (
        <Box sx={{ flexGrow: 1, background: '#732C02' }}>
            <AppBar position="static">
                <PageContainer>
                    <Toolbar sx={{ paddingLeft: 0, paddingRight: 0 }} disableGutters>
                        <Typography variant="h6" component="div"
                            sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={routeHome}>
                            FLAIME
                        </Typography>

                        {/* Menu Buttons */}
                        <Button
                            id="tools"
                            aria-haspopup="true"
                            onClick={e => setAnchorEl(e.currentTarget)}
                            color="inherit"
                        >
                            Tools
                        </Button>
                        <Menu
                            id="tools-menu"
                            anchorEl={anchorEl}
                            open={Boolean(anchorEl)}
                            onClose={handleClose}
                            MenuListProps={{
                                "aria-labelledby": "tools-button"
                            }}
                            PaperProps={{
                                sx: {
                                    bgcolor: 'rgba(115, 44, 2,0.9)',
                                    color: 'white',
                                    "& .MuiMenuItem-root:hover": {
                                        backgroundColor: "rgba(217, 150, 91,0.4)"
                                    },
                                }
                            }}
                        >
                            <MenuItem component={Link} to='/tools/product-browser'
                                onClick={handleClose}>Product Browser</MenuItem>
                            <MenuItem component={Link} to='/tools/product-finder'
                                onClick={handleClose}>Product Finder</MenuItem>
                            <MenuItem component={Link} to='/tools/advanced-search'
                                onClick={handleClose}>Advanced Search</MenuItem>
                            {userData && userData.is_staff && (
                                <MenuItem
                                    component={Link}
                                    to='/tools/category-verification-setup'
                                    onClick={handleClose}
                                >
                                    Category Verification
                                </MenuItem>
                            )}
                        </Menu>

                        <Button
                            id="reports"
                            aria-haspopup="true"
                            onClick={e => setAnchorEl2(e.currentTarget)}
                            color="inherit"
                        >
                            Reports
                        </Button>
                        <Menu
                            id="reports-menu"
                            anchorEl={anchorEl2}
                            open={Boolean(anchorEl2)}
                            onClose={handleClose}
                            MenuListProps={{
                                "aria-labelledby": "reports-button"
                            }}
                            PaperProps={{
                                sx: {
                                    bgcolor: 'rgba(115, 44, 2,0.9)',
                                    color: 'white',
                                    "& .MuiMenuItem-root:hover": {
                                        backgroundColor: "rgba(217, 150, 91,0.4)"
                                    },
                                }
                            }}
                        >
                            <MenuItem component={Link} to='/reports/collection-stats'
                                onClick={handleClose}>Collection Statistics</MenuItem>
                        </Menu>

                        <Button
                            id="data"
                            aria-haspopup="true"
                            onClick={e => setAnchorEl3(e.currentTarget)}
                            color="inherit"
                        >
                            Data
                        </Button>
                        <Menu
                            id="data-menu"
                            anchorEl={anchorEl3}
                            open={Boolean(anchorEl3)}
                            onClose={handleClose}
                            MenuListProps={{
                                "aria-labelledby": "data-button"
                            }}
                            PaperProps={{
                                sx: {
                                    bgcolor: 'rgba(115, 44, 2,0.9)',
                                    color: 'white',
                                    "& .MuiMenuItem-root:hover": {
                                        backgroundColor: "rgba(217, 150, 91,0.4)"
                                    },
                                }
                            }}
                        >
                            <MenuItem component={Link} to='/data/quality'
                                onClick={handleClose}>Quality</MenuItem>
                            <MenuItem component={Link} to='/data/download'
                                onClick={handleClose}>Download</MenuItem>
                        </Menu>

                        <Button
                            id="about"
                            aria-haspopup="true"
                            color="inherit"
                            sx={{ mr: 2 }}
                            component={Link} to="/about"
                        >
                            About
                        </Button>

                        {/* Authentication Button */}
                        {isAuthenticated ? (
                            <>
                                <Button
                                    id="user-menu"
                                    aria-haspopup="true"
                                    onClick={e => setAnchorElUser(e.currentTarget)}
                                    color="inherit"
                                >
                                    {userData ? userData.email : 'Account'}
                                </Button>
                                <Menu
                                    id="user-menu-dropdown"
                                    anchorEl={anchorElUser}
                                    open={Boolean(anchorElUser)}
                                    onClose={handleClose}
                                    MenuListProps={{
                                        "aria-labelledby": "user-menu-button"
                                    }}
                                    PaperProps={{
                                        sx: {
                                            bgcolor: 'rgba(115, 44, 2,0.9)',
                                            color: 'white',
                                            "& .MuiMenuItem-root:hover": {
                                                backgroundColor: "rgba(217, 150, 91,0.4)"
                                            },
                                        }
                                    }}
                                >
                                    {userData && userData.is_staff && (
                                        <MenuItem
                                            component={Link}
                                            to="/admin/"
                                            onClick={handleClose}
                                        >
                                            Admin
                                        </MenuItem>
                                    )}
                                    <MenuItem onClick={handleLogout}>Logout</MenuItem>
                                </Menu>
                            </>
                        ) : (
                            <Button
                                color="inherit"
                                component={Link}
                                to="/login"
                            >
                                Login
                            </Button>
                        )}
                    </Toolbar>
                </PageContainer>
            </AppBar>
        </Box>
    )
}

export default Header