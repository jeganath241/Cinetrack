import React from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  Box,
  LinearProgress,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchlist } from '../services/api';
import { WatchlistItem } from '../types/api';

const Watchlist: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: watchlistItems, isLoading } = useQuery({
    queryKey: ['watchlist'],
    queryFn: watchlist.getAll,
  });

  const updateMutation = useMutation({
    mutationFn: ({ itemId, watchedEpisodes, isCompleted }: {
      itemId: number;
      watchedEpisodes: number;
      isCompleted: boolean;
    }) => watchlist.update(itemId, watchedEpisodes, isCompleted),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });

  const removeMutation = useMutation({
    mutationFn: watchlist.remove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });

  const handleUpdateProgress = (itemId: number, watchedEpisodes: number) => {
    const item = watchlistItems?.find((i) => i.id === itemId);
    if (item) {
      const isCompleted = watchedEpisodes >= (item.content.total_episodes || 1);
      updateMutation.mutate({ itemId, watchedEpisodes, isCompleted });
    }
  };

  if (isLoading) {
    return <LinearProgress />;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        My Watchlist
      </Typography>
      <Grid container spacing={3}>
        {watchlistItems?.map((item: WatchlistItem) => (
          <Grid item xs={12} sm={6} md={4} key={item.id}>
            <Card>
              <CardMedia
                component="img"
                height="300"
                image={item.content.poster_url}
                alt={item.content.title}
              />
              <CardContent>
                <Typography gutterBottom variant="h6" component="div">
                  {item.content.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.content.year}
                </Typography>
                {item.content.type !== 'movie' && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      Progress: {item.watched_episodes} / {item.content.total_episodes} episodes
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(item.watched_episodes / (item.content.total_episodes || 1)) * 100}
                      sx={{ mt: 1 }}
                    />
                    <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleUpdateProgress(item.id, Math.max(0, item.watched_episodes - 1))}
                      >
                        -
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleUpdateProgress(item.id, item.watched_episodes + 1)}
                      >
                        +
                      </Button>
                    </Box>
                  </Box>
                )}
                <Button
                  variant="contained"
                  color="error"
                  fullWidth
                  sx={{ mt: 2 }}
                  onClick={() => removeMutation.mutate(item.id)}
                >
                  Remove from Watchlist
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Watchlist; 