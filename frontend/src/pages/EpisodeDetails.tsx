import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  CardMedia,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { content } from '../services/api';

const EpisodeDetails = () => {
  const { id } = useParams<{ id: string }>();

  const { data: episode, isLoading, error } = useQuery(
    ['episode', id],
    () => content.getEpisodeDetails(Number(id)),
    {
      enabled: !!id,
    }
  );

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
        <Alert severity="error">Failed to load episode details. Please try again.</Alert>
      </Container>
    );
  }

  if (!episode) {
    return (
      <Container>
        <Alert severity="info">Episode not found.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardMedia
              component="img"
              height="400"
              image={episode.image || '/placeholder-episode.jpg'}
              alt={episode.name}
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {episode.name}
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={`Season ${episode.season}`}
                  size="small"
                  sx={{ mr: 0.5 }}
                />
                <Chip
                  label={`Episode ${episode.number}`}
                  size="small"
                  sx={{ mr: 0.5 }}
                />
                {episode.rating && (
                  <Chip
                    label={`⭐ ${episode.rating}`}
                    size="small"
                  />
                )}
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                {episode.summary}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Air Date: {episode.airdate}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Air Time: {episode.airtime}
              </Typography>
              {episode.runtime && (
                <Typography variant="body2" color="text.secondary">
                  Runtime: {episode.runtime} minutes
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Guest Cast
            </Typography>
            <List>
              {episode.guestCast.map((cast: any, index: number) => (
                <ListItem key={index}>
                  <ListItemAvatar>
                    <Avatar src={cast.person.image || '/placeholder-avatar.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={cast.person.name}
                    secondary={`as ${cast.character.name}`}
                  />
                </ListItem>
              ))}
            </List>
          </Box>

          <Divider sx={{ my: 4 }} />

          <Box>
            <Typography variant="h6" gutterBottom>
              Guest Crew
            </Typography>
            <List>
              {episode.guestCrew.map((crew: any, index: number) => (
                <ListItem key={index}>
                  <ListItemAvatar>
                    <Avatar src={crew.person.image || '/placeholder-avatar.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={crew.person.name}
                    secondary={crew.type}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
};

export default EpisodeDetails;
