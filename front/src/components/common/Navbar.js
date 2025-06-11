import React, { useEffect, useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';
import logo from '../../image/leaves-growing-from-ground-green-glyph-style_78370-6720.png';
import { AuthContext } from '../../contexts/AuthContext';
import API_BASE_URL from '../../utils/config';
import { FaBars } from 'react-icons/fa';
import { IoNotifications } from 'react-icons/io5';

function Navbar() {
  const [show, setShow] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useContext(AuthContext);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

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

  return (
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
          {isLoggedIn && (
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
                  <IoNotifications size={24} />
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
          )}
        </div>
        {/* 모바일 햄버거 메뉴 */}
        <button className="hamburger-menu" onClick={()=>setMenuOpen(!menuOpen)}>
          <FaBars size={28} />
        </button>
        {menuOpen && (
          <div className="dropdown-menu">
            {isLoggedIn && (
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
                    <IoNotifications size={24} />
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
            )}
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar; 