import React, { useEffect, useState } from 'react';
import { MdClose } from 'react-icons/md';
import EmailItem from './EmailItem';
import { getEmails } from '../../api';

const EmailList = ({ onClose }) => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchEmails = async () => {
      try {
        const data = await getEmails();
        setEmails(data);
      } catch (error) {
        console.error('이메일 로드 오류:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchEmails();
  }, []);
  
  return (
    <div className="email-overlay open">
      <div className="email-header">
        <h2>이메일</h2>
        <button className="close-button" onClick={onClose} aria-label="닫기">
          <MdClose />
        </button>
      </div>
      
      <div className="email-list">
        {loading ? (
          <div className="loading">이메일을 불러오는 중...</div>
        ) : emails.length === 0 ? (
          <div className="empty-list">이메일이 없습니다.</div>
        ) : (
          emails.map((email) => (
            <EmailItem key={email.id} email={email} />
          ))
        )}
      </div>
    </div>
  );
};

export default EmailList;