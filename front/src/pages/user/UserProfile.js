import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';
import API_BASE_URL from '../../utils/config';

function UserProfile() {
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isPasswordMode, setIsPasswordMode] = useState(false);
  const [formData, setFormData] = useState({
    nickname: '',
    email: '',
    name: '',
    current_password: ''
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUserInfo(data.user);
          setFormData({
            nickname: data.user.nickname,
            email: data.user.email,
            name: data.user.name,
            current_password: ''
          });
        }
      } else {
        navigate('/login');
      }
    } catch (error) {
      console.error('프로필 로딩 실패:', error);
      setError('프로필을 불러오는데 실패했습니다.');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (response.ok) {
        setSuccess(data.message);
        setIsEditMode(false);
        fetchUserProfile();
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('프로필 수정 실패:', error);
      setError('프로필 수정에 실패했습니다.');
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/user/password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(passwordData)
      });

      const data = await response.json();
      if (response.ok) {
        setSuccess(data.message);
        setIsPasswordMode(false);
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('비밀번호 변경 실패:', error);
      setError('비밀번호 변경에 실패했습니다.');
    }
  };

  const handleKakaoConnect = () => {
    window.location.href = `${API_BASE_URL}/auth/kakao`;
  };

  if (!userInfo) {
    return <div className="loading">로딩 중...</div>;
  }

  return (
    <div className="profile-container">
      <h2>내 프로필</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {!isEditMode && !isPasswordMode && (
        <div className="profile-info">
          <div className="info-group">
            <label>아이디</label>
            <p>{userInfo.id}</p>
          </div>
          <div className="info-group">
            <label>닉네임</label>
            <p>{userInfo.nickname}</p>
          </div>
          <div className="info-group">
            <label>이메일</label>
            <p>{userInfo.email}</p>
          </div>
          <div className="info-group">
            <label>이름</label>
            <p>{userInfo.name}</p>
          </div>
          <div className="button-group">
            <button onClick={() => setIsEditMode(true)}>
              프로필 수정
            </button>
            <button onClick={() => setIsPasswordMode(true)}>
              비밀번호 변경
            </button>
            <button onClick={handleKakaoConnect} className="kakao-btn">
              카카오톡 연동
            </button>
          </div>
        </div>
      )}

      {isEditMode && (
        <form onSubmit={handleSubmit} className="edit-form">
          <div className="form-group">
            <label htmlFor="nickname">닉네임</label>
            <input
              type="text"
              id="nickname"
              name="nickname"
              value={formData.nickname}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="name">이름</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="current_password">현재 비밀번호</label>
            <input
              type="password"
              id="current_password"
              name="current_password"
              value={formData.current_password}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="button-group">
            <button type="submit">저장</button>
            <button type="button" onClick={() => setIsEditMode(false)}>
              취소
            </button>
          </div>
        </form>
      )}

      {isPasswordMode && (
        <form onSubmit={handlePasswordSubmit} className="edit-form">
          <div className="form-group">
            <label htmlFor="current_password">현재 비밀번호</label>
            <input
              type="password"
              id="current_password"
              name="current_password"
              value={passwordData.current_password}
              onChange={handlePasswordChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="new_password">새 비밀번호</label>
            <input
              type="password"
              id="new_password"
              name="new_password"
              value={passwordData.new_password}
              onChange={handlePasswordChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirm_password">새 비밀번호 확인</label>
            <input
              type="password"
              id="confirm_password"
              name="confirm_password"
              value={passwordData.confirm_password}
              onChange={handlePasswordChange}
              required
            />
          </div>
          <div className="button-group">
            <button type="submit">변경</button>
            <button type="button" onClick={() => setIsPasswordMode(false)}>
              취소
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default UserProfile; 