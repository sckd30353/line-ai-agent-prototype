import React from 'react';

const ChatBubble = ({ message }) => {
  const { text, sender, timestamp } = message;
  const isUser = sender === 'user';
  
  // 타임스탬프 포맷팅
  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return `오후 ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
  };
  
  return (
    <div className={`message-group ${isUser ? 'user' : 'ai'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'ai'}`}>
        {!isUser && (
          <div className="avatar">
            <img src="https://via.placeholder.com/36" alt="AI Avatar" />
          </div>
        )}
        <div className="message-content">{text}</div>
      </div>
      <div className={`timestamp ${isUser ? 'user' : 'ai'}`}>
        {formatTime(timestamp)}
      </div>
    </div>
  );
};

export default ChatBubble;