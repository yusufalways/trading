"""
Simple Authentication System for Trading Dashboard
Provides basic login functionality with session persistence
"""

import streamlit as st
import hashlib
import json
import os
import time
from datetime import datetime, timedelta
import base64

class SimpleAuth:
    def __init__(self, credentials_file="data/credentials.json"):
        self.credentials_file = credentials_file
        self.session_duration = 30  # days
        self.ensure_credentials_file()
    
    def ensure_credentials_file(self):
        """Create default credentials file if it doesn't exist"""
        if not os.path.exists(self.credentials_file):
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            # Default credentials - you should change these!
            default_creds = {
                "users": {
                    "admin@trading.com": {
                        "password_hash": self.hash_password("admin123"),
                        "name": "Trading Admin",
                        "created": datetime.now().isoformat()
                    }
                }
            }
            with open(self.credentials_file, 'w') as f:
                json.dump(default_creds, f, indent=2)
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_credentials(self, email, password):
        """Verify email and password"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
            
            if email in creds["users"]:
                stored_hash = creds["users"][email]["password_hash"]
                return stored_hash == self.hash_password(password)
            return False
        except:
            return False
    
    def get_user_info(self, email):
        """Get user information"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
            return creds["users"].get(email, {})
        except:
            return {}
    
    def create_session_token(self, email):
        """Create a simple session token"""
        timestamp = datetime.now().isoformat()
        token_data = f"{email}:{timestamp}"
        return base64.b64encode(token_data.encode()).decode()
    
    def verify_session_token(self, token):
        """Verify session token and check if it's still valid"""
        try:
            decoded = base64.b64decode(token.encode()).decode()
            email, timestamp = decoded.split(':', 1)
            token_time = datetime.fromisoformat(timestamp)
            
            # Check if token is still valid (within session duration)
            if datetime.now() - token_time <= timedelta(days=self.session_duration):
                return email
            return None
        except:
            return None
    
    def set_remember_me(self, email):
        """Set remember me using session state with persistence"""
        token = self.create_session_token(email)
        # Store in session state for persistence
        st.session_state.remember_token = token
        st.session_state.remember_email = email
        st.session_state.remember_me_active = True
        
        # Also use JavaScript to store in localStorage as backup
        st.markdown(f"""
        <script>
        localStorage.setItem('trading_auth_token', '{token}');
        localStorage.setItem('trading_auth_email', '{email}');
        localStorage.setItem('trading_remember_me', 'true');
        </script>
        """, unsafe_allow_html=True)
        return token
    
    def check_remember_me(self):
        """Check for remember me token on page load"""
        # First check session state
        if st.session_state.get('remember_me_active') and st.session_state.get('remember_token'):
            email = self.verify_session_token(st.session_state.remember_token)
            if email:
                return email, st.session_state.remember_token
        
        # Use a more reliable approach with hidden input and JavaScript
        if 'checked_localStorage' not in st.session_state:
            st.session_state.checked_localStorage = True
            
            # Create a hidden component to read localStorage
            st.markdown("""
            <div id="localStorage-reader" style="display: none;">
                <script>
                function checkLocalStorage() {
                    const token = localStorage.getItem('trading_auth_token');
                    const email = localStorage.getItem('trading_auth_email');
                    const rememberMe = localStorage.getItem('trading_remember_me');
                    
                    if (token && email && rememberMe === 'true') {
                        // Set URL parameters to pass data to Streamlit
                        const currentUrl = new URL(window.location.href);
                        if (!currentUrl.searchParams.has('auth_token')) {
                            currentUrl.searchParams.set('auth_token', token);
                            currentUrl.searchParams.set('auth_email', email);
                            window.location.href = currentUrl.toString();
                        }
                    }
                }
                checkLocalStorage();
                </script>
            </div>
            """, unsafe_allow_html=True)
        
        # Check URL parameters
        query_params = st.query_params
        if 'auth_token' in query_params and 'auth_email' in query_params:
            token = query_params['auth_token']
            email = query_params['auth_email']
            
            # Verify token
            verified_email = self.verify_session_token(token)
            if verified_email == email:
                # Clear URL parameters
                st.query_params.clear()
                st.session_state.remember_token = token
                st.session_state.remember_email = email
                st.session_state.remember_me_active = True
                return email, token
        
        return None, None
    
    def clear_remember_me(self):
        """Clear remember me data"""
        # Clear session state
        if 'remember_token' in st.session_state:
            del st.session_state.remember_token
        if 'remember_email' in st.session_state:
            del st.session_state.remember_email
        if 'remember_me_active' in st.session_state:
            del st.session_state.remember_me_active
        
        # Clear localStorage
        st.markdown("""
        <script>
        localStorage.removeItem('trading_auth_token');
        localStorage.removeItem('trading_auth_email');
        localStorage.removeItem('trading_remember_me');
        </script>
        """, unsafe_allow_html=True)

