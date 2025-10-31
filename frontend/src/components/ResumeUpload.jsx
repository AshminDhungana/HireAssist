import React, { useState } from 'react';
import { uploadResume } from '../api/resumeService';
import { Upload, Check, AlertCircle, Loader } from 'lucide-react';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messageType, setMessageType] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  // --- Handlers remain the same ---
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage('');
      setMessageType('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      setMessage('');
      setMessageType('');
    }
  };

  const handleSubmit = async () => {
    if (!file) {
      setMessage('❌ Please select a file first');
      setMessageType('error');
      return;
    }

    setIsLoading(true);
    setMessage('');
    setMessageType('');

    try {
      const data = await uploadResume(file);
      setMessage(data.message || '✅ Resume uploaded successfully!');
      setMessageType('success');
      setFile(null);
      setTimeout(() => {
        setMessage('');
        setMessageType('');
      }, 5000);
    } catch (err) {
      setMessage(err.message || '❌ Upload failed. Please try again.');
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };
  // --- End Handlers ---

  return (
    // Standardized max-w 
    <div className="w-full">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        className={`relative border-2 border-dashed rounded-xl p-10 sm:p-16 text-center transition-all duration-300 shadow-inner ${ // Added shadow-inner for depth
          isDragging
            ? 'border-blue-600 bg-blue-50 shadow-blue-200 shadow-xl' // Stronger focus style
            : file
            ? 'border-green-500 bg-white shadow-green-100 shadow-md' // File selected style
            : 'border-gray-300 hover:border-blue-500 bg-gray-50' // Default style
        }`}
      >
        {/* Upload Icon */}
        <div className="flex justify-center mb-4">
          {file ? (
            <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center border-4 border-green-200">
              <Check className="w-8 h-8 text-green-600" />
            </div>
          ) : (
            <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center border-4 border-blue-200 animate-pulse"> 
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
          )}
        </div>

        {/* Text */}
        <p className="text-xl font-extrabold text-gray-900 mb-2">
          {file ? '📄 File Ready for Parsing' : '📁 Drag & Drop Your Resume'}
        </p>
        <p className="text-base text-gray-500 mb-6">
          {file ? `Selected: ${file.name}` : 'or click the button below to browse'}
        </p>

        {/* File Input/Select Button */}
        <label className="inline-block">
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx"
            className="hidden"
          />
          <span className="inline-block px-8 py-3 bg-white text-blue-600 border border-blue-600 font-bold rounded-lg cursor-pointer hover:bg-blue-50 transition-all shadow-md">
            {file ? 'Change File' : 'Select File'}
          </span>
        </label>

        {/* Info Text */}
        <p className="text-xs text-gray-500 mt-6">
          📄 Supported: PDF, DOCX • Files are processed securely
        </p>
      </div>

      {/* Upload Button */}
      <div className="mt-8">
        <button
          onClick={handleSubmit}
          disabled={!file || isLoading}
          // Updated gradient for a more distinct 'action' color, consistent with App.jsx
          className={`w-full py-4 rounded-xl font-extrabold text-lg transition-all shadow-xl flex items-center justify-center gap-2 ${
            !file || isLoading
              ? 'bg-gray-200 text-gray-500 cursor-not-allowed shadow-none'
              : 'bg-gradient-to-r from-green-500 to-teal-600 text-white hover:shadow-2xl hover:scale-[1.01]' // Strong, inviting action color
          }`}
        >
          {isLoading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Upload & Parse Resume
            </>
          )}
        </button>
      </div>

      {/* Messages */}
      {/* Refined message box styling */}
      {message && (
        <div
          className={`mt-6 p-4 rounded-lg flex items-center gap-3 animate-in fade-in transition-all duration-500 ${
            messageType === 'success'
              ? 'bg-green-100 border border-green-400'
              : 'bg-red-100 border border-red-400'
          }`}
        >
          {messageType === 'success' ? (
            <Check className="w-6 h-6 text-green-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
          )}
          <p
            className={`font-semibold ${
              messageType === 'success' ? 'text-green-800' : 'text-red-800'
            }`}
          >
            {message}
          </p>
        </div>
      )}
    </div>
  );
}

export default ResumeUpload;