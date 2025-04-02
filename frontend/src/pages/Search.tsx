import React, { useState } from 'react';
import {
  Container,
  TextField,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { content } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Content, ContentType } from '../types/api';

const Search: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [contentType, setContentType] = useState<ContentType | ''>('');
  const navigate = useNavigate();

  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['search', searchQuery, contentType],
    queryFn: () => content.search(searchQuery, contentType || undefined),
    enabled: !!searchQuery,
  });

  const handleAddToWatchlist = async (contentId: number) => {
    try {
      await content.add(contentId);
      navigate('/watchlist');
    } catch (error) {
      console.error('Failed to add to watchlist:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label="Search movies, series, or anime"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={contentType}
                label="Content Type"
                onChange={(e) => setContentType(e.target.value as ContentType)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="movie">Movies</MenuItem>
                <MenuItem value="series">Series</MenuItem>
                <MenuItem value="anime">Anime</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {isLoading ? (
        <Typography>Loading...</Typography>
      ) : (
        <Grid container spacing={3}>
          {searchResults?.map((item: Content) => (
            <Grid item xs={12} sm={6} md={4} key={item.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="300"
                  image={item.poster_url}
                  alt={item.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h6" component="div">
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.year}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {item.description}
                  </Typography>
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    sx={{ mt: 2 }}
                    onClick={() => handleAddToWatchlist(item.id)}
                  >
                    Add to Watchlist
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default Search; 