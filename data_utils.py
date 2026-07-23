"""
Utilidades para el manejo de datos del Dashboard ICE - VERSIÓN CON SHEETS FICHAS
CORRECCIÓN: Cargar fichas metodológicas desde Google Sheets en lugar de Excel
"""

import pandas as pd
import numpy as np
import streamlit as st
import os
from config import COLUMN_MAPPING, DEFAULT_META, INDICATOR_TYPES

# Importación de Google Sheets
try:
    from google_sheets_manager import GoogleSheetsManager
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# Tabla de IPC (Índice de Precios al Consumidor) por año
IPC_ANUAL = {
    2019: 3.8,
    2020: 1.61,
    2021: 5.625,
    2022: 13.12,
    2023: 9.28,
    2024: 5.2,
    2025: 5.1
}

def calcular_factor_inflacion_acumulada(año_base, año_final):
    """
    Calcula el factor de inflación acumulada desde año_base hasta año_final
    Args:
        año_base: Año del valor original
        año_final: Año al que se quiere ajustar
    Returns:
        Factor de inflación acumulada (ej: 1.377 significa 37.7% de inflación acumulada)
    """
    if año_base >= año_final:
        return 1.0

    factor_acumulado = 1.0
    for año in range(año_base + 1, año_final + 1):
        if año in IPC_ANUAL:
            tasa_ipc = IPC_ANUAL[año] / 100
            factor_acumulado *= (1 + tasa_ipc)

    return factor_acumulado

