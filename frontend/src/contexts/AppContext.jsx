import React, { createContext, useState, useContext, useEffect } from 'react';
import { sendMessage, getEmails } from '../api';

// Context 생성
const AppContext = createContext();

// Context Provider 컴포넌트
export const AppProvider = ({ children }) => {
  // 채팅 관련 상태
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // 이메일 관련 상태
  const [emails, setEmails] = useState([]);
  const [emailsLoading, setEmailsLoading] = useState(false);
  
  // 이메일 데이터 로드
  useEffect(() => {
    const loadEmails = async () => {
      setEmailsLoading(true);
      try {
        const data = await getEmails();
        setEmails(data);
      } catch (error) {
        console.error('이메일 로드 오류:', error);
      } finally {
        setEmailsLoading(false);
      }
    };
    
    loadEmails();
  }, []);
  
  // 메시지 전송 함수
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
      // API 호출
      const response = await sendMessage(text, conversationId);
      
      // 응답 메시지 추가
      const aiResponse = {
        id: Date.now() + 1,
        text: response.message,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiResponse]);
      
      // 대화 ID 설정 (첫 메시지인 경우)
      if (!conversationId && response.conversation_id) {
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
  
  // Context 값
  const value = {
    messages,
    loading,
    handleSendMessage,
    emails,
    emailsLoading
  };
  
  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

// Context 사용을 위한 Custom Hook
export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export default AppContext;