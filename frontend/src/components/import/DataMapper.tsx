import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid
} from '@mui/material';
import {
  ExpandMore,
  Transform,
  CheckCircle,
  Error
} from '@mui/icons-material';

import { ImportData, ImportMapping } from '@/services/importService';

interface DataMapperProps {
  data: ImportData;
  onMappingComplete: (mappings: ImportMapping[]) => void;
  onDataTransform: (transformedData: ImportData) => void;
}

interface FieldMapping {
  sourceField: string;
  targetField: string;
  required: boolean;
  dataType: 'string' | 'number' | 'boolean' | 'array';
  sampleValue?: any;
}

export default function DataMapper({
  data,
  onMappingComplete,
  onDataTransform
}: DataMapperProps) {
  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [autoMap, setAutoMap] = useState(true);

  // Define target schemas
  const productSchema = [
    { field: 'name', required: true, type: 'string', description: 'Product name' },
    { field: 'symbol', required: true, type: 'string', description: 'Product symbol (unique identifier)' },
    { field: 'type', required: true, type: 'string', description: 'Product type (standard, semi-product, kit)' },
    { field: 'unit', required: true, type: 'string', description: 'Unit (piece, gram)' },
    { field: 'description', required: false, type: 'string', description: 'Product description' },
    { field: 'category', required: false, type: 'string', description: 'Product category' },
    { field: 'tags', required: false, type: 'array', description: 'Product tags (comma-separated)' }
  ];

  const recipeSchema = [
    { field: 'product_name', required: true, type: 'string', description: 'Product name for the recipe' },
    { field: 'yield_quantity', required: true, type: 'number', description: 'Recipe yield quantity' },
    { field: 'yield_unit', required: true, type: 'string', description: 'Recipe yield unit (piece, gram)' },
    { field: 'ingredients', required: true, type: 'array', description: 'Recipe ingredients' }
  ];

  const currentSchema = data.products ? productSchema : recipeSchema;
  const currentData = data.products || data.recipes || [];

  useEffect(() => {
    if (currentData.length > 0) {
      initializeMappings();
    }
  }, [data]);

  const initializeMappings = () => {
    const firstItem = currentData[0];
    const sourceFields = Object.keys(firstItem);
    
    const initialMappings: FieldMapping[] = [];
    
    // Auto-map fields if enabled
    currentSchema.forEach((schemaField) => {
      let mappedSourceField = '';
      
      if (autoMap) {
        // Try exact match first
        mappedSourceField = sourceFields.find(sf => 
          sf.toLowerCase() === schemaField.field.toLowerCase()
        ) || '';
        
        // Try partial match
        if (!mappedSourceField) {
          mappedSourceField = sourceFields.find(sf => 
            sf.toLowerCase().includes(schemaField.field.toLowerCase()) ||
            schemaField.field.toLowerCase().includes(sf.toLowerCase())
          ) || '';
        }
      }
      
      initialMappings.push({
        sourceField: mappedSourceField,
        targetField: schemaField.field,
        required: schemaField.required,
        dataType: schemaField.type as any,
        sampleValue: mappedSourceField ? firstItem[mappedSourceField] : null
      });
    });
    
    setMappings(initialMappings);
    generatePreview(initialMappings);
  };

  const handleMappingChange = (targetField: string, sourceField: string) => {
    const updatedMappings = mappings.map(mapping => {
      if (mapping.targetField === targetField) {
        const sampleValue = sourceField ? currentData[0][sourceField] : null;
        return {
          ...mapping,
          sourceField,
          sampleValue
        };
      }
      return mapping;
    });
    
    setMappings(updatedMappings);
    generatePreview(updatedMappings);
  };

  const generatePreview = (currentMappings: FieldMapping[]) => {
    try {
      const transformedData = currentData.slice(0, 5).map((item) => {
        const transformedItem: any = {};
        
        currentMappings.forEach((mapping) => {
          if (mapping.sourceField && item[mapping.sourceField] !== undefined) {
            let value = item[mapping.sourceField];
            
            // Apply data type transformations
            switch (mapping.dataType) {
              case 'number':
                value = parseFloat(value) || 0;
                break;
              case 'boolean':
                value = ['true', '1', 'yes', 'on'].includes(String(value).toLowerCase());
                break;
              case 'array':
                value = typeof value === 'string' 
                  ? value.split(',').map(v => v.trim()).filter(v => v)
                  : Array.isArray(value) ? value : [value];
                break;
              case 'string':
              default:
                value = String(value).trim();
                break;
            }
            
            transformedItem[mapping.targetField] = value;
          }
        });
        
        return transformedItem;
      });
      
      setPreviewData(transformedData);
      validateMappings(currentMappings, transformedData);
    } catch (error) {
      console.error('Preview generation failed:', error);
      setValidationErrors(['Failed to generate preview']);
    }
  };

  const validateMappings = (currentMappings: FieldMapping[], preview: any[]) => {
    const errors: string[] = [];
    
    // Check required fields
    currentMappings.forEach((mapping) => {
      if (mapping.required && !mapping.sourceField) {
        errors.push(`Required field "${mapping.targetField}" is not mapped`);
      }
    });
    
    // Check data types and values
    preview.forEach((item, index) => {
      currentMappings.forEach((mapping) => {
        if (mapping.sourceField && item[mapping.targetField] !== undefined) {
          const value = item[mapping.targetField];
          
          switch (mapping.targetField) {
            case 'symbol':
              // Check for symbol uniqueness within the dataset
              const symbolCount = preview.filter(item => item.symbol === value).length;
              if (symbolCount > 1) {
                errors.push(`Row ${index + 1}: Symbol "${value}" must be unique`);
              }
              if (!value || value.trim().length === 0) {
                errors.push(`Row ${index + 1}: Symbol cannot be empty`);
              }
              break;
            case 'type':
              if (!['standard', 'semi-product', 'kit'].includes(value)) {
                errors.push(`Row ${index + 1}: Invalid product type "${value}"`);
              }
              break;
            case 'unit':
            case 'yield_unit':
              if (!['piece', 'gram'].includes(value)) {
                errors.push(`Row ${index + 1}: Invalid unit "${value}"`);
              }
              break;
            case 'yield_quantity':
              if (isNaN(value) || value <= 0) {
                errors.push(`Row ${index + 1}: Yield quantity must be a positive number`);
              }
              break;
          }
        }
      });
    });
    
    setValidationErrors(errors);
  };

  const handleConfirmMapping = () => {
    const finalMappings: ImportMapping[] = mappings
      .filter(m => m.sourceField)
      .map(m => ({
        sourceField: m.sourceField,
        targetField: m.targetField,
        required: m.required,
        transform: m.dataType === 'string' ? 'string' : 
                   m.dataType === 'number' ? 'number' :
                   m.dataType === 'boolean' ? 'boolean' :
                   m.dataType === 'array' ? 'array' : 'string'
      }));
    
    // Transform all data
    const transformedData: ImportData = {};
    
    if (data.products) {
      transformedData.products = data.products.map((item) => {
        const transformed: any = {};
        finalMappings.forEach((mapping) => {
          if (mapping.sourceField && item[mapping.sourceField as keyof typeof item] !== undefined) {
            let value = item[mapping.sourceField as keyof typeof item];
            
            switch (mapping.transform) {
              case 'number':
                transformed[mapping.targetField] = parseFloat(value as any) || 0;
                break;
              case 'boolean':
                transformed[mapping.targetField] = ['true', '1', 'yes', 'on'].includes(String(value).toLowerCase());
                break;
              case 'array':
                transformed[mapping.targetField] = typeof value === 'string' 
                  ? (value as string).split(',').map(v => v.trim()).filter(v => v)
                  : Array.isArray(value) ? value : [value];
                break;
              default:
                transformed[mapping.targetField] = String(value).trim();
                break;
            }
          }
        });
        return transformed;
      });
    }
    
    if (data.recipes) {
      transformedData.recipes = data.recipes.map((item) => {
        const transformed: any = {};
        finalMappings.forEach((mapping) => {
          if (mapping.sourceField && item[mapping.sourceField as keyof typeof item] !== undefined) {
            let value = item[mapping.sourceField as keyof typeof item];
            
            switch (mapping.transform) {
              case 'number':
                transformed[mapping.targetField] = parseFloat(value as any) || 0;
                break;
              default:
                transformed[mapping.targetField] = String(value).trim();
                break;
            }
          }
        });
        return transformed;
      });
    }
    
    onMappingComplete(finalMappings);
    onDataTransform(transformedData);
  };

  const getSourceFields = (): string[] => {
    if (currentData.length === 0) return [];
    return Object.keys(currentData[0]);
  };

  const getMappingStatus = (mapping: FieldMapping): 'success' | 'error' | 'warning' => {
    if (mapping.required && !mapping.sourceField) return 'error';
    if (!mapping.sourceField) return 'warning';
    return 'success';
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Transform />
          Data Field Mapping
        </Typography>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Map your source data fields to the target schema fields. Required fields must be mapped.
        </Typography>

        <FormControlLabel
          control={
            <Switch
              checked={autoMap}
              onChange={(e) => setAutoMap(e.target.checked)}
            />
          }
          label="Auto-map similar field names"
          sx={{ mb: 2 }}
        />

        {/* Field Mapping Table */}
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Status</TableCell>
              <TableCell>Target Field</TableCell>
              <TableCell>Source Field</TableCell>
              <TableCell>Data Type</TableCell>
              <TableCell>Sample Value</TableCell>
              <TableCell>Description</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mappings.map((mapping) => (
              <TableRow key={mapping.targetField}>
                <TableCell>
                  {getMappingStatus(mapping) === 'success' && <CheckCircle color="success" fontSize="small" />}
                  {getMappingStatus(mapping) === 'error' && <Error color="error" fontSize="small" />}
                  {getMappingStatus(mapping) === 'warning' && <Error color="warning" fontSize="small" />}
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {mapping.targetField}
                    </Typography>
                    {mapping.required && (
                      <Chip label="Required" size="small" color="error" variant="outlined" />
                    )}
                  </Box>
                </TableCell>
                
                <TableCell>
                  <FormControl size="small" fullWidth sx={{ minWidth: 150 }}>
                    <Select
                      value={mapping.sourceField}
                      onChange={(e) => handleMappingChange(mapping.targetField, e.target.value)}
                      displayEmpty
                    >
                      <MenuItem value="">
                        <em>Not mapped</em>
                      </MenuItem>
                      {getSourceFields().map((field) => (
                        <MenuItem key={field} value={field}>
                          {field}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </TableCell>
                
                <TableCell>
                  <Chip 
                    label={mapping.dataType}
                    size="small"
                    variant="outlined"
                    icon={<Transform />}
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {mapping.sampleValue ? String(mapping.sampleValue).substring(0, 30) + 
                     (String(mapping.sampleValue).length > 30 ? '...' : '') : '-'}
                  </Typography>
                </TableCell>
                
                <TableCell>
                  <Typography variant="caption" color="text.secondary">
                    {currentSchema.find(s => s.field === mapping.targetField)?.description}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {/* Validation Errors */}
        {validationErrors.length > 0 && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Mapping Issues:
            </Typography>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {validationErrors.map((error, index) => (
                <li key={index}>
                  <Typography variant="body2">{error}</Typography>
                </li>
              ))}
            </ul>
          </Alert>
        )}

        {/* Preview Data */}
        <Accordion sx={{ mt: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle2">
              Preview Transformed Data ({previewData.length} of {currentData.length} items)
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {previewData.length > 0 && (
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      {Object.keys(previewData[0]).map((field) => (
                        <TableCell key={field} sx={{ fontWeight: 600 }}>
                          {field}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {previewData.map((item, index) => (
                      <TableRow key={index}>
                        {Object.entries(item).map(([field, value]) => (
                          <TableCell key={field}>
                            <Typography variant="body2">
                              {Array.isArray(value) ? value.join(', ') : String(value)}
                            </Typography>
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Actions */}
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            onClick={handleConfirmMapping}
            disabled={validationErrors.some(error => error.includes('Required field'))}
            startIcon={<CheckCircle />}
          >
            Confirm Mapping & Continue
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}