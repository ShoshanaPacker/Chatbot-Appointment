import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';

export default function ChatMessages({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    // גולל לתחתית בכל עדכון הודעה
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box sx={{ flexGrow: 1, overflowY: 'auto', padding: 1 }}>
      {messages.map((msg, idx) => (
        <Box
          key={idx}
          sx={{
            display: 'flex',
            justifyContent: msg.sender === 'bot' ? 'flex-end' : 'flex-start',
            marginBottom: 1,
          }}
        >
          <Box sx={{ backgroundColor: msg.sender === 'bot' ? '#e6f0fa' : '#e8fbe6', padding: 1.5, borderRadius: 2, maxWidth: '70%' }}>
            <Typography variant="body2">{msg.text}</Typography>
          </Box>
        </Box>
      ))}
      <div ref={endRef} />
    </Box>
  );
}



// import React from 'react';
// import { Box, Typography } from '@mui/material';

// export default function ChatMessages({ messages }) {
//   return (
//     <Box sx={{ flexGrow: 1, overflowY: 'auto', padding: 1 }}>
//       {messages.map((msg, idx) => (
//         <Box
//           key={idx}
//           sx={{
//             display: 'flex',
//             justifyContent: msg.sender === 'bot' ? 'flex-end' : 'flex-start',
//             marginBottom: 1,
//           }}
//         >
//           <Box
//             sx={{
//               backgroundColor: msg.sender === 'bot' ? '#e6f0fa' : '#e8fbe6',
//               padding: 1.5,
//               borderRadius: 2,
//               maxWidth: '70%',
//             }}
//           >
//             <Typography variant="body2">{msg.text}</Typography>
//           </Box>
//         </Box>
//       ))}
//     </Box>
//   );
// }
