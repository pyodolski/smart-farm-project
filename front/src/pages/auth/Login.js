import React, { useState, useContext, useEffect, useRef } from 'react';
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
  const [showKakaoModal, setShowKakaoModal] = useState(false);
  const waveRef = useRef(null);
  const waveText = "Smart Farm Hub에 오신 것을 환영합니다";

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

  useEffect(() => {
    const wave = waveRef.current;
    if (!wave) return;
    wave.innerHTML = waveText
      .split("")
      .map((letter, idx) => {
        if (letter === " ") return " ";
        return `<span style="animation-delay:${idx * 15}ms" class="letter">${letter}</span>`;
      })
      .join("");
  }, []);

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
    setShowKakaoModal(true);
  };

  const handleKakaoModalYes = () => {
    setShowKakaoModal(false);
    window.location.href = `${API_BASE_URL}/auth/kakao`;
  };

  const handleKakaoModalNo = () => {
    setShowKakaoModal(false);
    alert('마이페이지에서 연동한 후 이용해 주세요');
    navigate('/');
  };

  return (
    <>
      <div className="wave-text-area">
        <div ref={waveRef} className="wave title" />
      </div>
      <div className="login-container">
      </div>
    </>
  );
}

export default Login;
