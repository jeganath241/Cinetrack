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
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
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

const PersonDetails = () => {
  const { id } = useParams<{ id: string }>();
  const [tabValue, setTabValue] = useState(0);

  const { data: person, isLoading, error } = useQuery(
    ['person', id],
    () => content.getPersonDetails(Number(id)),
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
        <Alert severity="error">Failed to load person details. Please try again.</Alert>
      </Container>
    );
  }

  if (!person) {
    return (
      <Container>
        <Alert severity="info">Person not found.</Alert>
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
              image={person.image || '/placeholder-avatar.jpg'}
              alt={person.name}
              sx={{ objectFit: 'cover' }}
            />
            <CardContent>
              <Typography variant="h5" gutterBottom>
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
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Cast Roles" />
              <Tab label="Crew Roles" />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <List>
              {person.castRoles.map((role: any, index: number) => (
                <ListItem key={index}>
                  <ListItemAvatar>
                    <Avatar src={role.show.image || '/placeholder-poster.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={role.show.name}
                    secondary={`as ${role.character}`}
                  />
                </ListItem>
              ))}
            </List>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <List>
              {person.crewRoles.map((role: any, index: number) => (
                <ListItem key={index}>
                  <ListItemAvatar>
                    <Avatar src={role.show.image || '/placeholder-poster.jpg'} />
                  </ListItemAvatar>
                  <ListItemText
                    primary={role.show.name}
                    secondary={role.type}
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

export default PersonDetails;
