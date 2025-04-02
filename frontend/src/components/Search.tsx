import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  FormGroup,
  FormControlLabel,
  Checkbox,
  CircularProgress,
} from '@mui/material';
import { api } from '../services/api';

interface SearchResult {
  id: number;
  title: string;
  content_type: string;
  imdb_rating: number;
  poster_url: string;
  release_date: string;
}

type SortOption = 'release_date' | 'imdb_rating' | 'popularity';

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [contentTypes, setContentTypes] = useState<string[]>([]);
  const [imdbRatingRange, setImdbRatingRange] = useState<[number, number]>([0, 10]);
  const [sortBy, setSortBy] = useState<SortOption>('release_date');

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await api.get('/content/search', {
        params: {
          query,
          content_types: contentTypes.join(','),
          min_imdb_rating: imdbRatingRange[0],
          max_imdb_rating: imdbRatingRange[1],
          sort_by: sortBy
        }
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error searching content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContentTypeChange = (type: string) => {
    setContentTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search movies, TV shows, and anime"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Search'}
            </Button>
          </Grid>
        </Grid>

        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Content Type</InputLabel>
                <Select
                  multiple
                  value={contentTypes}
                  onChange={(e) => setContentTypes(e.target.value as string[])}
                  label="Content Type"
                >
                  <MenuItem value="movie">Movies</MenuItem>
                  <MenuItem value="series">TV Shows</MenuItem>
                  <MenuItem value="anime">Anime</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography gutterBottom>IMDb Rating Range</Typography>
              <Slider
                value={imdbRatingRange}
                onChange={(_, newValue) => setImdbRatingRange(newValue as [number, number])}
                valueLabelDisplay="auto"
                min={0}
                max={10}
                step={0.1}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  label="Sort By"
                >
                  <MenuItem value="release_date">Release Date</MenuItem>
                  <MenuItem value="imdb_rating">IMDb Rating</MenuItem>
                  <MenuItem value="popularity">Popularity</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {results.map((result) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={result.id}>
            <Card>
              <CardMedia
                component="img"
                height="300"
                image={result.poster_url}
                alt={result.title}
              />
              <CardContent>
                <Typography variant="h6" noWrap>
                  {result.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {result.content_type}
                </Typography>
                {result.imdb_rating && (
                  <Typography variant="body2" color="text.secondary">
                    IMDb: {result.imdb_rating}/10
                  </Typography>
                )}
                <Typography variant="body2" color="text.secondary">
                  {new Date(result.release_date).getFullYear()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}; 