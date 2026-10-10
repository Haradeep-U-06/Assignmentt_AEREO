import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Download, Plus, Trash2, Loader2, RefreshCw, Upload, Award, CheckCircle2, AlertCircle, FileText } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface Recipient {
  recipient_name: string;
  email: string;
  course_name: string;
}

interface Certificate {
  id: number;
  recipient_name: string;
  email: string;
  course_name: string;
  status: string;
  error_message?: string;
}

interface Job {
  id: number;
  status: string;
  created_at: string;
  certificates: Certificate[];
}

function App() {
  const [recipients, setRecipients] = useState<Recipient[]>([
    { recipient_name: '', email: '', course_name: '' }
  ]);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedCourse, setSelectedCourse] = useState<string>('All');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Polling for job status
  useEffect(() => {
    let interval: number;
    if (currentJob && ['pending', 'processing'].includes(currentJob.status)) {
      interval = window.setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE_URL}/jobs/${currentJob.id}`);
          setCurrentJob(res.data);
        } catch (err) {
          console.error("Failed to poll status", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [currentJob?.status, currentJob?.id]);

  const handleAddRecipient = () => {
    setRecipients([...recipients, { recipient_name: '', email: '', course_name: '' }]);
  };

  const handleRemoveRecipient = (index: number) => {
    setRecipients(recipients.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: keyof Recipient, value: string) => {
    const newRecipients = [...recipients];
    newRecipients[index][field] = value;
    setRecipients(newRecipients);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    const validRecipients = recipients.filter(
      r => r.recipient_name.trim() !== '' && r.email.trim() !== '' && r.course_name.trim() !== ''
    );

    if (validRecipients.length === 0) {
      setError("Please fill out at least one recipient completely.");
      setIsLoading(false);
      return;
    }

    try {
      const res = await axios.post(`${API_BASE_URL}/jobs/`, { recipients: validRecipients });
      setCurrentJob(res.data);
      setSelectedCourse('All');
      setRecipients([{ recipient_name: '', email: '', course_name: '' }]);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit request.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE_URL}/jobs/upload/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCurrentJob(res.data);
      setSelectedCourse('All');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to upload and process file.");
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const downloadCertificate = (id: number, name: string) => {
    window.open(`${API_BASE_URL}/certificates/${id}/download`, '_blank');
  };

  const startNewJob = () => {
    setCurrentJob(null);
  };

  const groupedCertificates = currentJob?.certificates.reduce((acc, cert) => {
    const course = cert.course_name || 'Unknown Course';
    if (!acc[course]) acc[course] = [];
    acc[course].push(cert);
    return acc;
  }, {} as Record<string, Certificate[]>) || {};

  const courses = Object.keys(groupedCertificates);

  return (
    <div className="container animate-fade-in">
      <div className="mb-12">
        <h1 className="text-3xl mb-2">Bulk Certificate Generator</h1>
        <p className="text-muted text-sm">Issue and manage certificates instantly via Supabase.</p>
      </div>

      {error && (
        <div className="glass-card mb-8 animate-fade-in flex items-center gap-3" style={{ borderLeft: '4px solid var(--error)', padding: '16px 24px' }}>
          <AlertCircle className="text-error" size={24} />
          <p className="text-error font-medium">{error}</p>
        </div>
      )}

      {!currentJob ? (
        <div className="glass-card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-medium text-white">
              New Request
            </h2>
            
            <div>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileUpload} 
                accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" 
                style={{ display: 'none' }} 
              />
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
                Bulk Upload (CSV/Excel)
              </button>
            </div>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="table-container mb-6">
              <table>
                <thead>
                  <tr>
                    <th>Recipient Name</th>
                    <th>Email Address</th>
                    <th>Course Name</th>
                    <th style={{ width: '60px' }}></th>
                  </tr>
                </thead>
                <tbody>
                  {recipients.map((rec, index) => (
                    <tr key={index}>
                      <td>
                        <input
                          type="text"
                          placeholder="John Doe"
                          value={rec.recipient_name}
                          onChange={(e) => handleChange(index, 'recipient_name', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          type="email"
                          placeholder="john@example.com"
                          value={rec.email}
                          onChange={(e) => handleChange(index, 'email', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          type="text"
                          placeholder="Master of Design"
                          value={rec.course_name}
                          onChange={(e) => handleChange(index, 'course_name', e.target.value)}
                          required
                        />
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        {recipients.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveRecipient(index)}
                            className="btn btn-secondary"
                            style={{ padding: '10px', color: 'var(--error)' }}
                            title="Remove row"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex justify-between items-center">
              <button
                type="button"
                onClick={handleAddRecipient}
                className="btn btn-secondary"
              >
                <Plus size={18} /> Add Row
              </button>
              
              <button
                type="submit"
                className="btn"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Generating...
                  </>
                ) : (
                  "Generate Certificates"
                )}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="glass-card animate-fade-in">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-2xl mb-2 flex items-center gap-3">
                Job Status: 
                <span className={`badge ${currentJob.status}`}>
                  {['pending', 'processing'].includes(currentJob.status) && <Loader2 size={14} className="animate-spin" />}
                  {currentJob.status.replace('_', ' ')}
                </span>
              </h2>
              <p className="text-muted text-sm">Job ID: #{currentJob.id} &bull; Started at: {new Date(currentJob.created_at).toLocaleString()}</p>
            </div>
            {['completed', 'completed_with_errors'].includes(currentJob.status) ? (
              <button onClick={startNewJob} className="btn btn-secondary">
                <RefreshCw size={16} /> New Job
              </button>
            ) : (
              <div className="flex items-center gap-2 text-primary bg-primary/10 px-4 py-2 rounded-full font-medium text-sm animate-pulse">
                Processing...
              </div>
            )}
          </div>

          {courses.length > 1 && (
            <div className="flex gap-3 mb-8 overflow-x-auto pb-2" style={{ scrollbarWidth: 'none' }}>
              <button 
                onClick={() => setSelectedCourse('All')}
                className={`btn ${selectedCourse === 'All' ? '' : 'btn-secondary'}`}
                style={{ padding: '8px 20px', borderRadius: '9999px', fontSize: '0.875rem' }}
              >
                All Courses
              </button>
              {courses.map(course => (
                <button 
                  key={course}
                  onClick={() => setSelectedCourse(course)}
                  className={`btn ${selectedCourse === course ? '' : 'btn-secondary'}`}
                  style={{ padding: '8px 20px', borderRadius: '9999px', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
                >
                  {course}
                  <span style={{ 
                    background: selectedCourse === course ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.1)', 
                    padding: '2px 8px', 
                    borderRadius: '9999px', 
                    marginLeft: '8px',
                    fontSize: '0.75rem'
                  }}>
                    {groupedCertificates[course].length}
                  </span>
                </button>
              ))}
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {Object.entries(groupedCertificates)
              .filter(([course]) => selectedCourse === 'All' || selectedCourse === course)
              .map(([course, certs]) => (
              <div key={course} className="glass-card animate-fade-in" style={{ padding: '24px', background: 'rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-white">
                    {course}
                  </h3>
                  <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#a1a1aa' }}>
                    {certs.length} {certs.length === 1 ? 'Recipient' : 'Recipients'}
                  </span>
                </div>
                
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Recipient Details</th>
                        <th>Status</th>
                        <th style={{ textAlign: 'right' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {certs.map(cert => (
                        <tr key={cert.id}>
                          <td>
                            <div style={{ fontWeight: 500, color: '#fff', marginBottom: '2px' }}>{cert.recipient_name}</div>
                            <div className="text-muted text-sm">{cert.email}</div>
                          </td>
                          <td>
                            <span className={`badge ${cert.status}`}>
                              {cert.status === 'processing' && <Loader2 size={12} className="animate-spin" />}
                              {cert.status}
                            </span>
                            {cert.error_message && (
                              <div className="text-error" style={{ fontSize: '0.75rem', marginTop: '6px', maxWidth: '200px' }}>
                                {cert.error_message}
                              </div>
                            )}
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            {cert.status === 'generated' ? (
                              <button
                                onClick={() => downloadCertificate(cert.id, cert.recipient_name)}
                                className="btn btn-secondary"
                                style={{ padding: '8px 16px', fontSize: '0.875rem' }}
                              >
                                <Download size={14} /> Download
                              </button>
                            ) : (
                              <span className="text-muted text-sm px-4">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
