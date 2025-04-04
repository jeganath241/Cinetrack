import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Delete as DeleteIcon, Check as CheckIcon } from '@mui/icons-material';
import api from '../services/api';
import { Content, BucketList as BucketListType } from '../types/api';

const BucketList: React.FC = () => {
  const [bucketList, setBucketList] = useState<BucketListType[]>([]);
  const [filteredList, setFilteredList] = useState<BucketListType[]>([]);
  const [contentType, setContentType] = useState<string>('');
  const [genre, setGenre] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [isWatched, setIsWatched] = useState<boolean | null>(null);
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<BucketListType | null>(null);

  useEffect(() => {
    fetchBucketList();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [bucketList, contentType, genre, language, isWatched, sortBy]);

  const fetchBucketList = async () => {
    try {
      const response = await api.get('/bucketlist/');
      setBucketList(response.data);
    } catch (error) {
      console.error('Error fetching bucket list:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...bucketList];

    if (contentType) {
      filtered = filtered.filter(item => item.content.content_type === contentType);
    }

    if (genre) {
      filtered = filtered.filter(item => 
        item.content.genres.toLowerCase().includes(genre.toLowerCase())
      );
    }

    if (language) {
      filtered = filtered.filter(item => item.content.language === language);
    }

    if (isWatched !== null) {
      filtered = filtered.filter(item => item.is_watched === isWatched);
    }

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'created_at') {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      } else if (sortBy === 'imdb_rating') {
        return (b.content.imdb_rating || 0) - (a.content.imdb_rating || 0);
      }
      return 0;
    });

    setFilteredList(filtered);
  };

  const handleMarkAsWatched = async (item: BucketListType) => {
    try {
      await api.put(`/bucketlist/${item.id}`, {
        content_id: item.content_id,
        is_watched: true,
        watched_at: new Date().toISOString(),
      });
      fetchBucketList();
    } catch (error) {
      console.error('Error marking item as watched:', error);
    }
  };

  const handleRemove = async (item: BucketListType) => {
    try {
      await api.delete(`/bucketlist/${item.id}`);
      fetchBucketList();
    } catch (error) {
      console.error('Error removing item:', error);
    }
  };

  const handleOpenDialog = (item: BucketListType) => {
    setSelectedItem(item);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setSelectedItem(null);
    setOpenDialog(false);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Bucket List
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Content Type</InputLabel>
              <Select
                value={contentType}
                label="Content Type"
                onChange={(e) => setContentType(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="movie">Movies</MenuItem>
                <MenuItem value="series">TV Series</MenuItem>
                <MenuItem value="anime">Anime</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={isWatched === null ? '' : isWatched}
                label="Status"
                onChange={(e) => setIsWatched(e.target.value === '' ? null : e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value={false}>Unwatched</MenuItem>
                <MenuItem value={true}>Watched</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="created_at">Date Added</MenuItem>
                <MenuItem value="imdb_rating">IMDb Rating</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {filteredList.map((item) => (
          <Grid item key={item.id} xs={12} sm={6} md={4}>
            <Card>
              <CardMedia
                component="img"
                height="300"
                image={item.content.poster_url}
                alt={item.content.title}
              />
              <CardContent>
                <Typography variant="h6" component="div">
                  {item.content.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.content.content_type.charAt(0).toUpperCase() + item.content.content_type.slice(1)}
                </Typography>
                <Box sx={{ mt: 1 }}>
                  {item.content.genres.split(',').map((genre) => (
                    <Chip
                      key={genre}
                      label={genre.trim()}
                      size="small"
                      sx={{ mr: 0.5, mb: 0.5 }}
                    />
                  ))}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  IMDb Rating: {item.content.imdb_rating || 'N/A'}
                </Typography>
              </CardContent>
              <CardActions>
                {!item.is_watched && (
                  <Button
                    startIcon={<CheckIcon />}
                    onClick={() => handleMarkAsWatched(item)}
                    color="primary"
                  >
                    Mark as Watched
                  </Button>
                )}
                <IconButton
                  onClick={() => handleOpenDialog(item)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Remove from Bucket List</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove "{selectedItem?.content.title}" from your bucket list?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={() => {
              if (selectedItem) {
                handleRemove(selectedItem);
                handleCloseDialog();
              }
            }}
            color="error"
          >
            Remove
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BucketList; 