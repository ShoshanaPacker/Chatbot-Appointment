import React from 'react';
import { Box, TextField, IconButton } from '@mui/material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import dayjs from 'dayjs';

export default function ChatInput({ input, setInput, sendMessage, currentStep }) {
  const handleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('הדפדפן שלך לא תומך בזיהוי קולי');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'he-IL';

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
    };

    recognition.start();
  };

  const handleDateChange = (newValue) => {
    if (newValue) {
      setInput(dayjs(newValue).format('YYYY-MM-DD'));
    }
  };

  const handleTimeChange = (newValue) => {
    if (newValue) {
      setInput(dayjs(newValue).format('HH:mm'));
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', paddingTop: 1 }}>
      {currentStep.key === 'date' ? (
        <DatePicker
          label="בחר תאריך"
          value={input ? dayjs(input) : null}
          onChange={handleDateChange}
          format="YYYY-MM-DD"
          disablePast
          slotProps={{ textField: { fullWidth: true } }}
        />
      ) : currentStep.key === 'start_time' ? (
        <TimePicker
          label="בחר שעה"
          value={input ? dayjs(`2000-01-01T${input}`) : null}
          onChange={handleTimeChange}
          format="HH:mm"
          ampm={false}
          slotProps={{ textField: { fullWidth: true } }}
        />
      ) : (
      <TextField
  variant="outlined"
  value={input}
  onChange={(e) => setInput(e.target.value)}
  onKeyDown={(e) => {
    if (e.key === 'Enter' && input.trim()) {
      e.preventDefault();
      sendMessage();
    }
  }}
  fullWidth
  label="הקלד או דבר..."
/>



      )}
      <IconButton color="primary" onClick={sendMessage} disabled={!input.trim()}>
        <SendIcon />
      </IconButton>
      <IconButton color="secondary" onClick={handleVoiceInput}>
        <MicIcon />
      </IconButton>
    </Box>
  );
}




// import React from 'react';
// import { Box, TextField, IconButton } from '@mui/material';
// import SendIcon from '@mui/icons-material/Send';
// import MicIcon from '@mui/icons-material/Mic';

// export default function ChatInput({ input, setInput, sendMessage }) {
//   const handleVoiceInput = () => {
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
//     if (!SpeechRecognition) {
//       alert('הדפדפן שלך לא תומך בזיהוי קולי');
//       return;
//     }

//     const recognition = new SpeechRecognition();
//     recognition.lang = 'he-IL'; // עברית

//     recognition.onresult = (event) => {
//       const transcript = event.results[0][0].transcript;
//       setInput(transcript);
//     };

//     recognition.start();
//   };

//   return (
//     <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', paddingTop: 1 }}>
//       <TextField
//         variant="outlined"
//         value={input}
//         onChange={(e) => setInput(e.target.value)}
//         fullWidth
//         label="הקלד או דבר..."
//       />
//       <IconButton color="primary" onClick={sendMessage} disabled={!input.trim()}>
//         <SendIcon />
//       </IconButton>
//       <IconButton color="secondary" onClick={handleVoiceInput}>
//         <MicIcon />
//       </IconButton>
//     </Box>
//   );
// }
