import React from 'react';
import { MdStar, MdStarBorder } from 'react-icons/md';
import { updateEmail } from '../../api';

const EmailItem = ({ email, onRefresh }) => {
  const {
    id,
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
  
  // 중요 표시 토글
  const toggleImportant = async (e) => {
    e.stopPropagation(); // 이벤트 전파 중지
    
    try {
      await updateEmail(id, {
        important: !important
      });
      
      // 목록 새로고침
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('이메일 중요 표시 업데이트 오류:', error);
    }
  };
  
  // 이메일 클릭 시 읽음 상태로 변경
  const handleClick = async () => {
    if (!read) {
      try {
        await updateEmail(id, {
          read: true
        });
        
        // 목록 새로고침
        if (onRefresh) onRefresh();
      } catch (error) {
        console.error('이메일 읽음 상태 업데이트 오류:', error);
      }
    }
    
    // 이메일 상세 보기 등의 추가 기능 구현 가능
  };
  
  return (
    <div 
      className={`email-item ${!read ? 'unread' : ''}`} 
      onClick={handleClick}
    >
      <div className="email-item-content">
        <div className="email-item-header">
          <span className="email-sender">{sender_name}</span>
          <span className="email-date">{formatDate(date)}</span>
        </div>
        <div className="email-subject">{subject}</div>
        <div className="email-preview">{content}</div>
      </div>
      <div className="email-status">
        {important ? (
          <MdStar 
            color="#FFD700" 
            onClick={toggleImportant} 
          />
        ) : (
          <MdStarBorder 
            onClick={toggleImportant} 
          />
        )}
      </div>
    </div>
  );
};

export default EmailItem;