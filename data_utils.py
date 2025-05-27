"""
Utilidades para el manejo de datos del Dashboard ICE
"""

import pandas as pd
import os
import streamlit as st
from config import COLUMN_MAPPING, DEFAULT_META, CSV_SEPARATOR, CSV_FILENAME

class DataLoader:
    """Clase para cargar y procesar datos del CSV"""
    
    def __init__(self):
        self.df = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.script_dir, CSV_FILENAME)
    
    def load_data(self):
        """Cargar datos desde el archivo CSV - CORREGIDO"""
        try:
            # Cargar el archivo CSV con punto y coma como separador
            self.df = pd.read_csv(self.csv_path, sep=CSV_SEPARATOR)
            
            import streamlit as st
            # Debug: Mostrar estructura original del CSV
            with st.expander("🔧 Debug: Estructura del CSV cargado", expanded=False):
                st.write(f"**Archivo:** {self.csv_path}")
                st.write(f"**Shape original:** {self.df.shape}")
                st.write(f"**Columnas originales:** {list(self.df.columns)}")
                if not self.df.empty:
                    st.write("**Primeras filas:**")
                    st.dataframe(self.df.head())
            
            # Renombrar columnas
            self._rename_columns()
            
            # Debug: Mostrar después del renombrado
            with st.expander("🔧 Debug: Después del renombrado de columnas", expanded=False):
                st.write(f"**Columnas después del renombrado:** {list(self.df.columns)}")
                
            # Procesar fechas y valores
            self._process_dates()
            self._process_values()
            
            # Añadir columnas por defecto
            self._add_default_columns()
            
            # Verificación final
            required_final_columns = ['Codigo', 'Fecha', 'Valor', 'Componente', 'Categoria', 'Indicador']
            missing_final = [col for col in required_final_columns if col not in self.df.columns]
            if missing_final:
                st.error(f"❌ Faltan columnas esenciales después del procesamiento: {missing_final}")
                st.write("**Columnas disponibles:**", list(self.df.columns))
                return None
            
            # Limpiar datos problemáticos
            self.df = self.df.dropna(subset=['Codigo', 'Fecha', 'Valor'])
            
            if self.df.empty:
                st.error("❌ No hay datos válidos después de la limpieza")
                return None
                
            st.success(f"✅ Datos cargados correctamente: {len(self.df)} registros, {self.df['Codigo'].nunique()} indicadores únicos")
            
            return self.df
            
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error crítico al cargar datos: {e}")
            import traceback
            st.code(traceback.format_exc())
            return None
    
    def _rename_columns(self):
        """Renombrar columnas según el mapeo"""
        for original, nuevo in COLUMN_MAPPING.items():
            if original in self.df.columns:
                self.df = self.df.rename(columns={original: nuevo})
    
    def _process_dates(self):
        """Procesar columna de fechas - CORREGIDO para múltiples formatos"""
        import streamlit as st
        
        try:
            # Debug: Mostrar fechas originales
            with st.expander("🔧 Debug: Procesamiento de fechas", expanded=False):
                st.write("**Fechas originales (primeras 10):**")
                st.write(self.df['Fecha'].head(10).tolist())
                st.write(f"**Tipos de datos originales:** {self.df['Fecha'].dtype}")
                
                # Mostrar ejemplos de diferentes formatos encontrados
                unique_samples = self.df['Fecha'].dropna().astype(str).unique()[:5]
                st.write(f"**Ejemplos de formatos encontrados:** {list(unique_samples)}")
            
            # Lista de formatos de fecha a intentar
            date_formats = [
                '%d/%m/%Y',    # 01/01/2025
                '%d-%m-%Y',    # 01-01-2025  
                '%Y-%m-%d',    # 2025-01-01
                '%Y/%m/%d',    # 2025/01/01
                '%m/%d/%Y',    # 01/01/2025 (formato US)
                '%d.%m.%Y',    # 01.01.2025
            ]
            
            fechas_convertidas = None
            formato_exitoso = None
            
            # Intentar cada formato
            for formato in date_formats:
                try:
                    fechas_convertidas = pd.to_datetime(self.df['Fecha'], format=formato, errors='coerce')
                    # Verificar si la conversión fue exitosa (menos de 50% de NaT)
                    porcentaje_validas = (fechas_convertidas.notna().sum() / len(fechas_convertidas)) * 100
                    
                    if porcentaje_validas >= 50:  # Si al menos 50% se convirtieron bien
                        formato_exitoso = formato
                        st.success(f"✅ Formato exitoso: {formato} ({porcentaje_validas:.1f}% válidas)")
                        break
                    else:
                        st.warning(f"⚠️ Formato {formato}: solo {porcentaje_validas:.1f}% válidas")
                        
                except ValueError as e:
                    st.info(f"ℹ️ Formato {formato} no compatible: {e}")
                    continue
            
            # Si ningún formato específico funcionó, usar conversión automática
            if fechas_convertidas is None or formato_exitoso is None:
                st.warning("⚠️ Ningún formato específico funcionó, intentando conversión automática...")
                try:
                    fechas_convertidas = pd.to_datetime(self.df['Fecha'], errors='coerce', dayfirst=True)
                    formato_exitoso = "automático (dayfirst=True)"
                except Exception as e:
                    st.error(f"❌ Error en conversión automática: {e}")
                    fechas_convertidas = pd.to_datetime(self.df['Fecha'], errors='coerce')
                    formato_exitoso = "automático (estándar)"
            
            # Aplicar las fechas convertidas
            self.df['Fecha'] = fechas_convertidas
            
            # Análisis de resultados
            fechas_validas = self.df['Fecha'].notna().sum()
            fechas_invalidas = self.df['Fecha'].isna().sum()
            
            # Debug: Mostrar resultados de conversión
            with st.expander("🔧 Debug: Resultados de conversión", expanded=False):
                st.write(f"**Formato usado:** {formato_exitoso}")
                st.write(f"**Fechas válidas:** {fechas_validas}")
                st.write(f"**Fechas inválidas:** {fechas_invalidas}")
                
                if fechas_validas > 0:
                    st.write("**Fechas convertidas (muestra):**")
                    st.write(self.df[self.df['Fecha'].notna()]['Fecha'].head().tolist())
                
                if fechas_invalidas > 0:
                    st.write("**Fechas problemáticas:**")
                    fechas_problematicas = self.df[self.df['Fecha'].isna()]['Fecha'].head()
                    st.write(list(fechas_problematicas))
            
            # Filtrar filas con fechas inválidas solo si hay muchas
            if fechas_invalidas > 0:
                if fechas_invalidas <= 5:  # Si son pocas, solo avisar
                    st.warning(f"⚠️ Se encontraron {fechas_invalidas} filas con fechas inválidas (se mantendrán para revisión)")
                else:  # Si son muchas, excluir
                    st.warning(f"⚠️ Se encontraron {fechas_invalidas} filas con fechas inválidas que serán excluidas del análisis")
                    self.df = self.df.dropna(subset=['Fecha'])
                    
        except Exception as e:
            st.error(f"❌ Error crítico al procesar fechas: {e}")
            import traceback
            st.code(traceback.format_exc())
            # En caso de error, intentar conversión básica
            try:
                self.df['Fecha'] = pd.to_datetime(self.df['Fecha'], errors='coerce')
            except:
                st.error("❌ No se pudieron procesar las fechas en absoluto")
                pass
    
    def _process_values(self):
        """Procesar valores numéricos"""
        if self.df['Valor'].dtype == 'object':
            self.df['Valor'] = self.df['Valor'].str.replace(',', '.').astype(float)
    
    def _add_default_columns(self):
        """Añadir columnas por defecto si no existen"""
        if 'Meta' not in self.df.columns:
            self.df['Meta'] = DEFAULT_META
        
        # Asignar peso igual a todos los indicadores (será normalizado por componente)
        if 'Peso' not in self.df.columns:
            self.df['Peso'] = 1.0

