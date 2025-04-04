import { useState } from 'react';
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
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  ImageList,
  ImageListItem,
} from '@mui/material';
import { content } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ShowDetails = () => {
  const { id } = useParams<{ id: string }>();
  const [tabValue, setTabValue] = useState(0);

  const { data: show, isLoading, error } = useQuery(
    ['show', id],
    () => content.getShowDetails(Number(id)),
    {
      enabled: !!id,
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
        <Alert severity="error">Failed to load show details. Please try again.</Alert>
      </Container>
    );
  }

  if (!show) {
    return (
      <Container>
        <Alert severity="info">Show not found.</Alert>
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
              height="500"
              image={show.image?.original || '/placeholder-poster.jpg'}
              alt={show.title}
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {show.title}
              </Typography>
              <Box sx={{ mb: 2 }}>
                {show.genres.map((genre: string) => (
                  <Chip
                    key={genre}
                    label={genre}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                {show.overview}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {show.status}
              </Typography>
              {show.network && (
                <Typography variant="body2" color="text.secondary">
                  Network: {show.network}
                </Typography>
              )}
              {show.webChannel && (
                <Typography variant="body2" color="text.secondary">
                  Web Channel: {show.webChannel}
                </Typography>
              )}
              <Typography variant="body2" color="text.secondary">
                Language: {show.language}
              </Typography>
              {show.rating && (
                <Typography variant="body2" color="text.secondary">
                  Rating: ⭐ {show.rating}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Episodes" />
              <Tab label="Cast" />
              <Tab label="Crew" />
              <Tab label="Images" />
              <Tab label="Alternate Names" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            {Object.entries(show.episodes).map(([season, episodes]: [string, any[]]) => (
              <Box key={season} sx={{ mb: 4 }}>
                <Typography variant="h6" gutterBottom>
                  Season {season}
                </Typography>
                <List>
                  {episodes.map((episode: any) => (
                    <ListItem key={episode.id}>
                      <ListItemText
                        primary={`${episode.number}. ${episode.name}`}
                        secondary={episode.summary?.replace(/<[^>]*>/g, '')}
                      />
                    </ListItem>
                  ))}
                </List>
                <Divider />
              </Box>
            ))}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <List>
              {show.cast.map((castMember: any) => (
                <ListItem key={castMember.person.id}>
                  <ListItemAvatar>
                    <Avatar src={castMember.person.image || '/placeholder-avatar.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={castMember.person.name}
                    secondary={`as ${castMember.character.name}`}
                  />
                </ListItem>
              ))}
            </List>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <List>
              {show.crew.map((crewMember: any) => (
                <ListItem key={crewMember.person.id}>
                  <ListItemAvatar>
                    <Avatar src={crewMember.person.image || '/placeholder-avatar.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={crewMember.person.name}
                    secondary={crewMember.type}
                  />
                </ListItem>
              ))}
            </List>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <ImageList cols={3} gap={8}>
              {show.images.map((image: any) => (
                <ImageListItem key={image.id}>
                  <img
                    src={image.url}
                    alt={`${show.title} - ${image.type}`}
                    loading="lazy"
                  />
                </ImageListItem>
              ))}
            </ImageList>
          </TabPanel>

          <TabPanel value={tabValue} index={4}>
            <List>
              {show.alternateNames.map((aka: any, index: number) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={aka.name}
                    secondary={aka.country ? `Country: ${aka.country}` : undefined}
                  />
                </ListItem>
              ))}
            </List>
          </TabPanel>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ShowDetails;
