import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Grid,
  Chip,
  Divider,
  CircularProgress,
} from '@mui/material';
import { Rating } from './Rating';
import { Review } from './Review';
import { api } from '../services/api';

interface ContentDetailsProps {
  contentId: number;
}

interface Review {
  id: number;
  description: string;
  is_private: boolean;
  user: {
    email: string;
  };
}

export const ContentDetails: React.FC<ContentDetailsProps> = ({ contentId }) => {
  const [content, setContent] = useState<any>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const [contentResponse, reviewsResponse] = await Promise.all([
          api.get(`/content/${contentId}`),
          api.get(`/reviews/content/${contentId}`)
        ]);
        setContent(contentResponse.data);
        setReviews(reviewsResponse.data);
      } catch (error) {
        console.error('Error fetching content:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [contentId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!content) {
    return (
      <Typography variant="h6" color="error">
        Content not found
      </Typography>
    );
  }

  return (
    <Card>
      <Grid container>
        <Grid item xs={12} md={4}>
          <CardMedia
            component="img"
            height="500"
            image={content.poster_url}
            alt={content.title}
          />
        </Grid>
        <Grid item xs={12} md={8}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              {content.title}
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Chip
                label={content.content_type}
                color="primary"
                sx={{ mr: 1 }}
              />
              {content.imdb_rating && (
                <Chip
                  label={`IMDb: ${content.imdb_rating}/10`}
                  color="secondary"
                />
              )}
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Your Rating
              </Typography>
              <Rating
                contentId={contentId}
                onRatingChange={() => {
                  // Refresh content to update average rating
                  api.get(`/content/${contentId}`).then(response => {
                    setContent(response.data);
                  });
                }}
              />
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="body1" paragraph>
              {content.description}
            </Typography>

            {content.total_episodes && (
              <Typography variant="body2" color="text.secondary">
                Total Episodes: {content.total_episodes}
              </Typography>
            )}

            {content.release_date && (
              <Typography variant="body2" color="text.secondary">
                Release Date: {new Date(content.release_date).toLocaleDateString()}
              </Typography>
            )}
          </CardContent>
        </Grid>
      </Grid>

      <Divider />

      <CardContent>
        <Typography variant="h6" gutterBottom>
          Reviews
        </Typography>
        
        <Review
          contentId={contentId}
          onReviewChange={() => {
            // Refresh reviews
            api.get(`/reviews/content/${contentId}`).then(response => {
              setReviews(response.data);
            });
          }}
        />

        {reviews.map((review) => (
          <Box key={review.id} sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary">
              {review.user.email}
            </Typography>
            <Typography variant="body1">
              {review.description}
            </Typography>
            {review.is_private && (
              <Typography variant="caption" color="text.secondary">
                Private Review
              </Typography>
            )}
          </Box>
        ))}
      </CardContent>
    </Card>
  );
}; 