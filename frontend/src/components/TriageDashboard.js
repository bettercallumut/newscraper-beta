import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TriageDashboard = () => {
    const [alerts, setAlerts] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const response = await axios.get('/api/alerts');
                setAlerts(response.data);
            } catch (err) {
                setError('Failed to fetch alerts. Is the backend running?');
                console.error(err);
            }
        };

        fetchAlerts();
        const interval = setInterval(fetchAlerts, 30000); // Poll every 30 seconds
        return () => clearInterval(interval);
    }, []);

    if (error) {
        return <div><p style={{ color: 'red' }}>{error}</p></div>;
    }

    if (alerts.length === 0) {
        return <div><p>No high-value alerts pending review. The system is monitoring...</p></div>;
    }

    return (
        <div>
            <h2>Triage Dashboard</h2>
            {alerts.map(alert => (
                <div key={alert.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
                    <h3>{alert.headline}</h3>
                    <p><strong>Source:</strong> {alert.source_name}</p>
                    <p><strong>Score:</strong> {alert.news_value_score}</p>
                    <p>{alert.summary}</p>
                    <button>Approve & Post</button>
                    <button>Dismiss</button>
                </div>
            ))}
        </div>
    );
};

export default TriageDashboard;