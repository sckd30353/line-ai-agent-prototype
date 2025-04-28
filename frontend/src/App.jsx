import React, { useState, useEffect } from 'react';
import ChatContainer from './components/Chat/ChatContainer';
import ChatInput from './components/Chat/ChatInput';
import EmailButton from './components/Email/EmailButton';
import EmailList from './components/Email/EmailList';
import { sendMessage } from './api';
import './styles/index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showEmailList, setShowEmailList] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  
  // 메시지 전송 처리 함수
  const handleSendMessage = async (text) => {
    if (!text.trim()) return;
    
    // 사용자 메시지 추가
    const userMessage = {
      id: Date.now(),
      text,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    
    try {
      // 백엔드 API 호출
      const response = await sendMessage(text, conversationId);
      
      // AI 응답 추가
      const aiResponse = {
        id: Date.now() + 1,
        text: response.message,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // 대화 ID 저장
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
    } catch (error) {
      console.error('메시지 전송 오류:', error);
      
      // 오류 메시지 추가
      const errorMessage = {
        id: Date.now() + 1,
        text: '메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.',
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  // 이메일 버튼 토글 함수
  const toggleEmailList = () => {
    setShowEmailList(prev => !prev);
  };
  
  return (
    <div className="app">
      <header className="header">
        <div className="header-logo">
          <img src="/line-icon.svg" alt="Line" className="line-icon" />
          <h1>Line AI Agent</h1>
        </div>
      </header>
      
      <main className="main-content">
        <ChatContainer messages={messages} loading={loading} />
        
        <EmailButton onClick={toggleEmailList} />
        
        {showEmailList && (
          <EmailList onClose={toggleEmailList} />
        )}
      </main>
      
      <footer className="footer">
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
      </footer>
    </div>
  );
}

export default App;