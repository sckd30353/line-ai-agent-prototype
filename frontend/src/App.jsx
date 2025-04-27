import React, { useState, useEffect } from 'react';
import ChatContainer from './components/Chat/ChatContainer';
import ChatInput from './components/Chat/ChatInput';
import EmailButton from './components/Email/EmailButton';
import EmailList from './components/Email/EmailList';
import './styles/index.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showEmailList, setShowEmailList] = useState(false);
  
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
      // TODO: API 호출 로직 구현
      // 임시 응답 (API 연동 전까지 사용)
      setTimeout(() => {
        const aiResponse = {
          id: Date.now() + 1,
          text: `이것은 "${text}"에 대한 응답입니다.`,
          sender: 'ai',
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, aiResponse]);
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('메시지 전송 오류:', error);
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
        <h1>Line AI Agent</h1>
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