class DataLoader:
    """Clase para cargar datos - VERSIÓN CON FICHAS DESDE SHEETS"""
    
    def __init__(self):
        self.df = None
        self.sheets_manager = None
        
        if not GOOGLE_SHEETS_AVAILABLE:
            st.error("❌ **Google Sheets no disponible.** Instala: `pip install gspread google-auth`")
            return
        
        try:
            self.sheets_manager = GoogleSheetsManager()
        except Exception as e:
            st.error(f"❌ Error al inicializar Google Sheets: {e}")
            self.sheets_manager = None
    
    def load_data(self):
        """Cargar datos desde Google Sheets - SILENCIOSO PARA ENCABEZADO"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                return self._create_empty_dataframe()
            
            # Cargar datos silenciosamente
            df = self.sheets_manager.load_data()
            
            if df is None or df.empty:
                return self._create_empty_dataframe()
            
            # Procesar datos silenciosamente
            self._process_dataframe_silent(df)
            
            # Verificar y limpiar silenciosamente
            if self._verify_dataframe_simple(df):
                return df
            else:
                return self._create_empty_dataframe()
                
        except Exception as e:
            return self._create_empty_dataframe()
    
    def load_fichas_data(self):
        """NUEVO: Cargar fichas metodológicas desde Google Sheets"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                return None

            # Cargar fichas desde Google Sheets
            fichas_df = self.sheets_manager.load_fichas_data()

            if fichas_df is None:
                return None

            if fichas_df.empty:
                return pd.DataFrame()

            # Limpiar datos de fichas usando COD
            if 'COD' in fichas_df.columns:
                fichas_df = fichas_df.dropna(subset=['COD'], how='all')

            return fichas_df

        except Exception as e:
            st.error(f"❌ Error al cargar fichas: {e}")
            return None

    def load_combined_data(self):
        """NUEVO: Cargar datos combinados (IndicadoresICE + Fichas con JOIN)"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE or not self.sheets_manager:
                return self._create_empty_dataframe()

            # Cargar datos combinados usando el método del GoogleSheetsManager
            df = self.sheets_manager.load_combined_data()

            if df is None or df.empty:
                return self._create_empty_dataframe()

            # Cargar fichas para calcular valores recalculados
            fichas_data = self.sheets_manager.load_fichas_data()

            # Procesar datos silenciosamente (incluye normalización)
            self._process_dataframe_silent(df)

            # Calcular valores recalculados DESPUÉS de todo el procesamiento
            if fichas_data is not None and not fichas_data.empty:
                self._calculate_recalculated_values(df, fichas_data)
            else:
                # Si no hay fichas, Valor_Recalculado = Valor
                if 'Valor' in df.columns:
                    df['Valor_Recalculado'] = df['Valor'].copy()

            # Verificar y limpiar silenciosamente
            if self._verify_dataframe_simple(df):
                return df
            else:
                return self._create_empty_dataframe()

        except Exception as e:
            st.error(f"❌ Error al cargar datos combinados: {e}")
            return self._create_empty_dataframe()

    def _create_empty_dataframe(self):
        """Crear DataFrame vacío"""
        return pd.DataFrame(columns=[
            'Componente', 'Categoria',
            'COD', 'Indicador', 'Valor', 'Fecha', 'Meta', 'Peso', 'Tipo', 'Valor_Normalizado', 'Valor_Recalculado'
        ])
    
    def _process_dataframe_silent(self, df):
        """Procesar DataFrame silenciosamente (sin mostrar información en pantalla)"""
        try:
            # Renombrar columnas
            for original, nuevo in COLUMN_MAPPING.items():
                if original in df.columns:
                    df.rename(columns={original: nuevo}, inplace=True)

            # Procesar fechas silenciosamente
            self._process_dates_silent(df)

            # Procesar valores silenciosamente
            self._process_values_silent(df)

            # Añadir columnas por defecto
            self._add_default_columns_corrected(df)

            # Normalización silenciosa
            self._normalize_values_silent(df)

        except Exception as e:
            pass  # Silencioso

    def _process_dataframe_without_normalize(self, df):
        """Procesar DataFrame SIN normalizar (para procesar antes de calcular Valor_Recalculado)"""
        try:
            # Renombrar columnas
            for original, nuevo in COLUMN_MAPPING.items():
                if original in df.columns:
                    df.rename(columns={original: nuevo}, inplace=True)

            # Procesar fechas silenciosamente
            self._process_dates_silent(df)

            # Procesar valores silenciosamente
            self._process_values_silent(df)

            # Añadir columnas por defecto
            self._add_default_columns_corrected(df)

            # NO normalizar aquí - se hará después de calcular Valor_Recalculado

        except Exception as e:
            pass  # Silencioso
    
    def _process_dates_silent(self, df):
        """Procesar fechas silenciosamente"""
        try:
            if 'Fecha' not in df.columns:
                return
            
            # Formatos de fecha comunes
            date_formats = [
                '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', 
                '%Y/%m/%d', '%m/%d/%Y', '%d.%m.%Y'
            ]
            
            fechas_convertidas = None
            
            for formato in date_formats:
                try:
                    temp_fechas = pd.to_datetime(df['Fecha'], format=formato, errors='coerce')
                    validas = temp_fechas.notna().sum()
                    
                    if validas > 0:
                        if fechas_convertidas is None or validas > fechas_convertidas.notna().sum():
                            fechas_convertidas = temp_fechas
                except:
                    continue
            
            if fechas_convertidas is None or fechas_convertidas.notna().sum() == 0:
                try:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce', dayfirst=True)
                except:
                    fechas_convertidas = pd.to_datetime(df['Fecha'], errors='coerce')
            
            df['Fecha'] = fechas_convertidas
                
        except Exception as e:
            pass  # Silencioso
    
    def _process_values_silent(self, df):
        """Procesar valores silenciosamente"""
        try:
            if 'Valor' not in df.columns:
                return
            
            # Convertir valores a numérico
            if df['Valor'].dtype == 'object':
                df['Valor'] = (df['Valor']
                              .astype(str)
                              .str.replace(',', '.')
                              .str.strip())
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
                
        except Exception as e:
            pass  # Silencioso
    
    def _normalize_values_silent(self, df):
        """
        Normalización de valores entre 0 y 1:
        - Si Calculo = "promedio": promedio de valores normalizados de últimos 4 años
        - Si Calculo = "acumulado": suma de valores de últimos 4 años, luego normalizar
        - Si tiene Meta: valor/Meta (Meta es 1), nunca pasa de 1
        - Si NO tiene Meta y hay datos históricos: min-max normalization
        - Si NO tiene Meta y NO hay datos históricos: asigna 0.7
        """
        try:
            if df.empty or 'Valor' not in df.columns or 'Fecha' not in df.columns:
                return

            # Inicializar valores normalizados como "sin dato" (NaN), no como 0.
            # Un período sin valor reportado no equivale a un desempeño de 0%;
            # debe quedar como dato faltante para que las gráficas muestren un vacío, no una caída a cero.
            df['Valor_Normalizado'] = np.nan

            # Verificar que tenemos datos válidos
            valores_validos = df['Valor'].notna()
            if not valores_validos.any():
                return

            # Usar columna COD
            if 'COD' not in df.columns:
                return

            tiene_meta = 'Meta' in df.columns
            tiene_calculo = 'Calculo' in df.columns

            # Asegurar que Fecha es datetime
            if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
                df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

            # Agrupar por indicador usando COD
            for codigo in df['COD'].unique():
                if pd.isna(codigo):
                    continue

                mask = df['COD'] == codigo
                datos_indicador = df[mask].copy()
                valores = datos_indicador['Valor'].dropna()

                if valores.empty:
                    continue

                # Obtener información del indicador
                indicador_info = datos_indicador.iloc[0]
                meta_valor = indicador_info.get('Meta') if tiene_meta else None
                calculo = indicador_info.get('Calculo', '').lower().strip() if tiene_calculo else ''

                # === CASO ESPECIAL: PROMEDIO ===
                if calculo == 'promedio':
                    self._normalize_promedio(df, datos_indicador, meta_valor)

                # === CASO ESPECIAL: ACUMULADO ===
                elif calculo == 'acumulado':
                    self._normalize_acumulado(df, datos_indicador, meta_valor)

                # === CASOS NORMALES ===
                else:
                    # Normalización estándar (sin considerar últimos 4 años)
                    if pd.notna(meta_valor) and meta_valor > 0:
                        # TIENE META: Meta es 1 (100%), normalizar como valor/Meta
                        for index in datos_indicador.index:
                            valor = datos_indicador.loc[index, 'Valor']
                            if pd.notna(valor):
                                valor_norm = valor / meta_valor
                                df.at[index, 'Valor_Normalizado'] = min(1.0, max(0.0, valor_norm))

                    elif len(valores) > 1:
                        # NO tiene Meta pero SÍ hay datos históricos: min-max normalization
                        max_valor = valores.max()
                        min_valor = valores.min()
                        rango = max_valor - min_valor

                        if rango > 0:
                            for index in datos_indicador.index:
                                valor = datos_indicador.loc[index, 'Valor']
                                if pd.notna(valor):
                                    valor_norm = (valor - min_valor) / rango
                                    df.at[index, 'Valor_Normalizado'] = min(1.0, max(0.0, valor_norm))
                        else:
                            # Todos los valores históricos son iguales
                            for index in datos_indicador.index:
                                if pd.notna(datos_indicador.loc[index, 'Valor']):
                                    df.at[index, 'Valor_Normalizado'] = 0.7

                    else:
                        # NO tiene Meta y NO hay datos históricos: asignar 0.7
                        for index in datos_indicador.index:
                            if pd.notna(datos_indicador.loc[index, 'Valor']):
                                df.at[index, 'Valor_Normalizado'] = 0.7

        except Exception as e:
            # Fallback silencioso
            pass

    def _normalize_promedio(self, df, datos_indicador, meta_valor):
        """
        Normalización tipo PROMEDIO: para cada año, promedio de valores normalizados de ese año y los 3 anteriores
        """
        try:
            # Ordenar por fecha ascendente
            datos_ordenados = datos_indicador.sort_values('Fecha', ascending=True).copy()
            datos_ordenados['Año'] = datos_ordenados['Fecha'].dt.year

            # Obtener min y max de TODOS los valores históricos del indicador (para min-max)
            todos_valores = datos_indicador['Valor'].dropna()
            min_historico = todos_valores.min()
            max_historico = todos_valores.max()
            rango = max_historico - min_historico

            # Para cada registro, calcular promedio con sus 3 años anteriores
            for index in datos_ordenados.index:
                año_actual = datos_ordenados.loc[index, 'Año']

                # Obtener datos de este año y los 3 anteriores
                años_ventana = [año_actual - i for i in range(4)]
                datos_ventana = datos_ordenados[datos_ordenados['Año'].isin(años_ventana)]

                if datos_ventana.empty:
                    df.at[index, 'Valor_Normalizado'] = 0.7
                    continue

                # Normalizar cada valor en la ventana
                valores_normalizados = []
                for _, row in datos_ventana.iterrows():
                    valor = row['Valor']
                    if pd.notna(valor):
                        if pd.notna(meta_valor) and meta_valor > 0:
                            # Con meta: valor/meta
                            valor_norm = min(1.0, max(0.0, valor / meta_valor))
                        elif rango > 0:
                            # Sin meta: min-max
                            valor_norm = (valor - min_historico) / rango
                            valor_norm = min(1.0, max(0.0, valor_norm))
                        elif len(todos_valores) == 1:
                            valor_norm = 0.7
                        else:
                            valor_norm = 0.7
                        valores_normalizados.append(valor_norm)

                # Calcular promedio para este año
                if valores_normalizados:
                    promedio_norm = sum(valores_normalizados) / len(valores_normalizados)
                else:
                    promedio_norm = 0.7

                df.at[index, 'Valor_Normalizado'] = promedio_norm

        except Exception as e:
            # Fallback
            for index in datos_indicador.index:
                df.at[index, 'Valor_Normalizado'] = 0.7

    def _normalize_acumulado(self, df, datos_indicador, meta_valor):
        """
        Normalización tipo ACUMULADO: para cada año, suma de valores de ese año y los 3 anteriores, luego normalizar
        """
        try:
            # Ordenar por fecha ascendente
            datos_ordenados = datos_indicador.sort_values('Fecha', ascending=True).copy()
            datos_ordenados['Año'] = datos_ordenados['Fecha'].dt.year

            # Calcular todas las sumas posibles de ventanas de 4 años para min-max
            todos_años = sorted(datos_ordenados['Año'].unique())
            sumas_historicas = []

            for año_ref in todos_años:
                años_ventana = [año_ref - i for i in range(4)]
                datos_ventana = datos_ordenados[datos_ordenados['Año'].isin(años_ventana)]
                if not datos_ventana.empty:
                    suma_ventana = datos_ventana['Valor'].sum()
                    sumas_historicas.append(suma_ventana)

            # Min y max de las sumas históricas
            if len(sumas_historicas) > 1:
                min_suma = min(sumas_historicas)
                max_suma = max(sumas_historicas)
                rango_suma = max_suma - min_suma
            else:
                min_suma = 0
                max_suma = 0
                rango_suma = 0

            # Para cada registro, calcular suma acumulada con sus 3 años anteriores
            for index in datos_ordenados.index:
                año_actual = datos_ordenados.loc[index, 'Año']

                # Obtener datos de este año y los 3 anteriores
                años_ventana = [año_actual - i for i in range(4)]
                datos_ventana = datos_ordenados[datos_ordenados['Año'].isin(años_ventana)]

                if datos_ventana.empty:
                    df.at[index, 'Valor_Normalizado'] = 0.7
                    continue

                # Sumar valores de la ventana
                suma_valores = datos_ventana['Valor'].sum()

                # Normalizar la suma
                if pd.notna(meta_valor) and meta_valor > 0:
                    # Con meta: normalizar contra meta acumulada (meta * número de años en ventana)
                    num_años_ventana = len(años_ventana)
                    meta_acumulada = meta_valor * num_años_ventana
                    valor_norm = min(1.0, max(0.0, suma_valores / meta_acumulada))
                elif rango_suma > 0:
                    # Sin meta: min-max sobre sumas históricas
                    valor_norm = (suma_valores - min_suma) / rango_suma
                    valor_norm = min(1.0, max(0.0, valor_norm))
                else:
                    # Sin rango o datos insuficientes
                    valor_norm = 0.7

                df.at[index, 'Valor_Normalizado'] = valor_norm

        except Exception as e:
            # Fallback
            for index in datos_indicador.index:
                df.at[index, 'Valor_Normalizado'] = 0.7

    def _calculate_recalculated_values(self, df, fichas_data):
        """
        Calcular valores recalculados ajustados por inflación
        Si VPN=1 en Fichas, ajustar el valor por inflación acumulada
        """
        try:
            from datetime import datetime

            # Inicializar columna Valor_Recalculado
            df['Valor_Recalculado'] = df['Valor'].copy()

            # Verificar que tenemos las columnas necesarias
            if 'COD' not in df.columns or 'Valor' not in df.columns or 'Fecha' not in df.columns:
                return

            # Año actual como referencia para ajustar
            año_actual = datetime.now().year

            # Crear diccionario de VPN por código de indicador
            vpn_dict = {}
            if 'COD' in fichas_data.columns and 'VPN' in fichas_data.columns:
                for _, ficha in fichas_data.iterrows():
                    codigo = ficha.get('COD')
                    vpn = ficha.get('VPN')
                    if pd.notna(codigo) and pd.notna(vpn):
                        try:
                            vpn_dict[str(codigo).strip()] = int(vpn)
                        except:
                            vpn_dict[str(codigo).strip()] = 0

            # Procesar cada registro
            for index, row in df.iterrows():
                codigo = str(row.get('COD', '')).strip()
                valor = row.get('Valor')
                fecha = row.get('Fecha')

                # Verificar si debe ajustarse por inflación
                if codigo in vpn_dict and vpn_dict[codigo] == 1:
                    # VPN=1: Ajustar por inflación
                    if pd.notna(valor) and pd.notna(fecha):
                        try:
                            # Obtener año del registro
                            if isinstance(fecha, pd.Timestamp):
                                año_registro = fecha.year
                            elif isinstance(fecha, str):
                                año_registro = pd.to_datetime(fecha).year
                            else:
                                año_registro = None

                            if año_registro and año_registro <= año_actual:
                                # Calcular factor de inflación acumulada
                                factor_inflacion = calcular_factor_inflacion_acumulada(año_registro, año_actual)

                                # Aplicar ajuste
                                valor_recalculado = valor * factor_inflacion
                                df.at[index, 'Valor_Recalculado'] = valor_recalculado
                            else:
                                # Año inválido: mantener valor original
                                df.at[index, 'Valor_Recalculado'] = valor
                        except Exception as e:
                            # Error al procesar: mantener valor original
                            df.at[index, 'Valor_Recalculado'] = valor
                else:
                    # VPN != 1 o no tiene VPN: mantener valor original
                    df.at[index, 'Valor_Recalculado'] = valor

        except Exception as e:
            # Fallback: Valor_Recalculado = Valor
            try:
                df['Valor_Recalculado'] = df['Valor']
            except:
                pass

    def _add_default_columns_corrected(self, df):
        """Añadir columnas por defecto - VERSIÓN SILENCIOSA"""
        try:
            # Meta - NO establecer valor por defecto, dejar NaN si no existe
            if 'Meta' not in df.columns:
                df['Meta'] = pd.NA
            else:
                # Solo convertir a numérico, mantener NaN como NaN
                df['Meta'] = pd.to_numeric(df['Meta'], errors='coerce')

            # Peso por defecto
            if 'Peso' not in df.columns:
                df['Peso'] = 1.0
            else:
                df['Peso'] = pd.to_numeric(df['Peso'], errors='coerce').fillna(1.0)

            # Tipo por defecto
            if 'Tipo' not in df.columns:
                df['Tipo'] = 'porcentaje'

        except Exception as e:
            pass  # Silencioso
    
    def _verify_dataframe_simple(self, df):
        """Verificar DataFrame"""
        try:
            if df.empty:
                return True

            # Verificar columnas esenciales (permitir variantes de nombres)
            required_columns = ['COD', 'Fecha', 'Valor']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return False

            # Verificar que tenga al menos componente/categoría e indicador (con nombres flexibles)
            has_componente = any(col in df.columns for col in ['Componente', 'COMPONENTE PROPUESTO'])
            has_categoria = any(col in df.columns for col in ['Categoria', 'Categoría', 'CATEGORÍA'])
            has_indicador = any(col in df.columns for col in ['Indicador', 'Nombre de indicador', 'Nombre_Indicador'])

            if not (has_componente and has_categoria and has_indicador):
                return False

            # Limpiar registros vacíos
            initial_count = len(df)
            df.dropna(subset=['COD'], inplace=True)
            
            return True
            
        except Exception as e:
            return False
    
    def get_data_source_info(self):
        """Obtener información de la fuente"""
        if self.sheets_manager:
            return {
                'source': 'Google Sheets',
                'connection_info': self.sheets_manager.get_connection_info()
            }
        else:
            return {
                'source': 'Google Sheets (No conectado)',
                'connection_info': {'connected': False}
            }

class DataProcessor:
    """Clase para procesar datos - VERSIÓN CORREGIDA"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """Calcular puntajes usando normalización simple - APLICANDO FILTRO DE FECHA"""
        try:
            if df.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # ✅ APLICAR FILTRO DE FECHA SI SE PROPORCIONA
            if fecha_filtro is not None:
                # Convertir fecha_filtro a datetime si es necesario
                if not pd.api.types.is_datetime64_any_dtype(pd.Series([fecha_filtro])):
                    fecha_filtro = pd.to_datetime(fecha_filtro)
                
                # Filtrar por la fecha específica
                df_filtrado = df[df['Fecha'] == fecha_filtro].copy()
                
                if df_filtrado.empty:
                    # Si no hay datos para esa fecha exacta, usar los más cercanos
                    fechas_disponibles = df['Fecha'].dropna().sort_values()
                    fecha_mas_cercana = fechas_disponibles[fechas_disponibles <= fecha_filtro]
                    
                    if not fecha_mas_cercana.empty:
                        fecha_usar = fecha_mas_cercana.iloc[-1]  # La más reciente antes o igual
                        df_filtrado = df[df['Fecha'] == fecha_usar].copy()
                    else:
                        # Si no hay fechas anteriores, usar la primera disponible
                        fecha_usar = fechas_disponibles.iloc[0]
                        df_filtrado = df[df['Fecha'] == fecha_usar].copy()
            else:
                # Sin filtro de fecha, usar valores más recientes por indicador
                df_filtrado = DataProcessor._get_latest_values_by_indicator(df)
            
            if df_filtrado.empty:
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Resto del método permanece igual...
            required_columns = ['Valor_Normalizado', 'Peso', 'Componente', 'Categoria']
            if not all(col in df_filtrado.columns for col in required_columns):
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Calcular puntajes por componente
            puntajes_componente = df_filtrado.groupby('Componente', group_keys=False).apply(
                lambda x: (x['Valor_Normalizado'] * x['Peso']).sum() / x['Peso'].sum(),
                include_groups=False
            ).reset_index()
            puntajes_componente.columns = ['Componente', 'Puntaje_Ponderado']

            # Calcular puntajes por categoría
            puntajes_categoria = df_filtrado.groupby('Categoria', group_keys=False).apply(
                lambda x: (x['Valor_Normalizado'] * x['Peso']).sum() / x['Peso'].sum(),
                include_groups=False
            ).reset_index()
            puntajes_categoria.columns = ['Categoria', 'Puntaje_Ponderado']
            
            # Calcular puntaje general
            peso_total = df_filtrado['Peso'].sum()
            if peso_total > 0:
                puntaje_general = (df_filtrado['Valor_Normalizado'] * df_filtrado['Peso']).sum() / peso_total
            else:
                puntaje_general = df_filtrado['Valor_Normalizado'].mean()
            
            return puntajes_componente, puntajes_categoria, puntaje_general
            
        except Exception as e:
            st.error(f"Error en cálculo de puntajes: {e}")
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
    
    @staticmethod
    def _get_latest_values_by_indicator(df):
        """Obtener valores más recientes por indicador"""
        try:
            if df.empty:
                return df
            
            # Verificar columnas necesarias
            if not all(col in df.columns for col in ['COD', 'Fecha', 'Valor']):
                return df

            # Limpiar datos
            df_clean = df.dropna(subset=['COD', 'Fecha', 'Valor'])

            if df_clean.empty:
                return df

            # Obtener valores más recientes
            df_latest = (df_clean
                        .sort_values(['COD', 'Fecha'])
                        .groupby('COD')
                        .last()
                        .reset_index())
            
            return df_latest
            
        except Exception as e:
            st.error(f"Error al obtener valores recientes: {e}")
            return df

class DataEditor:
    """Clase para editar datos - VERSIÓN CORREGIDA"""
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path=None):
        """Agregar nuevo registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                st.error("❌ Google Sheets no disponible")
                return False
            
            sheets_manager = GoogleSheetsManager()
            
            # Buscar información base
            if df.empty:
                st.error("❌ No hay datos base disponibles")
                return False
            
            indicador_existente = df[df['COD'] == codigo]
            if indicador_existente.empty:
                st.error(f"❌ No se encontró el código {codigo}")
                return False
            
            indicador_base = indicador_existente.iloc[0]
            
            # Preparar datos
            data_dict = {
                'COMPONENTE PROPUESTO': indicador_base.get('Componente', ''),
                'CATEGORÍA': indicador_base.get('Categoria', ''),
                'COD': codigo,
                'Nombre de indicador': indicador_base.get('Indicador', ''),
                'Valor': valor,
                'Fecha': fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else str(fecha),
                'Tipo': indicador_base.get('Tipo', 'porcentaje')
            }
            
            # Agregar a Google Sheets
            return sheets_manager.add_record(data_dict)
            
        except Exception as e:
            st.error(f"❌ Error al agregar: {e}")
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path=None):
        """Actualizar registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                return False
            
            sheets_manager = GoogleSheetsManager()
            return sheets_manager.update_record(codigo, fecha, nuevo_valor)
            
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path=None):
        """Eliminar registro"""
        try:
            if not GOOGLE_SHEETS_AVAILABLE:
                return False
            
            sheets_manager = GoogleSheetsManager()
            return sheets_manager.delete_record(codigo, fecha)
            
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            return False

class SheetsDataLoader:
    """NUEVA CLASE: Cargador de datos metodológicos desde Google Sheets"""
    
    def __init__(self):
        self.sheets_manager = None
        
        if GOOGLE_SHEETS_AVAILABLE:
            try:
                self.sheets_manager = GoogleSheetsManager()
            except Exception as e:
                st.error(f"❌ Error al inicializar Google Sheets para fichas: {e}")
    
    def load_fichas_data(self):
        """Cargar datos de fichas metodológicas desde Google Sheets"""
        try:
            if not self.sheets_manager:
                return None
            
            fichas_df = self.sheets_manager.load_fichas_data()
            
            if fichas_df is None:
                return None
            
            if fichas_df.empty:
                return pd.DataFrame()
            
            # Limpiar y procesar fichas usando COD
            if 'COD' in fichas_df.columns:
                fichas_df = fichas_df.dropna(subset=['COD'], how='all')

            return fichas_df
            
        except Exception as e:
            st.error(f"❌ Error al cargar fichas desde Sheets: {e}")
            return None
    
    def add_ficha(self, ficha_data):
        """Agregar nueva ficha metodológica"""
        try:
            if not self.sheets_manager:
                return False
            
            return self.sheets_manager.add_ficha_record(ficha_data)
            
        except Exception as e:
            st.error(f"❌ Error al agregar ficha: {e}")
            return False
    
    def update_ficha(self, codigo, campo, nuevo_valor):
        """Actualizar campo de ficha metodológica"""
        try:
            if not self.sheets_manager:
                return False
            
            return self.sheets_manager.update_ficha_record(codigo, campo, nuevo_valor)
            
        except Exception as e:
            st.error(f"❌ Error al actualizar ficha: {e}")
            return False

# Mantener compatibilidad con ExcelDataLoader para transición gradual
class ExcelDataLoader:
    """CLASE OBSOLETA: Mantenida para compatibilidad pero ya no se usa"""
    
    def __init__(self):
        st.warning("⚠️ ExcelDataLoader obsoleto. Ahora se usan fichas de Google Sheets.")
    
    def load_excel_data(self):
        """Método obsoleto"""
        st.info("📋 Cargando fichas desde Google Sheets en lugar de Excel...")
        
        # Redirigir a SheetsDataLoader
        sheets_loader = SheetsDataLoader()
        return sheets_loader.load_fichas_data()
