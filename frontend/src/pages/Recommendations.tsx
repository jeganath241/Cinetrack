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
  Switch,
  FormControlLabel,
} from '@mui/material';
import { Delete as DeleteIcon, Edit as EditIcon } from '@mui/icons-material';
import { api } from '../services/api';
import { Content, Recommendation as RecommendationType } from '../types/api';

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecommendationType[]>([]);
  const [filteredList, setFilteredList] = useState<RecommendationType[]>([]);
  const [contentType, setContentType] = useState<string>('');
  const [genre, setGenre] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [isPublic, setIsPublic] = useState<boolean | null>(null);
  const [sortBy, setSortBy] = useState<string>('created_at');
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState<RecommendationType | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [note, setNote] = useState<string>('');
  const [publicToggle, setPublicToggle] = useState<boolean>(false);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [recommendations, contentType, genre, language, isPublic, sortBy]);

  const fetchRecommendations = async () => {
    try {
      const response = await api.get('/recommendations/');
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const applyFilters = () => {
    let filtered = [...recommendations];

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

    if (isPublic !== null) {
      filtered = filtered.filter(item => item.is_public === isPublic);
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

  const handleOpenDialog = (item: RecommendationType) => {
    setSelectedItem(item);
    setNote(item.note || '');
    setPublicToggle(item.is_public);
    setEditMode(true);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setSelectedItem(null);
    setNote('');
    setPublicToggle(false);
    setEditMode(false);
    setOpenDialog(false);
  };

  const handleUpdate = async () => {
    if (!selectedItem) return;

    try {
      await api.put(`/recommendations/${selectedItem.id}`, {
        content_id: selectedItem.content_id,
        is_public: publicToggle,
        note: note,
      });
      fetchRecommendations();
      handleCloseDialog();
    } catch (error) {
      console.error('Error updating recommendation:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedItem) return;

    try {
      await api.delete(`/recommendations/${selectedItem.id}`);
      fetchRecommendations();
      handleCloseDialog();
    } catch (error) {
      console.error('Error deleting recommendation:', error);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Recommendations
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
              <InputLabel>Visibility</InputLabel>
              <Select
                value={isPublic === null ? '' : isPublic}
                label="Visibility"
                onChange={(e) => setIsPublic(e.target.value === '' ? null : e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value={true}>Public</MenuItem>
                <MenuItem value={false}>Private</MenuItem>
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
                {item.note && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Note: {item.note}
                  </Typography>
                )}
                <Chip
                  label={item.is_public ? 'Public' : 'Private'}
                  color={item.is_public ? 'primary' : 'default'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </CardContent>
              <CardActions>
                <IconButton
                  onClick={() => handleOpenDialog(item)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  onClick={() => {
                    setSelectedItem(item);
                    setEditMode(false);
                    setOpenDialog(true);
                  }}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editMode ? 'Edit Recommendation' : 'Delete Recommendation'}
        </DialogTitle>
        <DialogContent>
          {editMode ? (
            <>
              <Typography variant="h6" gutterBottom>
                {selectedItem?.content.title}
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                sx={{ mt: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={publicToggle}
                    onChange={(e) => setPublicToggle(e.target.checked)}
                  />
                }
                label="Make Public"
                sx={{ mt: 2 }}
              />
            </>
          ) : (
            <Typography>
              Are you sure you want to delete your recommendation for "{selectedItem?.content.title}"?
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          {editMode ? (
            <Button onClick={handleUpdate} color="primary">
              Update
            </Button>
          ) : (
            <Button onClick={handleDelete} color="error">
              Delete
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Recommendations; 