def show_login_form():
    """Display login form"""
    # Clear any previous content
    st.set_page_config(
        page_title="Trading Dashboard Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Clear page content completely
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp {
        background-color: #0e1117;
    }
    /* Hide any potential sidebar content */
    .css-1d391kg {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("# 🔐 Trading Dashboard Login")
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome Back!")
        st.markdown("Please login to access your trading dashboard")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="your.email@example.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("🔄 Remember me on this device")
            
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submitted:
                auth = SimpleAuth()
                if auth.verify_credentials(email, password):
                    # Successful login
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_info = auth.get_user_info(email)
                    
                    if remember_me:
                        auth.set_remember_me(email)
                    
                    st.success("✅ Login successful! Redirecting...")
                    time.sleep(1)  # Brief pause for user feedback
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
        
        # Default credentials info
        with st.expander("🔑 Default Login Credentials", expanded=False):
            st.info("""
            **Default credentials for testing:**
            - Email: `admin@trading.com`
            - Password: `admin123`
            
            **Security Note:** Change these credentials in `data/credentials.json` after first login!
            """)
        
        st.markdown("---")
        st.markdown("🛡️ *Your data is protected by session-based authentication*")

def check_authentication():
    """Check if user is authenticated"""
    auth = SimpleAuth()
    
    # Check current session
    if st.session_state.get('authenticated', False):
        return True
    
    # Check remember me functionality
    remember_email, remember_token = auth.check_remember_me()
    if remember_email and remember_token:
        # Auto-login with remember me
        st.session_state.authenticated = True
        st.session_state.user_email = remember_email
        st.session_state.user_info = auth.get_user_info(remember_email)
        return True
    
    return False

def show_logout_option():
    """Show logout option in sidebar"""
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.markdown("---")
            user_info = st.session_state.get('user_info', {})
            user_name = user_info.get('name', 'User')
            st.markdown(f"👤 **Logged in as:** {user_name}")
            st.markdown(f"📧 {st.session_state.get('user_email', '')}")
            
            if st.button("🚪 Logout", use_container_width=True):
                # Clear session
                auth = SimpleAuth()
                auth.clear_remember_me()
                
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.user_info = None
                
                if 'remember_token' in st.session_state:
                    del st.session_state.remember_token
                if 'remember_email' in st.session_state:
                    del st.session_state.remember_email
                if 'remember_me_active' in st.session_state:
                    del st.session_state.remember_me_active
                if 'remember_token' in st.session_state:
                    del st.session_state.remember_token
                
                # Clear browser storage
                auth = SimpleAuth()
                auth.clear_remember_me()
                
                st.success("✅ Logged out successfully")
                st.rerun()

def require_authentication(func):
    """Decorator to require authentication for functions"""
    def wrapper(*args, **kwargs):
        if check_authentication():
            return func(*args, **kwargs)
        else:
            show_login_form()
            return None
    return wrapper

# Utility function to add user (for admin use)
def add_user(email, password, name="User"):
    """Add a new user to the system"""
    auth = SimpleAuth()
    try:
        with open(auth.credentials_file, 'r') as f:
            creds = json.load(f)
        
        creds["users"][email] = {
            "password_hash": auth.hash_password(password),
            "name": name,
            "created": datetime.now().isoformat()
        }
        
        with open(auth.credentials_file, 'w') as f:
            json.dump(creds, f, indent=2)
        
        return True
    except:
        return False
