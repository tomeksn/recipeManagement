import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Container,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Link
} from '@mui/material';
import {
  CloudUpload,
  Transform,
  PlayArrow,
  GetApp,
  Description,
  Code,
  TableChart,
  CheckCircle,
  FileUpload as FileUploadIcon
} from '@mui/icons-material';

import { FileUpload, DataMapper, ImportProgress } from '@/components/import';
import { importService, ImportData, ImportMapping, ImportProgress as IImportProgress, ImportResult } from '@/services/importService';

const steps = ['Upload Files', 'Map Fields', 'Review & Import'];

export default function ImportPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [parsedData, setParsedData] = useState<ImportData | null>(null);
  const [mappings, setMappings] = useState<ImportMapping[]>([]);
  const [transformedData, setTransformedData] = useState<ImportData | null>(null);
  const [importProgress, setImportProgress] = useState<IImportProgress | null>(null);
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (files: File[]) => {
    setSelectedFiles(files);
    setError(null);
  };

  const handleFileRemove = (fileToRemove: File) => {
    setSelectedFiles(files => files.filter(file => file !== fileToRemove));
  };

  const handleNext = async () => {
    setError(null);

    switch (activeStep) {
      case 0: // Upload Files -> Parse Data
        if (selectedFiles.length === 0) {
          setError('Please select at least one file');
          return;
        }

        try {
          // For now, parse only the first file
          const file = selectedFiles[0];
          const parsed = await importService.parseFile(file);
          setParsedData(parsed);
          setActiveStep(1);
        } catch (err) {
          setError(`Failed to parse file: ${(err as Error).message}`);
        }
        break;

      case 1: // Map Fields -> Review
        if (mappings.length === 0) {
          setError('Please complete field mapping');
          return;
        }
        setActiveStep(2);
        break;

      case 2: // Review -> Import
        if (!transformedData) {
          setError('No data to import');
          return;
        }

        try {
          setImportProgress({ 
            stage: 'parsing', 
            current: 0, 
            total: 100, 
            message: 'Starting import...', 
            percentage: 0 
          });

          const result = await importService.importData(transformedData, (progress) => {
            setImportProgress(progress);
          });

          setImportResult(result);
          setImportProgress(null);
        } catch (err) {
          setError(`Import failed: ${(err as Error).message}`);
          setImportProgress(null);
        }
        break;
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
    setError(null);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedFiles([]);
    setParsedData(null);
    setMappings([]);
    setTransformedData(null);
    setImportProgress(null);
    setImportResult(null);
    setError(null);
  };

  const handleRetry = () => {
    setActiveStep(1); // Go back to mapping step
    setImportResult(null);
    setError(null);
  };

  const handleMappingComplete = (completedMappings: ImportMapping[]) => {
    setMappings(completedMappings);
  };

  const handleDataTransform = (data: ImportData) => {
    setTransformedData(data);
  };

  const downloadTemplate = (type: 'products' | 'recipes', format: 'csv' | 'json') => {
    importService.downloadTemplate(type, format);
  };

  const getDataSummary = () => {
    if (!parsedData) return null;

    const productCount = parsedData.products?.length || 0;
    const recipeCount = parsedData.recipes?.length || 0;

    return { productCount, recipeCount };
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0: return selectedFiles.length > 0;
      case 1: return mappings.length > 0 && transformedData;
      case 2: return transformedData !== null;
      default: return false;
    }
  };

  // Show import result if completed
  if (importResult) {
    return (
      <>
        <Helmet>
          <title>Import Complete - Recipe Management System</title>
        </Helmet>

        <Container maxWidth='xl' sx={{ py: 4 }}>
          <ImportProgress 
            result={importResult} 
            onRetry={handleRetry}
            onReset={handleReset}
          />
        </Container>
      </>
    );
  }

  // Show progress if importing
  if (importProgress) {
    return (
      <>
        <Helmet>
          <title>Importing Data - Recipe Management System</title>
        </Helmet>

        <Container maxWidth='xl' sx={{ py: 4 }}>
          <ImportProgress progress={importProgress} />
        </Container>
      </>
    );
  }

  return (
    <>
      <Helmet>
        <title>Data Import - Recipe Management System</title>
      </Helmet>

      <Container maxWidth='xl' sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CloudUpload sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant='h4' component='h1' sx={{ fontWeight: 600 }}>
              Import Data
            </Typography>
          </Box>
          <Typography variant='body1' color='text.secondary'>
            Import products and recipes from CSV, JSON, or Excel files
          </Typography>
        </Box>

        {/* Template Downloads */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Download Templates
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Download template files to understand the required data format
          </Typography>
          
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Product Templates
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Template for importing products with name, symbol, type, unit, and categories
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                    <Chip 
                      label="name" 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      label="symbol" 
                      size="small" 
                      variant="outlined"
                      color="primary"
                    />
                    <Chip 
                      label="type" 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      label="unit" 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      label="category" 
                      size="small" 
                      variant="outlined" 
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<TableChart />}
                    onClick={() => downloadTemplate('products', 'csv')}
                  >
                    CSV
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Code />}
                    onClick={() => downloadTemplate('products', 'json')}
                  >
                    JSON
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Recipe Templates
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Template for importing recipes with product info and ingredients
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Chip 
                      label="product_name" 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      label="yield_quantity" 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      label="ingredients" 
                      size="small" 
                      variant="outlined" 
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<TableChart />}
                    onClick={() => downloadTemplate('recipes', 'csv')}
                  >
                    CSV
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Code />}
                    onClick={() => downloadTemplate('recipes', 'json')}
                  >
                    JSON
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </Paper>

        {/* Import Wizard */}
        <Paper sx={{ p: 3 }}>
          {/* Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Error Display */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Step Content */}
          {activeStep === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Upload Import Files
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Select CSV, JSON, or Excel files containing your product or recipe data
              </Typography>
              
              <FileUpload
                accept=".csv,.json,.xlsx,.xls"
                maxSize={10 * 1024 * 1024} // 10MB
                multiple={false}
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                files={selectedFiles}
              />

              {selectedFiles.length > 0 && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Ready to parse {selectedFiles.length} file(s). Click "Next" to continue.
                </Alert>
              )}
            </Box>
          )}

          {activeStep === 1 && parsedData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Map Data Fields
              </Typography>
              
              {/* Data Summary */}
              <Box sx={{ mb: 3 }}>
                <Alert severity="info">
                  <Typography variant="subtitle2" gutterBottom>
                    Parsed Data Summary:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {parsedData.products && (
                      <Chip 
                        label={`${parsedData.products.length} Products`}
                        color="primary"
                        size="small"
                      />
                    )}
                    {parsedData.recipes && (
                      <Chip 
                        label={`${parsedData.recipes.length} Recipes`}
                        color="secondary"
                        size="small"
                      />
                    )}
                  </Box>
                </Alert>
              </Box>

              <DataMapper
                data={parsedData}
                onMappingComplete={handleMappingComplete}
                onDataTransform={handleDataTransform}
              />
            </Box>
          )}

          {activeStep === 2 && transformedData && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Review & Import
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Review the processed data before importing to the database
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        Import Summary
                      </Typography>
                      
                      <List dense>
                        {transformedData.products && (
                          <ListItem>
                            <ListItemIcon>
                              <CheckCircle color="success" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={`${transformedData.products.length} Products`}
                              secondary="Ready to import"
                            />
                          </ListItem>
                        )}
                        {transformedData.recipes && (
                          <ListItem>
                            <ListItemIcon>
                              <CheckCircle color="success" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={`${transformedData.recipes.length} Recipes`}
                              secondary="Ready to import"
                            />
                          </ListItem>
                        )}
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        Import Actions
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        The import process will:
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemText 
                            primary="• Validate all data entries"
                            secondary="Check required fields and data types"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText 
                            primary="• Create new records"
                            secondary="Import valid entries to the database"
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText 
                            primary="• Report errors"
                            secondary="Show detailed error information for failed imports"
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Navigation */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              onClick={handleBack}
              disabled={activeStep === 0}
            >
              Back
            </Button>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                onClick={handleReset}
              >
                Reset
              </Button>
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceed()}
                startIcon={
                  activeStep === 0 ? <FileUploadIcon /> :
                  activeStep === 1 ? <Transform /> :
                  <PlayArrow />
                }
              >
                {activeStep === steps.length - 1 ? 'Start Import' : 'Next'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Container>
    </>
  );
}