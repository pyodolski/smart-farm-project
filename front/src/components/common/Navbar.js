import React, { useEffect, useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';
import logo from '../../image/leaves-growing-from-ground-green-glyph-style_78370-6720.png';
import { AuthContext } from '../../contexts/AuthContext';
import API_BASE_URL from '../../utils/config';
import { FaBars } from 'react-icons/fa';
import { VscBell, VscBellDot } from "react-icons/vsc";
import Login from '../../pages/auth/Login';

function Navbar() {
  const [show, setShow] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useContext(AuthContext);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showKakaoModal, setShowKakaoModal] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY < 10) {
        setShow(true);
      } else if (window.scrollY > lastScrollY) {
        setShow(false);
      } else {
        setShow(true);
      }
      setLastScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  // 알림 목록 가져오기
  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notifications`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('알림 가져오기 실패:', error);
    }
  };

  // 로그인 상태가 변경되거나 컴포넌트가 마운트될 때 알림 가져오기
  useEffect(() => {
    if (isLoggedIn) {
      fetchNotifications();
      // 60초마다 알림 갱신
      const interval = setInterval(fetchNotifications, 60000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn]);

  // 알림 클릭 처리
  const handleNotificationClick = async (notification) => {
    try {
      // 알림 삭제
      const response = await fetch(`${API_BASE_URL}/api/notifications/${notification.id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      
      if (response.ok) {
        // 알림 목록 업데이트
        setNotifications(notifications.filter(n => n.id !== notification.id));
        
        // 해당 페이지로 이동
        navigate(notification.url);
        setShowNotifications(false);
      }
    } catch (error) {
      console.error('알림 처리 실패:', error);
    }
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  const handleLogout = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        sessionStorage.removeItem('isLoggedIn');
        sessionStorage.removeItem('userId');
        setIsLoggedIn(false);
        setId('');
        setPassword('');
        navigate('/login');
      }
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  // 알림 팝업 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showNotifications && !event.target.closest('.notification-container')) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [showNotifications]);

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
        setShowLoginForm(false);

        if (data.admin) {
          window.location.href = `${API_BASE_URL}/admin.html`;
        } else {
          navigate('/');
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

  const resetLoginForm = () => {
    setId('');
    setPassword('');
    setError('');
    setShowLoginForm(false);
  };

  const handleKakaoModalNo = () => {
    setShowKakaoModal(false);
    resetLoginForm();
    alert('마이페이지에서 연동한 후 이용해 주세요');
    navigate('/');
  };

  return (
    <>
      <nav className={`navbar ${show ? 'navbar-show' : 'navbar-hide'}`}>
        <div className="nav-brand" onClick={handleLogoClick}>
          <img 
            src={logo}
            alt="Smart Farm Hub" 
            className="nav-logo" 
          />
          <span className="brand-text" style={{fontSize: "1.6rem"}}>Smart Farm Hub</span>
        </div>
        <div className="nav-menu">
          {/* 데스크탑 메뉴 */}
          <div className="menu-items desktop-menu">
            {isLoggedIn ? (
              <>
                <a onClick={()=> navigate('/Products')}>Products</a>
                <a onClick={()=> navigate('/encyclopedia')}>Encyclopedia</a>
                <a onClick={()=> navigate('/')}>Farm</a>
                <a onClick={()=> navigate('/Statistics')}>Statistics</a>
                <a onClick={()=> navigate('/community')}>Community</a>
                <div className="notification-container">
                  <button 
                    className="notification-btn" 
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowNotifications(!showNotifications);
                    }}
                  >
                    {notifications.length > 0 ? <VscBellDot size={24} /> : <VscBell size={24} />}
                    {notifications.length > 0 && (
                      <span className="notification-badge">{notifications.length}</span>
                    )}
                  </button>
                  {showNotifications && (
                    <div className="notification-popup">
                      {notifications.length > 0 ? (
                        notifications.map((notification) => (
                          <div
                            key={notification.id}
                            className="notification-item"
                            onClick={() => handleNotificationClick(notification)}
                          >
                            <p>{notification.message}</p>
                            <span className="notification-date">
                              {new Date(notification.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="no-notifications">
                          새로운 알림이 없습니다
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <button className="login-btn" onClick={()=> navigate('/profile')}>
                  {sessionStorage.getItem('nickname')}님 환영합니다
                </button>
                <button className="logout-btn" onClick={handleLogout}>
                  로그아웃
                </button>
              </>
            ) : (
              <button className="nav-login-btn" onClick={() => {setShowLoginForm(true); setMenuOpen(false);}}>
                로그인
              </button>
            )}
          </div>
          {/* 모바일 햄버거 메뉴 */}
          <button className="hamburger-menu" onClick={()=>setMenuOpen(!menuOpen)}>
            <FaBars size={28} />
          </button>
          {menuOpen && (
            <div className="dropdown-menu">
              {isLoggedIn ? (
                <>
                  <a onClick={()=> {navigate('/Products'); setMenuOpen(false);}}>Products</a>
                  <a onClick={()=> {navigate('/encyclopedia'); setMenuOpen(false);}}>Encyclopedia</a>
                  <a onClick={()=> {navigate('/'); setMenuOpen(false);}}>Farm</a>
                  <a onClick={()=> {navigate('/Statistics'); setMenuOpen(false);}}>Statistics</a>
                  <a onClick={()=> {navigate('/community'); setMenuOpen(false);}}>Community</a>
                  <div className="notification-container">
                    <button 
                      className="notification-btn" 
                      onClick={(e) => {
                        e.stopPropagation();
                        setShowNotifications(!showNotifications);
                      }}
                    >
                      {notifications.length > 0 ? <VscBellDot size={24} /> : <VscBell size={24} />}
                      {notifications.length > 0 && (
                        <span className="notification-badge">{notifications.length}</span>
                      )}
                    </button>
                  </div>
                  <button className="login-btn" onClick={()=> {navigate('/profile'); setMenuOpen(false);}}>
                    {sessionStorage.getItem('nickname')}님 환영합니다
                  </button>
                  <button className="logout-btn" onClick={()=> {handleLogout(); setMenuOpen(false);}}>
                    로그아웃
                  </button>
                </>
              ) : (
                <button className="login-btn" onClick={() => {setShowLoginForm(true); setMenuOpen(false);}}>
                  로그인
                </button>
              )}
            </div>
          )}
        </div>
      </nav>
      {showLoginForm && (
        <div className="login-modal-overlay" onClick={resetLoginForm}>
          <div className="login-modal-content" onClick={e => e.stopPropagation()}>
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
                  onClick={() => {
                    setShowLoginForm(false);
                    navigate('/register');
                  }}
                  disabled={isLoading}
                >
                  회원가입
                </button>
                <button
                  className="kakao-login-button"
                  onClick={handleKakaoLogin}
                  disabled={isLoading}
                  type="button"
                >
                  카카오로 로그인
                </button>
              </form>
              {showKakaoModal && (
                <div className="modal-overlay">
                  <div className="modal-box">
                    <p>카카오톡 로그인을 클릭하셨습니다.<br/>카카오톡 연동을 하셨나요?</p>
                    <auth-button onClick={handleKakaoModalYes}>네</auth-button>
                    <auth-button onClick={handleKakaoModalNo}>아니요</auth-button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Navbar; 