import React, { useState } from 'react';
import { uploadResume } from '../api/resumeService';
import { Upload, Check, AlertCircle, Loader } from 'lucide-react';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messageType, setMessageType] = useState('');
  const [isDragging, setIsDragging] = useState(false);

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

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
          isDragging
            ? 'border-blue-500 bg-blue-50 shadow-lg scale-105'
            : file
            ? 'border-green-400 bg-green-50'
            : 'border-gray-300 hover:border-blue-500 bg-gray-50'
        }`}
      >
        {/* Upload Icon */}
        <div className="flex justify-center mb-4">
          {file ? (
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
              <Check className="w-8 h-8 text-green-600" />
            </div>
          ) : (
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center animate-bounce">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
          )}
        </div>

        {/* Text */}
        <p className="text-xl font-semibold text-gray-900 mb-2">
          {file ? '📄 File Selected' : '📁 Drag & Drop Your Resume'}
        </p>
        <p className="text-sm text-gray-600 mb-6">
          {file ? file.name : 'or click below to browse'}
        </p>

        {/* File Input */}
        <label className="inline-block">
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx"
            className="hidden"
          />
          <span className="inline-block px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-lg cursor-pointer hover:shadow-lg hover:scale-105 transition-all">
            Select File
          </span>
        </label>

        {/* File Info */}
        {file && (
          <div className="mt-6 p-4 bg-white rounded-lg border border-green-200 inline-block">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">File:</span> {file.name}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Size: {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        )}

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
          className={`w-full py-4 rounded-lg font-bold text-lg transition-all flex items-center justify-center gap-2 ${
            !file || isLoading
              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-600 to-emerald-600 text-white hover:shadow-xl hover:scale-105'
          }`}
        >
          {isLoading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Uploading & Parsing...
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
      {message && (
        <div
          className={`mt-8 p-6 rounded-lg flex items-center gap-3 animate-in fade-in ${
            messageType === 'success'
              ? 'bg-green-50 border border-green-300'
              : messageType === 'error'
              ? 'bg-red-50 border border-red-300'
              : 'bg-blue-50 border border-blue-300'
          }`}
        >
          {messageType === 'success' && (
            <Check className="w-6 h-6 text-green-600 flex-shrink-0" />
          )}
          {messageType === 'error' && (
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
          )}
          <p
            className={`font-medium ${
              messageType === 'success'
                ? 'text-green-800'
                : messageType === 'error'
                ? 'text-red-800'
                : 'text-blue-800'
            }`}
          >
            {message}
          </p>
        </div>
      )}

      {/* Features */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-white rounded-lg shadow-md border-l-4 border-blue-600">
          <div className="text-2xl font-bold text-blue-600 mb-2">⚡</div>
          <p className="font-semibold text-gray-900">Fast Parsing</p>
          <p className="text-sm text-gray-600 mt-1">Process resumes in seconds</p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md border-l-4 border-purple-600">
          <div className="text-2xl font-bold text-purple-600 mb-2">🎯</div>
          <p className="font-semibold text-gray-900">Accurate Extraction</p>
          <p className="text-sm text-gray-600 mt-1">Extract skills, experience & more</p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md border-l-4 border-green-600">
          <div className="text-2xl font-bold text-green-600 mb-2">🔒</div>
          <p className="font-semibold text-gray-900">Secure & Private</p>
          <p className="text-sm text-gray-600 mt-1">Your data is safe with us</p>
        </div>
      </div>
    </div>
  );
}

export default ResumeUpload;