class DataProcessor:
    """Clase para procesar y calcular métricas de los datos"""
    
    @staticmethod
    def calculate_scores(df, fecha_filtro=None):
        """
        Calcular puntajes usando SIEMPRE el valor más reciente de cada indicador.
        CORREGIDO: Manejo robusto de errores y validaciones.
        """
        try:
            if df.empty:
                import streamlit as st
                st.warning("DataFrame vacío para cálculo de puntajes")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # SIEMPRE usar el valor más reciente de cada indicador
            df_filtrado = DataProcessor._get_latest_values_by_indicator(df)

            if len(df_filtrado) == 0:
                import streamlit as st
                st.error("No se pudieron obtener valores más recientes de los indicadores")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # Debug: Verificar estructura del DataFrame
            import streamlit as st
            with st.expander("🔧 Debug: Estructura de datos para cálculos", expanded=False):
                st.write(f"**Shape del DataFrame filtrado:** {df_filtrado.shape}")
                st.write(f"**Columnas disponibles:** {list(df_filtrado.columns)}")
                st.write(f"**Tipos de datos:**")
                st.write(df_filtrado.dtypes)
                if len(df_filtrado) > 0:
                    st.write("**Muestra de datos:**")
                    st.dataframe(df_filtrado.head())

            # Verificar columnas esenciales
            required_columns = ['Valor', 'Peso', 'Componente', 'Categoria']
            missing_columns = [col for col in required_columns if col not in df_filtrado.columns]
            if missing_columns:
                st.error(f"Faltan columnas esenciales: {missing_columns}")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0

            # Normalizar valores (0-1)
            df_filtrado['Valor_Normalizado'] = df_filtrado['Valor'].clip(0, 1)
            
            # Verificar que tenemos datos después de la normalización
            if df_filtrado['Valor_Normalizado'].isna().all():
                st.error("Todos los valores normalizados son NaN")
                return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                       pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
            
            # Calcular puntajes por componente
            try:
                puntajes_componente = DataProcessor._calculate_weighted_average_by_group(
                    df_filtrado, 'Componente'
                )
            except Exception as e:
                st.error(f"Error al calcular puntajes por componente: {e}")
                puntajes_componente = pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []})
            
            # Calcular puntajes por categoría
            try:
                puntajes_categoria = DataProcessor._calculate_weighted_average_by_group(
                    df_filtrado, 'Categoria'
                )
            except Exception as e:
                st.error(f"Error al calcular puntajes por categoría: {e}")
                puntajes_categoria = pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []})
            
            # Calcular puntaje general
            try:
                peso_total = df_filtrado['Peso'].sum()
                if peso_total > 0:
                    puntaje_general = (df_filtrado['Valor_Normalizado'] * df_filtrado['Peso']).sum() / peso_total
                else:
                    puntaje_general = df_filtrado['Valor_Normalizado'].mean()
                
                # Verificar que el puntaje general es válido
                if pd.isna(puntaje_general):
                    puntaje_general = 0.0
                    
            except Exception as e:
                st.error(f"Error al calcular puntaje general: {e}")
                puntaje_general = 0.0

            return puntajes_componente, puntajes_categoria, puntaje_general
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error crítico en calculate_scores: {e}")
            import traceback
            st.code(traceback.format_exc())
            return pd.DataFrame({'Componente': [], 'Puntaje_Ponderado': []}), \
                   pd.DataFrame({'Categoria': [], 'Puntaje_Ponderado': []}), 0
    
    @staticmethod
    def _get_latest_values_by_indicator(df):
        """
        Obtener el valor más reciente de cada indicador.
        CORREGIDO: Evita problemas de estructura multidimensional.
        """
        try:
            if df.empty:
                return df
            
            # Verificar que tenemos las columnas necesarias
            required_columns = ['Codigo', 'Fecha', 'Valor']
            if not all(col in df.columns for col in required_columns):
                import streamlit as st
                st.error(f"Faltan columnas requeridas: {required_columns}")
                return df
            
            # Remover filas con valores NaN en columnas críticas
            df_clean = df.dropna(subset=['Codigo', 'Fecha', 'Valor']).copy()
            
            if df_clean.empty:
                import streamlit as st
                st.warning("No hay datos válidos después de limpiar valores NaN")
                return df
            
            # MÉTODO CORREGIDO: Usar sort_values y drop_duplicates
            # Esto evita problemas con groupby().apply()
            df_latest = (df_clean
                        .sort_values(['Codigo', 'Fecha'])  # Ordenar por código y fecha
                        .groupby('Codigo', as_index=False)  # Agrupar por código
                        .last()  # Tomar el último registro de cada grupo
                        .reset_index(drop=True))  # Resetear índice
            
            import streamlit as st
            # Mostrar información de debug solo si hay problemas
            debug_info = len(df_clean['Codigo'].unique()) != len(df_latest)
            if debug_info:
                with st.expander("🔍 Debug: Valores más recientes por indicador", expanded=False):
                    st.write(f"**Total indicadores únicos en datos originales:** {df_clean['Codigo'].nunique()}")
                    st.write(f"**Registros después de filtrar:** {len(df_latest)}")
                    st.write(f"**Estructura del DataFrame resultante:** {df_latest.shape}")
                    st.dataframe(df_latest[['Codigo', 'Indicador', 'Valor', 'Fecha', 'Componente']].sort_values('Fecha'))
            
            return df_latest
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error crítico al obtener valores más recientes: {e}")
            import traceback
            st.code(traceback.format_exc())
            # En caso de error, retornar DataFrame original como fallback
            return df
    
    @staticmethod
    def _calculate_weighted_average_by_group(df, group_column):
        """Calcular promedio ponderado por grupo - CORREGIDO para evitar errores dimensionales"""
        try:
            # Verificar que el DataFrame y la columna de agrupación son válidos
            if df.empty:
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            if group_column not in df.columns:
                import streamlit as st
                st.error(f"La columna '{group_column}' no existe en los datos")
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            # Verificar que tenemos las columnas necesarias
            required_cols = ['Valor_Normalizado', 'Peso']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                import streamlit as st
                st.error(f"Faltan columnas necesarias: {missing_cols}")
                return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
            
            # Función para calcular promedio ponderado
            def weighted_avg(valores, pesos):
                """Calcular promedio ponderado de forma segura"""
                # Filtrar valores no nulos
                mask = pd.notna(valores) & pd.notna(pesos)
                if not mask.any():
                    return 0.0
                
                valores_clean = valores[mask]
                pesos_clean = pesos[mask]
                peso_total = pesos_clean.sum()
                
                if peso_total > 0:
                    return (valores_clean * pesos_clean).sum() / peso_total
                else:
                    return valores_clean.mean() if len(valores_clean) > 0 else 0.0
            
            # Calcular promedio ponderado por grupo usando agg()
            result = df.groupby(group_column).agg({
                'Valor_Normalizado': list,
                'Peso': list
            }).reset_index()
            
            # Aplicar la función de promedio ponderado
            result['Puntaje_Ponderado'] = result.apply(
                lambda row: weighted_avg(
                    pd.Series(row['Valor_Normalizado']), 
                    pd.Series(row['Peso'])
                ), axis=1
            )
            
            # Mantener solo las columnas necesarias
            result = result[[group_column, 'Puntaje_Ponderado']]
            
            return result
            
        except Exception as e:
            import streamlit as st
            st.error(f"Error en cálculo ponderado por {group_column}: {e}")
            import traceback
            st.code(traceback.format_exc())
            # Retornar DataFrame vacío pero con estructura correcta
            return pd.DataFrame(columns=[group_column, 'Puntaje_Ponderado'])
    
    @staticmethod
    def create_pivot_table(df, fecha=None, filas='Categoria', columnas='Componente', valores='Valor'):
        """Crear tabla dinámica (función legacy - ya no se usa)"""
        return pd.DataFrame()  # Función deshabilitada

