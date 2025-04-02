import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  FormControlLabel,
  Switch,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import { api } from '../services/api';

interface ReviewProps {
  contentId: number;
  initialReview?: {
    id: number;
    description: string;
    is_private: boolean;
  };
  onReviewChange?: () => void;
}

export const Review: React.FC<ReviewProps> = ({
  contentId,
  initialReview,
  onReviewChange
}) => {
  const [review, setReview] = useState(initialReview?.description || '');
  const [isPrivate, setIsPrivate] = useState(initialReview?.is_private || false);
  const [isEditing, setIsEditing] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);

  const handleSubmit = async () => {
    try {
      if (initialReview) {
        // Update existing review
        await api.put(`/reviews/${initialReview.id}`, {
          content_id: contentId,
          description: review,
          is_private: isPrivate
        });
      } else {
        // Create new review
        await api.post('/reviews/', {
          content_id: contentId,
          description: review,
          is_private: isPrivate
        });
      }
      setIsEditing(false);
      onReviewChange?.();
    } catch (error) {
      console.error('Error saving review:', error);
    }
  };

  const handleDelete = async () => {
    try {
      if (initialReview) {
        await api.delete(`/reviews/${initialReview.id}`);
        setReview('');
        setIsPrivate(false);
        onReviewChange?.();
      }
    } catch (error) {
      console.error('Error deleting review:', error);
    }
  };

  if (!isEditing && !initialReview) {
    return (
      <Button
        variant="outlined"
        onClick={() => setIsEditing(true)}
        sx={{ mt: 2 }}
      >
        Write a Review
      </Button>
    );
  }

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      {isEditing ? (
        <Box>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={review}
            onChange={(e) => setReview(e.target.value)}
            placeholder="Write your review..."
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
              />
            }
            label="Make this review private"
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={!review.trim()}
            >
              Save Review
            </Button>
            <Button
              variant="outlined"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </Button>
          </Box>
        </Box>
      ) : (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body1">{review}</Typography>
            <Box>
              <IconButton onClick={() => setIsEditing(true)}>
                <Edit />
              </IconButton>
              <IconButton onClick={() => setOpenDialog(true)}>
                <Delete />
              </IconButton>
            </Box>
          </Box>
          {isPrivate && (
            <Typography variant="caption" color="text.secondary">
              Private Review
            </Typography>
          )}
        </Box>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Delete Review</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this review? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}; 