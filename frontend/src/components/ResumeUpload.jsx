import React, { useState } from 'react';
import { uploadResume } from '../api/resumeService';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = e => setFile(e.target.files[0]);

  const handleSubmit = async () => {
    try {
      const data = await uploadResume(file);
      setMessage(data.message || 'Uploaded successfully');
    } catch (err) {
      setMessage('Upload error');
    }
  };

  return (
    <div className="p-6">
      <input type="file" onChange={handleFileChange} accept=".pdf,.docx" />
      <button onClick={handleSubmit}>Upload</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default ResumeUpload;
