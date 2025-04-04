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
  Chip,
  Button,
} from '@mui/material';
import { content } from '../services/api';
import { useNavigate } from 'react-router-dom';

const ShowIndex = () => {
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data: shows, isLoading, error } = useQuery(
    ['shows', page],
    () => content.getShowIndex(page),
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
        <Alert severity="error">Failed to load shows. Please try again.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        TV Shows
      </Typography>

      <Grid container spacing={3}>
        {shows?.map((show: any) => (
          <Grid item xs={12} sm={6} md={4} key={show.id}>
            <Card>
              <CardMedia
                component="img"
                height="300"
                image={show.image || '/placeholder-poster.jpg'}
                alt={show.title}
                sx={{ objectFit: 'cover' }}
              />
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {show.title}
                </Typography>
                <Box sx={{ mb: 2 }}>
                  {show.genres.slice(0, 3).map((genre: string) => (
                    <Chip
                      key={genre}
                      label={genre}
                      size="small"
                      sx={{ mr: 0.5, mb: 0.5 }}
                    />
                  ))}
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Status: {show.status}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Language: {show.language}
                </Typography>
                {show.premiered && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Premiered: {show.premiered}
                  </Typography>
                )}
                {show.rating && (
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Rating: ⭐ {show.rating}
                  </Typography>
                )}
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => navigate(`/show/${show.id}`)}
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

export default ShowIndex;