class DataEditor:
    """Clase para editar datos con operaciones CRUD completas"""
    
    @staticmethod
    def save_edit(df, codigo, fecha, nuevo_valor, csv_path):
        """Guardar edición de un indicador (función heredada para compatibilidad)"""
        return DataEditor.update_record(df, codigo, fecha, nuevo_valor, csv_path)
    
    @staticmethod
    def add_new_record(df, codigo, fecha, valor, csv_path):
        """Agregar un nuevo registro para un indicador - CORREGIDO formato de fecha"""
        try:
            # Leer el CSV actual para mantener el formato original
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            
            # Debug: Ver formato de fechas existentes
            import streamlit as st
            with st.expander("🔧 Debug: Formato de fechas en CSV", expanded=False):
                st.write("**Fechas existentes en CSV:**")
                st.write(df_actual['Fecha'].head().tolist())
                st.write(f"**Fecha nueva a agregar:** {fecha}")
                st.write(f"**Tipo de fecha nueva:** {type(fecha)}")
            
            # Obtener información base del indicador desde df_actual
            codigo_col = None
            for col_name in ['COD', 'Codigo']:
                if col_name in df_actual.columns:
                    codigo_col = col_name
                    break
            
            if codigo_col is None:
                st.error("❌ No se encontró columna de código en el CSV")
                return False
            
            # Buscar información base del indicador
            indicadores_existentes = df_actual[df_actual[codigo_col] == codigo]
            if len(indicadores_existentes) == 0:
                st.error(f"❌ No se encontró información base para el código {codigo}")
                return False
                
            indicador_base = indicadores_existentes.iloc[0]
            
            # IMPORTANTE: Convertir fecha al formato correcto del CSV
            # Detectar formato de fechas existentes en el CSV
            sample_date = df_actual['Fecha'].dropna().iloc[0] if len(df_actual['Fecha'].dropna()) > 0 else None
            
            if sample_date:
                # Si las fechas existentes están en formato d/m/Y, usar ese formato
                if '/' in str(sample_date):
                    fecha_formateada = fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else pd.to_datetime(fecha).strftime('%d/%m/%Y')
                else:
                    # Si están en otro formato, usar ISO
                    fecha_formateada = fecha.strftime('%Y-%m-%d') if hasattr(fecha, 'strftime') else pd.to_datetime(fecha).strftime('%Y-%m-%d')
            else:
                # Por defecto usar formato d/m/Y que es el esperado por el sistema
                fecha_formateada = fecha.strftime('%d/%m/%Y') if hasattr(fecha, 'strftime') else pd.to_datetime(fecha).strftime('%d/%m/%Y')
            
            # Debug: Mostrar formato final
            with st.expander("🔧 Debug: Fecha formateada", expanded=False):
                st.write(f"**Fecha original:** {fecha}")
                st.write(f"**Fecha formateada:** {fecha_formateada}")
                st.write(f"**Formato detectado en CSV:** {sample_date}")
            
            # Crear nueva fila manteniendo la estructura original del CSV
            nueva_fila = {}
            for col in df_actual.columns:
                if col == 'Fecha':
                    nueva_fila[col] = fecha_formateada  # Usar fecha formateada
                elif col == 'Valor':
                    nueva_fila[col] = valor
                else:
                    # Mantener el valor original de la primera fila del indicador
                    nueva_fila[col] = indicador_base[col]
            
            # Agregar nueva fila al DataFrame
            df_nuevo = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)
            
            # Guardar al CSV manteniendo el formato original
            df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
            
            # Debug: Verificar que se guardó correctamente
            with st.expander("🔧 Debug: Verificación de guardado", expanded=False):
                df_verificacion = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
                st.write(f"**Registros totales después de guardar:** {len(df_verificacion)}")
                st.write("**Últimas 3 filas guardadas:**")
                st.dataframe(df_verificacion.tail(3))
            
            # FORZAR recarga completa del cache
            st.cache_data.clear()
            if 'data_timestamp' not in st.session_state:
                st.session_state.data_timestamp = 0
            st.session_state.data_timestamp += 1
            
            return True
            
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error al agregar nuevo registro: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    @staticmethod
    def update_record(df, codigo, fecha, nuevo_valor, csv_path):
        """Actualizar un registro existente - CORREGIDO"""
        try:
            # Leer el CSV actual con el mismo separador
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            
            # Procesar fechas si es necesario
            df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')
            
            # Determinar la columna de código correcta
            codigo_col = None
            for col_name in ['COD', 'Codigo']:
                if col_name in df_actual.columns:
                    codigo_col = col_name
                    break
            
            if codigo_col is None:
                import streamlit as st
                st.error("❌ No se encontró columna de código en el CSV (COD o Codigo)")
                return False
            
            # Encontrar el índice del registro a actualizar
            idx = df_actual[(df_actual[codigo_col] == codigo) & (df_actual['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                # Actualizar el valor
                df_actual.loc[idx, 'Valor'] = nuevo_valor
                # Guardar al CSV manteniendo el formato original
                df_actual.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                
                # Forzar recarga de datos en Streamlit
                import streamlit as st
                if 'data_timestamp' not in st.session_state:
                    st.session_state.data_timestamp = 0
                st.session_state.data_timestamp += 1
                
                return True
            else:
                import streamlit as st
                st.error(f"❌ No se encontró registro para código {codigo} en fecha {fecha.strftime('%d/%m/%Y')}")
                # Debug: mostrar registros disponibles para este código
                registros_codigo = df_actual[df_actual[codigo_col] == codigo]
                if not registros_codigo.empty:
                    st.write("**Registros disponibles para este código:**")
                    st.dataframe(registros_codigo[['Fecha', 'Valor']])
                return False
                
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error al actualizar el registro: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
    
    @staticmethod
    def delete_record(df, codigo, fecha, csv_path):
        """Eliminar un registro existente - CORREGIDO"""
        try:
            # Leer el CSV actual
            df_actual = pd.read_csv(csv_path, sep=CSV_SEPARATOR)
            
            # Procesar fechas si es necesario
            df_actual['Fecha'] = pd.to_datetime(df_actual['Fecha'], errors='coerce')
            
            # Determinar la columna de código correcta
            codigo_col = None
            for col_name in ['COD', 'Codigo']:
                if col_name in df_actual.columns:
                    codigo_col = col_name
                    break
            
            if codigo_col is None:
                import streamlit as st
                st.error("❌ No se encontró columna de código en el CSV")
                return False
            
            # Encontrar el índice del registro a eliminar
            idx = df_actual[(df_actual[codigo_col] == codigo) & (df_actual['Fecha'] == fecha)].index
            
            if len(idx) > 0:
                # Eliminar la fila
                df_nuevo = df_actual.drop(idx).reset_index(drop=True)
                # Guardar al CSV
                df_nuevo.to_csv(csv_path, sep=CSV_SEPARATOR, index=False)
                
                # Forzar recarga de datos en Streamlit
                import streamlit as st
                if 'data_timestamp' not in st.session_state:
                    st.session_state.data_timestamp = 0
                st.session_state.data_timestamp += 1
                
                return True
            else:
                import streamlit as st
                st.error(f"❌ No se encontró registro para eliminar")
                return False
                
        except Exception as e:
            import streamlit as st
            st.error(f"❌ Error al eliminar el registro: {e}")
            import traceback
            st.code(traceback.format_exc())
            return False
