import React, { useState, useEffect } from 'react';
import { Box, Rating as MuiRating, Typography, IconButton, Tooltip } from '@mui/material';
import { Star, StarBorder } from '@mui/icons-material';
import { api } from '../services/api';

interface RatingProps {
  contentId: number;
  initialRating?: number;
  readOnly?: boolean;
  onRatingChange?: (rating: number) => void;
}

export const Rating: React.FC<RatingProps> = ({
  contentId,
  initialRating = 0,
  readOnly = false,
  onRatingChange
}) => {
  const [rating, setRating] = useState<number>(initialRating);
  const [hover, setHover] = useState<number>(-1);

  useEffect(() => {
    setRating(initialRating);
  }, [initialRating]);

  const handleRatingChange = async (newRating: number) => {
    try {
      if (rating === 0) {
        // Create new rating
        await api.post('/ratings/', {
          content_id: contentId,
          rating: newRating
        });
      } else {
        // Update existing rating
        await api.put(`/ratings/${rating}`, {
          content_id: contentId,
          rating: newRating
        });
      }
      setRating(newRating);
      onRatingChange?.(newRating);
    } catch (error) {
      console.error('Error updating rating:', error);
    }
  };

  const labels: { [index: string]: string } = {
    0: 'No rating',
    1: 'Poor',
    2: 'Fair',
    3: 'Good',
    4: 'Very Good',
    5: 'Excellent',
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <MuiRating
        value={rating}
        precision={1}
        onChange={(_, newValue) => {
          if (!readOnly && newValue !== null) {
            handleRatingChange(newValue);
          }
        }}
        onChangeActive={(_, newHover) => {
          setHover(newHover);
        }}
        readOnly={readOnly}
        emptyIcon={<StarBorder sx={{ color: 'text.secondary' }} />}
        icon={<Star sx={{ color: 'primary.main' }} />}
      />
      {rating !== null && (
        <Box sx={{ width: 100 }}>
          <Typography variant="body2" color="text.secondary">
            {labels[hover !== -1 ? hover : rating]}
          </Typography>
        </Box>
      )}
    </Box>
  );
}; 