import React, { useRef, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  CloudUpload,
  DragIndicator,
  Delete,
  InsertDriveFile,
  Description,
  Code,
  TableChart
} from '@mui/icons-material';

interface FileUploadProps {
  accept?: string;
  maxSize?: number; // in bytes
  multiple?: boolean;
  onFileSelect: (files: File[]) => void;
  onFileRemove?: (file: File) => void;
  files?: File[];
  loading?: boolean;
  disabled?: boolean;
}

export default function FileUpload({
  accept = '.csv,.json,.xlsx,.xls',
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = false,
  onFileSelect,
  onFileRemove,
  files = [],
  loading = false,
  disabled = false
}: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (disabled || loading) return;

    const droppedFiles = Array.from(e.dataTransfer.files);
    validateAndSelectFiles(droppedFiles);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      validateAndSelectFiles(selectedFiles);
    }
  };

  const validateAndSelectFiles = (fileList: File[]) => {
    const validFiles: File[] = [];
    const errors: string[] = [];

    fileList.forEach((file) => {
      // Check file size
      if (file.size > maxSize) {
        errors.push(`${file.name}: File too large (${formatFileSize(file.size)} > ${formatFileSize(maxSize)})`);
        return;
      }

      // Check file type
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (accept && !accept.split(',').some(type => type.trim() === extension)) {
        errors.push(`${file.name}: Unsupported file type`);
        return;
      }

      validFiles.push(file);
    });

    if (errors.length > 0) {
      setError(errors.join(', '));
    }

    if (validFiles.length > 0) {
      if (!multiple) {
        onFileSelect([validFiles[0]]);
      } else {
        onFileSelect(validFiles);
      }
    }

    // Clear input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = (file: File) => {
    if (onFileRemove) {
      onFileRemove(file);
    }
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'csv':
        return <TableChart />;
      case 'json':
        return <Code />;
      case 'xlsx':
      case 'xls':
        return <Description />;
      default:
        return <InsertDriveFile />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box>
      {/* Drop Zone */}
      <Paper
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          p: 4,
          border: 2,
          borderStyle: 'dashed',
          borderColor: dragActive ? 'primary.main' : 'grey.300',
          backgroundColor: dragActive ? 'primary.50' : (disabled ? 'grey.100' : 'background.paper'),
          cursor: disabled ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            borderColor: disabled ? 'grey.300' : 'primary.light',
            backgroundColor: disabled ? 'grey.100' : 'primary.50'
          }
        }}
        onClick={!disabled && !loading ? handleButtonClick : undefined}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CloudUpload
            sx={{
              fontSize: 48,
              color: dragActive ? 'primary.main' : 'grey.400',
              mb: 2
            }}
          />
          
          <Typography variant="h6" gutterBottom>
            {dragActive ? 'Drop files here' : 'Drag & drop files here'}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            or click to browse files
          </Typography>
          
          <Typography variant="caption" color="text.secondary">
            Supported formats: {accept.split(',').join(', ')} • Max size: {formatFileSize(maxSize)}
          </Typography>

          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Processing files...
              </Typography>
            </Box>
          )}
        </Box>

        <input
          ref={fileInputRef}
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={disabled || loading}
        />
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {/* Selected Files */}
      {files.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Selected Files ({files.length})
          </Typography>
          
          <List dense>
            {files.map((file, index) => (
              <ListItem
                key={`${file.name}-${index}`}
                sx={{
                  border: 1,
                  borderColor: 'grey.200',
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: 'background.paper'
                }}
              >
                <ListItemIcon>
                  {getFileIcon(file.name)}
                </ListItemIcon>
                
                <ListItemText
                  primary={file.name}
                  secondary={
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mt: 0.5 }}>
                      <Chip
                        label={formatFileSize(file.size)}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={file.type || 'Unknown'}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`Modified: ${file.lastModified ? new Date(file.lastModified).toLocaleDateString() : 'Unknown'}`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  }
                />
                
                {onFileRemove && !loading && (
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => handleRemoveFile(file)}
                      size="small"
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                )}
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Additional Actions */}
      <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button
          variant="outlined"
          size="small"
          onClick={handleButtonClick}
          disabled={disabled || loading}
          startIcon={<CloudUpload />}
        >
          Choose Files
        </Button>
        
        {files.length > 0 && onFileRemove && (
          <Button
            variant="outlined"
            size="small"
            color="error"
            onClick={() => files.forEach(handleRemoveFile)}
            disabled={loading}
            startIcon={<Delete />}
          >
            Remove All
          </Button>
        )}
      </Box>
    </Box>
  );
}