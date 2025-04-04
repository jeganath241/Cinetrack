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
  Pagination,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import { content } from '../services/api';
import { useNavigate } from 'react-router-dom';

const PeopleIndex = () => {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data: people, isLoading, error } = useQuery(
    ['people', page],
    () => content.getPeopleIndex(page),
    {
      keepPreviousData: true,
    }
  );

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
    window.scrollTo(0, 0);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" my={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">Failed to load people. Please try again.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        People in TV
      </Typography>

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
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Birthday: {person.birthday}
                  </Typography>
                )}
                {person.deathday && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Deathday: {person.deathday}
                  </Typography>
                )}
                {person.gender && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Gender: {person.gender}
                  </Typography>
                )}
                {person.country && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Country: {person.country}
                  </Typography>
                )}
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => navigate(`/people/${person.id}`)}
                >
                  View Details
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box display="flex" justifyContent="center" my={4}>
        <Pagination
          count={250} // TVMaze API has a maximum of 250 pages
          page={page}
          onChange={handlePageChange}
          color="primary"
          size="large"
        />
      </Box>
    </Container>
  );
};

export default PeopleIndex;
