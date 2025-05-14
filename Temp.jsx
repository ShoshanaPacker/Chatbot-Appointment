import React, { useState } from 'react';
import axios from 'axios';
import { TextField, IconButton, Typography, Box, Paper } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

export default function ChatUITemp() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'שלום! איך אפשר לעזור לך לקבוע תור לרופא?' }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);

    try {
      const [date, time] = input.split(' ');
      const res = await axios.post('http://127.0.0.1:5000/appointments', {
        user_id: '123456789',
        date,
        start_time: time,
        duration: 30,
        tz: 'Asia/Jerusalem'
      });

      const appointmentTime = new Date(`${date}T${time}`);
      setMessages([...newMessages, {
        sender: 'bot',
        text: `תור נקבע בהצלחה ל-${appointmentTime.toLocaleString('he-IL')}`
      }]);
    } catch (error) {
      const message = error.response?.data?.error || 'אירעה שגיאה.';
      setMessages([...newMessages, { sender: 'bot', text: message }]);
    }

    setInput('');
  };

  return (
    <Box
      dir="rtl"
      sx={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        bgcolor: '#fff',
        padding: 2,
      }}
    >
      <Paper
        elevation={0}
        sx={{
          width: '100%',
          maxWidth: '800px',
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
          padding: 2,
          boxSizing: 'border-box',
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            padding: 1,
          }}
        >
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              sx={{
                display: 'flex',
                justifyContent: msg.sender === 'bot' ? 'flex-end' : 'flex-start',
                marginBottom: 1,
              }}
            >
              <Box
                sx={{
                  backgroundColor: msg.sender === 'bot' ? '#e6f0fa' : '#e8fbe6',
                  padding: 1.5,
                  borderRadius: 2,
                  maxWidth: '70%',
                }}
              >
                <Typography variant="body2">
                  {/* <strong>{msg.sender === 'bot' ? '🤖' : '🧑'}:</strong> {msg.text} */}
                  <strong></strong> {msg.text}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>

        <Box
          sx={{
            display: 'flex',
            gap: 1,
            alignItems: 'center',
            paddingTop: 1,
          }}
        >
          <TextField
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            fullWidth
            label="לדוגמה: 2025-05-13 09:30"
          />
          <IconButton
            color="primary"
            onClick={sendMessage}
            disabled={!input.trim()}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
}
