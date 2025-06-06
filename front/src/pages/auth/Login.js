import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';
import './Login.css';
import API_BASE_URL from '../../utils/config';

function Login() {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useContext(AuthContext);

  useEffect(() => {
    // 이미 로그인된 상태라면 메인 페이지로 리다이렉트
    const checkLoginStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/check_login`, {
          credentials: 'include'
        });
        const data = await response.json();
        
        if (data.logged_in) {
          navigate('/');
        }
      } catch (error) {
        console.error('로그인 상태 확인 실패:', error);
      }
    };

    checkLoginStatus();
  }, [navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, password }),
        credentials: 'include'
      });

      const data = await response.json();

      if (response.ok) {
        console.log('로그인 성공:', data);
        sessionStorage.setItem('isLoggedIn', 'true');
        sessionStorage.setItem('userId', data.user_id);
        sessionStorage.setItem('nickname', data.nickname);
        setIsLoggedIn(true);

        if (data.admin) {
          window.location.href = `${API_BASE_URL}/admin.html`;  // 관리자일 경우 정적 페이지 이동
        } else {
          navigate('/');  // 일반 유저는 홈으로 이동
        }
      } else {
        console.error('로그인 실패:', data);
        setError(data.message || '로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('로그인 오류:', error);
      setError('서버와의 통신 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKakaoLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/kakao`;
  };

  return (
    <div className="login-container">
      <div className="login-form-box">
        <h2>로그인</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <input
              type="text"
              placeholder="ID"
              value={id}
              onChange={(e) => setId(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          <div className="input-group">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? '로그인 중...' : '로그인'}
          </button>
          <button
            type="button"
            className="register-button"
            onClick={() => navigate('/register')}
            disabled={isLoading}
          >
            회원가입
          </button>

          <button
            className="kakao-login-button"
            onClick={handleKakaoLogin}
            disabled={isLoading}
          >
            카카오로 로그인
          </button>

        </form>
      </div>
    </div>
  );
}

export default Login;
