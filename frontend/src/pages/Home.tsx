import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Movie as MovieIcon, Search as SearchIcon, List as ListIcon } from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 8 }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to CineTrack
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph>
          Your personal movie and series tracking companion
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <SearchIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Search Content
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Find movies, series, and anime from IMDb's extensive database
              </Typography>
              <Button
                variant="contained"
                color="primary"
                onClick={() => navigate('/search')}
              >
                Start Searching
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <ListIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Track Progress
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Keep track of your watched episodes and movies
              </Typography>
              {isAuthenticated ? (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => navigate('/watchlist')}
                >
                  View Watchlist
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => navigate('/login')}
                >
                  Login to Track
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <MovieIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Get Started
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Create an account to start tracking your favorite content
              </Typography>
              {!isAuthenticated && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => navigate('/register')}
                >
                  Register Now
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home; 