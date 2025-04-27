import axios from 'axios';

// API 기본 설정
const api = axios.create({
  baseURL: 'http://localhost:8000',  // 백엔드 서버 주소
  headers: {
    'Content-Type': 'application/json',
  },
});

// 채팅 메시지 전송 함수
export const sendMessage = async (message, conversationId = null) => {
  try {
    const response = await api.post('/agent/', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  } catch (error) {
    console.error('API 오류:', error);
    throw error;
  }
};

// 이메일 데이터 가져오기 (임시 데이터)
export const getEmails = async () => {
  // 실제 API가 구현되기 전까지 임시 데이터 반환
  return [
    {
      id: '1',
      sender: 'john.doe@example.com',
      sender_name: 'John Doe',
      subject: '회의 일정 안내',
      date: '2025-04-27T10:30:00Z',
      category: 'inbox',
      read: false,
      important: true,
      content: '안녕하세요, 내일 오전 10시에 프로젝트 진행 상황 회의가 있습니다. 참석 부탁드립니다.'
    },
    {
      id: '2',
      sender: 'marketing@company.com',
      sender_name: '마케팅팀',
      subject: '4월 마케팅 보고서',
      date: '2025-04-26T14:15:00Z',
      category: 'inbox',
      read: true,
      important: false,
      content: '4월 마케팅 캠페인 결과를 첨부합니다. 성과가 좋았으며, 다음 달 계획도 함께 검토해주세요.'
    },
    {
      id: '3',
      sender: 'support@service.com',
      sender_name: '고객센터',
      subject: '문의하신 내용에 대한 답변입니다',
      date: '2025-04-25T09:45:00Z',
      category: 'inbox',
      read: true,
      important: false,
      content: '문의하신 서비스 이용 관련 내용에 대해 답변 드립니다. 추가 질문이 있으시면 언제든지 문의해주세요.'
    },
    {
      id: '4',
      sender: 'newsletter@news.com',
      sender_name: '뉴스레터',
      subject: '주간 기술 트렌드 소식',
      date: '2025-04-27T07:00:00Z',
      category: 'spam',
      read: false,
      important: false,
      content: '이번 주 기술 트렌드: AI 발전 동향, 새로운 프로그래밍 언어 출시, 클라우드 서비스 업데이트 등의 내용을 담고 있습니다.'
    },
    {
      id: '5',
      sender: 'team@project.com',
      sender_name: '프로젝트팀',
      subject: '프로젝트 마감일 연장 안내',
      date: '2025-04-26T16:20:00Z',
      category: 'inbox',
      read: false,
      important: true,
      content: '현재 진행 중인 프로젝트의 마감일이 다음 주 금요일로 연장되었습니다. 일정 참고 부탁드립니다.'
    }
  ];
};