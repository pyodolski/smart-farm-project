import React, { useEffect, useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';
import logo from '../../image/leaves-growing-from-ground-green-glyph-style_78370-6720.png';
import { AuthContext } from '../../contexts/AuthContext';
import API_BASE_URL from '../../utils/config';
import { FaBars } from 'react-icons/fa';

function Navbar() {
  const [show, setShow] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useContext(AuthContext);
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

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