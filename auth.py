"""
Sistema de autenticación para el Dashboard ICE
Módulo simple de autenticación con session state
"""

import streamlit as st
import hashlib
import time

class AuthManager:
    """Gestor de autenticación simple para el dashboard"""
    
    def __init__(self):
        # Credenciales por defecto (en producción usar base de datos)
        self.valid_credentials = {
            'admin': self._hash_password('qwerty'),
            'editor': self._hash_password('editor123'),
            'viewer': self._hash_password('viewer456')
        }
        
        # Roles y permisos
        self.user_roles = {
            'admin': ['create', 'edit', 'delete', 'view', 'export'],
            'editor': ['edit', 'view', 'export'],
            'viewer': ['view']
        }
        
        # Inicializar session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None
    
    def _hash_password(self, password):
        """Hash de contraseña usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Autenticar usuario"""
        if username in self.valid_credentials:
            password_hash = self._hash_password(password)
            if self.valid_credentials[username] == password_hash:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_role = username  # Rol simple basado en username
                st.session_state.login_time = time.time()
                return True
        return False
    
    def logout(self):
        """Cerrar sesión"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.login_time = None
    
    def is_authenticated(self):
        """Verificar si el usuario está autenticado"""
        return st.session_state.get('authenticated', False)
    
    def get_username(self):
        """Obtener nombre de usuario actual"""
        return st.session_state.get('username', None)
    
    def get_user_role(self):
        """Obtener rol del usuario actual"""
        return st.session_state.get('user_role', None)
    
    def has_permission(self, action):
        """Verificar si el usuario tiene permiso para una acción"""
        if not self.is_authenticated():
            return False
        
        user_role = self.get_user_role()
        if user_role in self.user_roles:
            return action in self.user_roles[user_role]
        return False
    
    def require_auth_for_action(self, action_name):
        """Requerir autenticación para una acción específica"""
        if not self.is_authenticated():
            st.warning(f"🔒 **Autenticación requerida para:** {action_name}")
            st.info("Inicia sesión como administrador para acceder a esta funcionalidad.")
            return False
        
        if not self.has_permission('edit'):  # La mayoría de acciones admin requieren 'edit'
            st.error(f"❌ **Sin permisos para:** {action_name}")
            st.info(f"Tu rol ({self.get_user_role()}) no tiene permisos suficientes.")
            return False
        
        return True
    
    def login_form(self):
        """Mostrar formulario de login"""
        with st.form("login_form_unique"):
            st.markdown("#### 🔐 Iniciar Sesión como Administrador")
            
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Usuario", placeholder="admin", key="login_username")
            
            with col2:
                password = st.text_input("Contraseña", type="password", placeholder="qwerty", key="login_password")
            
            login_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if login_button:
                if username and password:
                    if self.login(username, password):
                        st.success(f"✅ Sesión iniciada como {username}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.warning("⚠️ Completa todos los campos")
    
    def show_auth_status(self):
        """Mostrar estado de autenticación en la interfaz"""
        if self.is_authenticated():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                username = self.get_username()
                role = self.get_user_role()
                login_time = st.session_state.get('login_time', 0)
                
                if login_time:
                    elapsed = int(time.time() - login_time)
                    minutes = elapsed // 60
                    hours = minutes // 60
                    
                    if hours > 0:
                        time_str = f"{hours}h {minutes % 60}m"
                    else:
                        time_str = f"{minutes}m"
                    
                    st.success(f"🔓 **Sesión activa:** {username} ({role}) - {time_str}")
                else:
                    st.success(f"🔓 **Sesión activa:** {username} ({role})")
            
            with col2:
                if st.button("Cerrar Sesión", key="logout_button_unique"):
                    self.logout()
                    st.rerun()
        else:
            st.info("🔒 **Sin autenticar** - Solo modo consulta disponible")

# Instancia global del gestor de autenticación
auth_manager = AuthManager()
