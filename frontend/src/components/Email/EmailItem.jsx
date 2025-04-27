import React from 'react';
import { MdStar, MdStarBorder } from 'react-icons/md';

const EmailItem = ({ email }) => {
  const {
    sender_name,
    subject,
    content,
    date,
    read,
    important
  } = email;
  
  // 날짜 포맷팅
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // 오늘 날짜인 경우 시간만 표시
    if (date.toDateString() === today.toDateString()) {
      return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
    }
    
    // 어제인 경우 '어제'로 표시
    if (date.toDateString() === yesterday.toDateString()) {
      return '어제';
    }
    
    // 그 외에는 월/일 표시
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };
  
  return (
    <div className={`email-item ${!read ? 'unread' : ''}`}>
      <div className="email-item-content">
        <div className="email-item-header">
          <span className="email-sender">{sender_name}</span>
          <span className="email-date">{formatDate(date)}</span>
        </div>
        <div className="email-subject">{subject}</div>
        <div className="email-preview">{content}</div>
      </div>
      <div className="email-status">
        {important ? <MdStar color="#FFD700" /> : <MdStarBorder />}
      </div>
    </div>
  );
};

export default EmailItem;