import React, { useEffect, useState } from 'react';
import { MdClose, MdInbox, MdReportProblem, MdStar } from 'react-icons/md';
import EmailItem from './EmailItem';
import { getEmails } from '../../api';

const EmailList = ({ onClose }) => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    category: null,
    important: null,
    read: null
  });
  
  // 이메일 데이터 로드
  const fetchEmails = async () => {
    try {
      setLoading(true);
      const data = await getEmails(filter);
      setEmails(data);
    } catch (error) {
      console.error('이메일 로드 오류:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 필터 변경 시 이메일 다시 로드
  useEffect(() => {
    fetchEmails();
  }, [filter]);
  
  // 필터 변경 핸들러
  const handleFilterChange = (type, value) => {
    // 이미 선택된 필터를 다시 클릭하면 필터 해제
    if (filter[type] === value) {
      setFilter({ ...filter, [type]: null });
    } else {
      setFilter({ ...filter, [type]: value });
    }
  };
  
  return (
    <div className="email-overlay open">
      <div className="email-header">
        <h2>이메일</h2>
        <button className="close-button" onClick={onClose} aria-label="닫기">
          <MdClose />
        </button>
      </div>
      
      <div className="email-filters">
        <button 
          className={`filter-button ${filter.category === 'inbox' ? 'active' : ''}`}
          onClick={() => handleFilterChange('category', 'inbox')}
        >
          <MdInbox /> 받은편지함
        </button>
        <button 
          className={`filter-button ${filter.category === 'spam' ? 'active' : ''}`}
          onClick={() => handleFilterChange('category', 'spam')}
        >
          <MdReportProblem /> 스팸
        </button>
        <button 
          className={`filter-button ${filter.important === true ? 'active' : ''}`}
          onClick={() => handleFilterChange('important', true)}
        >
          <MdStar /> 중요
        </button>
      </div>
      
      <div className="email-list">
        {loading ? (
          <div className="loading">이메일을 불러오는 중...</div>
        ) : emails.length === 0 ? (
          <div className="empty-list">이메일이 없습니다.</div>
        ) : (
          emails.map((email) => (
            <EmailItem 
              key={email.id} 
              email={email} 
              onRefresh={fetchEmails}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default EmailList;