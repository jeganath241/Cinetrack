import React, { useState, useCallback } from 'react';
import {
  Container,
  TextField,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { content, bucketList, watchlist } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useDebounce } from '../hooks/useDebounce';
import { Content, ContentType } from '../types/api';

// Common languages in TV shows and movies
const LANGUAGES = [
  { code: '', label: 'All Languages' },
  { code: 'english', label: 'English' },
  { code: 'japanese', label: 'Japanese' },
  { code: 'korean', label: 'Korean' },
  { code: 'spanish', label: 'Spanish' },
  { code: 'french', label: 'French' },
  { code: 'german', label: 'German' },
  { code: 'chinese', label: 'Chinese' },
  { code: 'hindi', label: 'Hindi' },
];

const Search: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [contentType, setContentType] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [loginDialogOpen, setLoginDialogOpen] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Create a debounced function to update debouncedQuery
  const debouncedSetQuery = useCallback(
    useDebounce((query: string) => {
      setDebouncedQuery(query);
    }, 500),
    []
  );

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setSearchQuery(query);
    debouncedSetQuery(query);
  };

  const { data: searchResults, isLoading, error } = useQuery(
    ['search', debouncedQuery, contentType, language],
    () => content.search(debouncedQuery, contentType, language),
    {
      enabled: debouncedQuery.length >= 2,
      keepPreviousData: true,
    }
  );

  const handleAddToWatchlist = async (contentId: number) => {
    if (!isAuthenticated) {
      setLoginDialogOpen(true);
      return;
    }

    try {
      await watchlist.add(contentId);
      alert('Successfully added to watchlist!');
    } catch (error: any) {
      console.error('Failed to add to watchlist:', error);
      alert(error.response?.data?.detail || 'Failed to add to watchlist. Please try again.');
    }
  };

  const handleAddToBucketList = async (contentId: number) => {
    if (!isAuthenticated) {
      setLoginDialogOpen(true);
      return;
    }

    try {
      await bucketList.add(contentId);
      alert('Successfully added to bucket list!');
    } catch (error: any) {
      console.error('Failed to add to bucket list:', error);
      alert(error.response?.data?.detail || 'Failed to add to bucket list. Please try again.');
    }
  };

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search movies, series, or anime"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Type at least 2 characters to search..."
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={contentType}
                label="Content Type"
                onChange={(e) => setContentType(e.target.value)}
              >
                <MenuItem value="">All Types</MenuItem>
                <MenuItem value="movie">Movies</MenuItem>
                <MenuItem value="series">Series</MenuItem>
                <MenuItem value="anime">Anime</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={language}
                label="Language"
                onChange={(e) => setLanguage(e.target.value)}
              >
                {LANGUAGES.map((lang) => (
                  <MenuItem key={lang.code} value={lang.code}>
                    {lang.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Failed to load search results. Please try again.
        </Alert>
      )}

      {isLoading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : debouncedQuery.length < 2 ? (
        <Box textAlign="center" my={4}>
          <Typography color="text.secondary">
            Enter at least 2 characters to start searching...
          </Typography>
        </Box>
      ) : searchResults?.results?.length === 0 ? (
        <Box textAlign="center" my={4}>
          <Typography color="text.secondary">
            No results found for "{searchQuery}"
            {contentType && ` in ${contentType}`}
            {language && ` in ${LANGUAGES.find(l => l.code === language)?.label}`}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {searchResults?.results?.map((item: Content) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="300"
                  image={item.poster_url || '/placeholder-poster.jpg'}
                  alt={item.title}
                  sx={{
                    objectFit: 'cover',
                    backgroundColor: 'rgba(0, 0, 0, 0.08)'
                  }}
                />
                <CardContent>
                  <Typography gutterBottom variant="h6" component="div">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {item.overview || 'No description available'}
                  </Typography>
                  {item.genres && item.genres.length > 0 && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Genres: {item.genres.join(', ')}
                    </Typography>
                  )}
                  {item.rating && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Rating: ⭐ {item.rating}
                    </Typography>
                  )}
                  {item.language && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Language: {item.language}
                    </Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Button
                          variant="contained"
                          color="primary"
                          onClick={() => handleAddToWatchlist(item.id)}
                          fullWidth
                        >
                          Add to Watchlist
                        </Button>
                      </Grid>
                      <Grid item xs={6}>
                        <Button
                          variant="outlined"
                          color="secondary"
                          onClick={() => handleAddToBucketList(item.id)}
                          fullWidth
                        >
                          Add to Bucket List
                        </Button>
                      </Grid>
                    </Grid>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Login Dialog */}
      <Dialog open={loginDialogOpen} onClose={() => setLoginDialogOpen(false)}>
        <DialogTitle>Login Required</DialogTitle>
        <DialogContent>
          <Typography>
            You need to be logged in to add content to your watchlist.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLoginDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleLoginClick} variant="contained" color="primary">
            Login
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Search;