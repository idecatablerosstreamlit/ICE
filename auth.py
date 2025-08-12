"""
Sistema de Autenticación para Dashboard ICE
Archivo: auth.py
"""

import streamlit as st
import hashlib
from datetime import datetime, timedelta

class AuthenticationManager:
    """Gestor de autenticación para el Dashboard ICE"""
    
    def __init__(self):
        self.admin_username = "admin"
        self.admin_password_hash = self._hash_password("qwerty")
        self.session_timeout = 30  # minutos
    
    def _hash_password(self, password):
        """Hashear contraseña para seguridad básica"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Autenticar usuario"""
        if username == self.admin_username:
            password_hash = self._hash_password(password)
            return password_hash == self.admin_password_hash
        return False
    
    def login_form(self):
        """Mostrar formulario de login"""
        st.markdown("### Acceso de Administrador")
        st.warning("Se requieren permisos de administrador para crear, editar o eliminar indicadores")
        
        with st.form("login_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                username = st.text_input("Usuario", placeholder="admin")
                password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            with col2:
                st.write("")  # Espaciado
                st.write("")  # Espaciado
                login_button = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("Por favor ingresa usuario y contraseña")
                    return False
                
                if self.authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.auth_time = datetime.now()
                    st.session_state.admin_user = username
                    st.success("Acceso autorizado")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
                    return False
        
        return False
    
    def is_authenticated(self):
        """Verificar si el usuario está autenticado y la sesión es válida"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Verificar timeout de sesión
        auth_time = st.session_state.get('auth_time')
        if auth_time:
            time_diff = datetime.now() - auth_time
            if time_diff > timedelta(minutes=self.session_timeout):
                self.logout()
                return False
        
        return True
    
    def logout(self):
        """Cerrar sesión"""
        st.session_state.authenticated = False
        st.session_state.auth_time = None
        st.session_state.admin_user = None
        st.rerun()
    
    def show_auth_status(self):
        """Mostrar estado de autenticación en sidebar"""
        if self.is_authenticated():
            with st.sidebar:
                st.markdown("---")
                st.markdown("### Sesión Activa")
                st.success(f"**Usuario:** {st.session_state.get('admin_user', 'admin')}")
                
                # Mostrar tiempo restante
                auth_time = st.session_state.get('auth_time')
                if auth_time:
                    time_diff = datetime.now() - auth_time
                    remaining = self.session_timeout - int(time_diff.total_seconds() / 60)
                    if remaining > 0:
                        st.info(f"**Tiempo restante:** {remaining} min")
                    else:
                        st.warning("**Sesión expirada**")
                
                if st.button("Cerrar Sesión", use_container_width=True):
                    self.logout()
    
    def require_auth_for_action(self, action_name):
        """Decorador/wrapper para requerir autenticación en acciones específicas"""
        if not self.is_authenticated():
            st.warning(f"Acción restringida: {action_name}")
            st.info("Se requieren permisos de administrador para realizar esta acción")
            return False
        return True

# Instancia global del gestor de autenticación
auth_manager = AuthenticationManager()
