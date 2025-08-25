import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Button,
  Card,
  CardContent
} from '@mui/material';
import {
  CheckCircle,
  Error,
  Warning,
  Schedule,
  CloudUpload,
  Verified,
  Storage,
  Done,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

import { ImportProgress as IImportProgress, ImportResult } from '@/services/importService';

interface ImportProgressProps {
  progress?: IImportProgress;
  result?: ImportResult;
  onRetry?: () => void;
  onReset?: () => void;
}

export default function ImportProgress({
  progress,
  result,
  onRetry,
  onReset
}: ImportProgressProps) {
  const [showDetails, setShowDetails] = React.useState(false);

  const getStepIcon = (stage: string) => {
    if (!progress) return <Schedule />;
    
    switch (stage) {
      case 'parsing':
        return progress.stage === 'parsing' ? <CloudUpload color="primary" /> : 
               progress.stage === 'error' ? <Error color="error" /> : <CheckCircle color="success" />;
      case 'validating':
        return progress.stage === 'validating' ? <Verified color="primary" /> :
               progress.stage === 'error' ? <Error color="error" /> :
               ['importing', 'completed'].includes(progress.stage) ? <CheckCircle color="success" /> : <Schedule />;
      case 'importing':
        return progress.stage === 'importing' ? <Storage color="primary" /> :
               progress.stage === 'error' ? <Error color="error" /> :
               progress.stage === 'completed' ? <CheckCircle color="success" /> : <Schedule />;
      default:
        return <Schedule />;
    }
  };

  const getActiveStep = () => {
    if (!progress) return 0;
    
    switch (progress.stage) {
      case 'parsing': return 0;
      case 'validating': return 1;
      case 'importing': return 2;
      case 'completed': return 3;
      case 'error': return -1;
      default: return 0;
    }
  };

  const steps = [
    {
      label: 'Parsing Data',
      description: 'Reading and parsing imported files',
      stage: 'parsing'
    },
    {
      label: 'Validating Data',
      description: 'Checking data integrity and format',
      stage: 'validating'
    },
    {
      label: 'Importing Data',
      description: 'Saving data to the database',
      stage: 'importing'
    },
    {
      label: 'Import Complete',
      description: 'Data successfully imported',
      stage: 'completed'
    }
  ];

  if (result) {
    return (
      <Paper sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          {result.error_count === 0 ? (
            <>
              <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom color="success.main">
                Import Completed Successfully!
              </Typography>
            </>
          ) : (
            <>
              <Warning sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom color="warning.main">
                Import Completed with Issues
              </Typography>
            </>
          )}
        </Box>

        {/* Summary Stats */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <Chip
            label={`${result.success_count} Successful`}
            color="success"
            variant={result.success_count > 0 ? 'filled' : 'outlined'}
            sx={{ fontSize: '0.875rem', py: 1 }}
          />
          <Chip
            label={`${result.error_count} Errors`}
            color="error"
            variant={result.error_count > 0 ? 'filled' : 'outlined'}
            sx={{ fontSize: '0.875rem', py: 1 }}
          />
          <Chip
            label={`${result.total_count} Total`}
            color="primary"
            variant="outlined"
            sx={{ fontSize: '0.875rem', py: 1 }}
          />
          <Chip
            label={`${result.processing_time_ms}ms`}
            variant="outlined"
            sx={{ fontSize: '0.875rem', py: 1 }}
          />
        </Box>

        {/* Success Summary */}
        {result.success_count > 0 && (
          <Card sx={{ mb: 2, bgcolor: 'success.50', borderColor: 'success.200' }}>
            <CardContent>
              <Typography variant="subtitle1" color="success.main" gutterBottom>
                Successfully Imported Items:
              </Typography>
              <List dense>
                {result.imported_products && (
                  <ListItem>
                    <ListItemText 
                      primary={`${result.imported_products.length} Products`}
                      secondary={result.imported_products.slice(0, 3).map(p => p.name).join(', ') + 
                                (result.imported_products.length > 3 ? '...' : '')}
                    />
                  </ListItem>
                )}
                {result.imported_recipes && (
                  <ListItem>
                    <ListItemText 
                      primary={`${result.imported_recipes.length} Recipes`}
                      secondary={result.imported_recipes.slice(0, 3).map(r => r.product?.name || 'Unknown').join(', ') + 
                                (result.imported_recipes.length > 3 ? '...' : '')}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        )}

        {/* Error Details */}
        {result.errors.length > 0 && (
          <Card sx={{ mb: 2, bgcolor: 'error.50', borderColor: 'error.200' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="error.main">
                  Import Errors ({result.errors.length}):
                </Typography>
                <Button
                  size="small"
                  onClick={() => setShowDetails(!showDetails)}
                  endIcon={showDetails ? <ExpandLess /> : <ExpandMore />}
                >
                  {showDetails ? 'Hide' : 'Show'} Details
                </Button>
              </Box>
              
              <Collapse in={showDetails}>
                <List dense>
                  {result.errors.slice(0, 10).map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Error color="error" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`Row ${error.row}: ${error.field}`}
                        secondary={`${error.error} (Value: ${error.value})`}
                      />
                    </ListItem>
                  ))}
                  {result.errors.length > 10 && (
                    <ListItem>
                      <ListItemText 
                        secondary={`... and ${result.errors.length - 10} more errors`}
                      />
                    </ListItem>
                  )}
                </List>
              </Collapse>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 3 }}>
          {result.error_count > 0 && onRetry && (
            <Button variant="outlined" onClick={onRetry} color="warning">
              Fix Errors & Retry
            </Button>
          )}
          {onReset && (
            <Button variant="contained" onClick={onReset}>
              Import More Data
            </Button>
          )}
        </Box>
      </Paper>
    );
  }

  if (!progress) {
    return null;
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Storage />
        Import Progress
      </Typography>

      {/* Progress Bar */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {progress.message}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {progress.percentage}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={progress.percentage}
          color={progress.stage === 'error' ? 'error' : 'primary'}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>

      {/* Status Message */}
      {progress.stage === 'error' ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          Import failed: {progress.message}
        </Alert>
      ) : (
        <Alert 
          severity={progress.stage === 'completed' ? 'success' : 'info'} 
          sx={{ mb: 2 }}
        >
          <Typography variant="body2">
            {progress.stage === 'completed' ? 'Import completed successfully!' : progress.message}
          </Typography>
        </Alert>
      )}

      {/* Step Progress */}
      <Stepper activeStep={getActiveStep()} orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.stage}>
            <StepLabel 
              icon={getStepIcon(step.stage)}
              error={progress.stage === 'error' && index === getActiveStep()}
            >
              <Typography variant="subtitle2">
                {step.label}
              </Typography>
            </StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                {step.description}
              </Typography>
              {progress.stage === step.stage && progress.stage !== 'completed' && (
                <Box sx={{ mt: 1 }}>
                  <LinearProgress size="small" />
                </Box>
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>

      {/* Detailed Progress Info */}
      {progress.total > 0 && (
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Progress: {progress.current} / {progress.total} items processed
          </Typography>
        </Box>
      )}
    </Paper>
  );
}