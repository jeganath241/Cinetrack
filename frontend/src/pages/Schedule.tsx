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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { content } from '../services/api';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { format } from 'date-fns';

const COUNTRIES = [
  { code: 'US', name: 'United States' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'CA', name: 'Canada' },
  { code: 'AU', name: 'Australia' },
  // Add more countries as needed
];

const Schedule = () => {
  const [country, setCountry] = useState('US');
  const [date, setDate] = useState<Date | null>(new Date());

  const { data: schedule, isLoading, error } = useQuery(
    ['schedule', country, date],
    () =>
      content.getSchedule(
        country,
        date ? format(date, 'yyyy-MM-dd') : undefined
      ),
    {
      keepPreviousData: true,
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
        <Alert severity="error">Failed to load schedule. Please try again.</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Country</InputLabel>
            <Select
              value={country}
              label="Country"
              onChange={(e) => setCountry(e.target.value)}
            >
              {COUNTRIES.map((c) => (
                <MenuItem key={c.code} value={c.code}>
                  {c.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <DatePicker
              label="Date"
              value={date}
              onChange={(newDate) => setDate(newDate)}
              renderInput={(params) => <TextField {...params} fullWidth />}
            />
          </LocalizationProvider>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {schedule?.map((item: any) => (
          <Grid item xs={12} sm={6} md={4} key={item.id}>
            <Card>
              <CardMedia
                component="img"
                height="200"
                image={item.show.image || '/placeholder-poster.jpg'}
                alt={item.show.name}
                sx={{ objectFit: 'cover' }}
              />
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {item.show.name}
                </Typography>
                <Box sx={{ mb: 1 }}>
                  <Chip
                    label={item.show.type}
                    size="small"
                    sx={{ mr: 0.5 }}
                  />
                  <Chip
                    label={item.show.language}
                    size="small"
                    sx={{ mr: 0.5 }}
                  />
                  <Chip
                    label={item.show.status}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Air Time: {item.airtime}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Runtime: {item.runtime} minutes
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default Schedule;
