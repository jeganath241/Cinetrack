import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Box,
  TextField,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import { content } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { useDebounce } from '../hooks/useDebounce';

const PeopleSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const navigate = useNavigate();

  // Create a debounced function to update debouncedQuery
  const debouncedSetQuery = useDebounce((query: string) => {
    setDebouncedQuery(query);
  }, 500);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setSearchQuery(query);
    debouncedSetQuery(query);
  };

  const { data: people, isLoading, error } = useQuery(
    ['people', debouncedQuery],
    () => content.searchPeople(debouncedQuery),
    {
      enabled: debouncedQuery.length >= 2,
      keepPreviousData: true,
    }
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ mb: 4 }}>
        <TextField
          fullWidth
          label="Search people"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Type at least 2 characters to search..."
        />
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
      ) : people?.length === 0 ? (
        <Box textAlign="center" my={4}>
          <Typography color="text.secondary">
            No results found for "{searchQuery}"
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {people?.map((person: any) => (
            <Grid item xs={12} sm={6} md={4} key={person.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="300"
                  image={person.image || '/placeholder-avatar.jpg'}
                  alt={person.name}
                  sx={{ objectFit: 'cover' }}
                />
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {person.name}
                  </Typography>
                  {person.birthday && (
                    <Typography variant="body2" color="text.secondary">
                      Birthday: {person.birthday}
                    </Typography>
                  )}
                  {person.deathday && (
                    <Typography variant="body2" color="text.secondary">
                      Deathday: {person.deathday}
                    </Typography>
                  )}
                  {person.gender && (
                    <Typography variant="body2" color="text.secondary">
                      Gender: {person.gender}
                    </Typography>
                  )}
                  {person.country && (
                    <Typography variant="body2" color="text.secondary">
                      Country: {person.country}
                    </Typography>
                  )}
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => navigate(`/people/${person.id}`)}
                    >
                      View Details
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default PeopleSearch;
