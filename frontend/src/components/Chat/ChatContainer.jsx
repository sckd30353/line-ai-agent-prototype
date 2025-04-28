import React, { useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';

const ChatContainer = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);
  
  // 새 메시지가 추가될 때마다 스크롤을 맨 아래로 이동
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // 오늘 날짜 포맷팅
  const getTodayDate = () => {
    const date = new Date();
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    const dayOfWeek = days[date.getDay()];
    return `${date.getMonth() + 1}월 ${date.getDate()}일 (${dayOfWeek})`;
  };
  
  return (
    <div className="chat-container">
      <div className="messages-list">
        {messages.length === 0 ? (
          <div className="empty-chat">
            <h2>프로토타입 기능 소개</h2>
            <p></p>
            <ul>
              <li>웹 검색을 통한 정보 찾기</li>
              <li>이메일 관리 및 조회</li>
              <li>일상 대화 및 질문 응답</li>
            </ul>
          </div>
        ) : (
          <>
            {/* 채팅이 있을 때만 날짜 표시 */}
            <div className="date-divider">
              <span>{getTodayDate()}</span>
            </div>
            
            {/* 메시지 목록 */}
            {messages.map((message) => (
              <ChatBubble key={message.id} message={message} />
            ))}
          </>
        )}
        
        {loading && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatContainer;