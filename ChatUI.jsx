// ChatUI.jsx
import React, { useState } from 'react';
import axios from 'axios';
import { Box, Paper } from '@mui/material';
import ChatMessages from './ChatMessege';
import ChatInput from './ChatInput';

const steps = [
  { key: 'start', question: 'שלום! האם ברצונך לקבוע תור לרופא? כתוב "כן" כדי להתחיל.' },
  { key: 'user_id', question: 'מה מספר תעודת הזהות של הפציינט?' },
   { key: 'phon', question: 'נא להכניס טלפון ' },
  { key: 'email', question: 'נא להכניס מייל' },
  { key: 'date', question: 'מה התאריך שבו תרצה לקבוע תור? (למשל: 2025-05-13)' },
  { key: 'start_time', question: 'ובאיזו שעה? (למשל: 09:30)' }
];


const isValidDate = (str) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(str)) return false;
  const date = new Date(str);
  const [y, m, d] = str.split('-').map(Number);
  return (
    date.getFullYear() === y &&
    date.getMonth() + 1 === m &&
    date.getDate() === d
  );
};

const isValidTime = (str) => {
  if (!/^\d{2}:\d{2}$/.test(str)) return false;
  const [hour, minute] = str.split(':').map(Number);
  return hour >= 0 && hour < 24 && minute >= 0 && minute < 60;
};

const detectLanguage = (text) => /[\u0590-\u05FF]/.test(text) ? 'he' : 'en';
const isValidIsraeliID = (id) => {
  if (!/^\d{9}$/.test(id)) return false;
  const digits = id.split('').map(Number);
  const sum = digits
    .map((d, i) => {
      const val = i % 2 === 0 ? d : d * 2;
      return val > 9 ? val - 9 : val;
    })
    .reduce((acc, curr) => acc + curr, 0);
  return sum % 10 === 0;
};
const isValidPhoneNumber = (phone) => {
  const cleaned = phone.replace(/[-\s]/g, '');
  return /^05\d{8}$/.test(cleaned); // למשל: 0501234567
};

 const validateEmail = (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  };



export const ChatUI = () => {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: steps[0].question }
  ]);
  const [input, setInput] = useState('');
  const [stepIndex, setStepIndex] = useState(0);
  const [formData, setFormData] = useState({});

  const sendMessage = async () => {
    if (!input.trim()) return;

    const currentStep = steps[stepIndex];
    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);

    if (currentStep.key === 'start' && (input.trim().toLowerCase() !== 'כן' && input.trim().toLowerCase())) {
      setMessages([...newMessages, { sender: 'bot', text: 'כדי להתחיל יש לרשום "כן"' }]);
      return;
    }

    if (currentStep.key === 'user_id' && !isValidIsraeliID(input)) {
      setMessages([...newMessages, { sender: 'bot', text: 'תעודת הזהות אינה תקינה. יש להזין 9 ספרות תקפות.' }]);
      return;
    }
    if (currentStep.key === 'phon' && !isValidPhoneNumber(input)) {
  setMessages([...newMessages, { sender: 'bot', text: 'מספר טלפון אינו תקין. נא להזין מספר תקני בפורמט 05XXXXXXXX' }]);
  return;
}
     if (currentStep.key === 'email' && !validateEmail(input)) {
  setMessages([...newMessages, { sender: 'bot', text: 'המייל לא תקין ' }]);
  return;

}
    // Validation
    if (currentStep.key === 'date' && !isValidDate(input)) {
      const lang = detectLanguage(input);
      setMessages([...newMessages, { sender: 'bot', text: lang === 'he' ? 'Please enter the date in format YYYY-MM-DD' : 'יש להזין תאריך בפורמט YYYY-MM-DD' }]);
      return;
    }
    if (currentStep.key === 'date') {
      const selectedDate = new Date(`${input}T00:00`);
      const now = new Date();
      if (selectedDate < now.setHours(0, 0, 0, 0)) {
        setMessages([...newMessages, { sender: 'bot', text: 'תאריך זה כבר עבר. אנא בחר תאריך עתידי.' }]);
        return;
      }
    }

    if (currentStep.key === 'start_time' && !isValidTime(input)) {
      const lang = detectLanguage(input);
      setMessages([...newMessages, { sender: 'bot', text: lang === 'he' ? 'יש להזין שעה בפורמט HH:MM' : 'Please enter the time in format HH:MM' }]);
      return;
    }
    if (currentStep.key === 'start_time') {
      const fullDateTime = new Date(`${formData.date}T${input}`);
      if (fullDateTime < new Date()) {
        setMessages([...newMessages, { sender: 'bot', text: 'השעה שציינת כבר עברה. אנא בחר מועד עתידי.' }]);
        return;
      }
    }

    setFormData(prev => ({ ...prev, [currentStep.key]: input }));
    setInput('');

    if (stepIndex < steps.length - 1) {
      setStepIndex(stepIndex + 1);
      setMessages(prev => [...prev, { sender: 'bot', text: steps[stepIndex + 1].question }]);
    } else {
      try {
        const res = await axios.post('http://127.0.0.1:5000/appointments', {
          ...formData,
          [currentStep.key]: input,
          duration: 30,
          tz: 'Asia/Jerusalem'
        });

        const appointmentTime = new Date(`${formData.date}T${input}`);
        setMessages(prev => [...prev, {
          sender: 'bot',
          text: `תור נקבע בהצלחה ל-${appointmentTime.toLocaleString('he-IL')}`
        }]);
      } catch (error) {
        const message = error.response?.data?.error || 'אירעה שגיאה.';
        const status = error.response?.status;

        if (status === 409) {
          if (message.includes('התור כבר נקבע')) {
            // חוזרים לבחירת תאריך
            setStepIndex(4); // index של 'date'
            setMessages(prev => [...prev, {
              sender: 'bot',
              text: 'התאריך והשעה שבחרת כבר תפוסים. נסה תאריך אחר:'
            }]);
            return;
          }

          if (message.includes('מחוץ לשעות הפעילות')) {
            // חוזרים לבחירת שעה
            setStepIndex(5); // index של 'start_time'
            setMessages(prev => [...prev, {
              sender: 'bot',
              text: 'השעה שבחרת מחוץ לשעות הפעילות. אנא הזן שעה אחרת:'
            }]);
            return;
          }
        }

        // טיפול בשגיאות אחרות
        setMessages(prev => [...prev, { sender: 'bot', text: message }]);
        return;
      }

      // Reset the form
      setFormData({});
      setStepIndex(0);
      setMessages(prev => [...prev, { sender: 'bot', text: steps[0].question }]);
    }
  };

  return (
    <Box dir="rtl" sx={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: '#fff', padding: 2 }}>
      <Paper elevation={0} sx={{ width: '100%', maxWidth: '800px', height: '90vh', display: 'flex', flexDirection: 'column', padding: 2, boxSizing: 'border-box' }}>
        <ChatMessages messages={messages} />
        <ChatInput
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
          currentStep={steps[stepIndex]}
        />
      </Paper>
    </Box>
  );
}

export default ChatUI;
