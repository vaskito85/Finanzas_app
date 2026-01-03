# 💰 Finanzas Personales — Streamlit + Supabase  
Gestión financiera moderna, simple y potente.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B)
![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-3ECF8E)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Aplicación web para registrar movimientos financieros, analizarlos con dashboards avanzados, generar alertas automáticas, importar CSV y proyectar balances futuros.  
Construida con **Python 3.13**, **Streamlit**, **Supabase Auth**, **Supabase Database**, **Pandas**, **Altair** y **NumPy**.

---

## 🎥 Demo (GIF)
> _Colocá aquí tu GIF de demostración cuando lo tengas_  
`/assets/demo.gif`

---

## ✨ Funcionalidades

### 🧾 Carga de movimientos
- Fecha  
- Tipo (ingreso / gasto)  
- Categoría  
- Cuenta (Santander, Mercado Pago, BullMarket, Balanz, Buenbit, Efectivo)  
- Descripción  
- Monto  
- Etiquetas (sugeridas + personalizadas)

---

### 📊 Resumen General
- Métricas de ingresos, gastos y balance  
- Evolución mensual  
- Ranking de categorías  
- Formato argentino  

---

### 📄 Listado de Movimientos
- Filtros avanzados  
- Exportación a CSV  
- Eliminación por ID  
- Tabla responsiva  

---

### 🏦 Balance por Cuenta
- Saldos actuales  
- Gráfico comparativo  
- Cálculo automático de ingresos/gastos  

---

### 📅 Dashboard Mensual
- Selección de mes  
- Métricas del mes  
- Evolución diaria  
- Ranking de categorías  

---

### 📊 Dashboard Anual
- Balance por año  
- Evolución anual  
- Categorías más relevantes  
- Distribución por categoría  

---

### 🔄 Comparación Mes a Mes
- Variación absoluta y porcentual  
- Gráfico comparativo  
- Categorías que más crecieron  

---

### 🚨 Alertas Automáticas
- Alertas por cuenta (mínimos y objetivos)  
- Alertas por categoría (límites)  
- Balance mensual negativo  
- Detección de gastos inusuales  
- Configuración mediante `objetivos.json`  

---

### 📥 Importación desde CSV
Carga masiva de movimientos desde un archivo CSV con columnas:

- fecha  
- categoria  
- tipo  
- descripcion  
- monto  
- cuenta  
- etiquetas (opcional)

---

### 🔮 Forecast Financiero
- Proyección lineal de los próximos 12 meses  
- Gráfico de tendencia  
- Estimaciones clave (3, 6 y 12 meses)  

---

## 🔐 Autenticación

La app utiliza **Supabase Auth** con:

- Registro  
- Login  
- Logout  
- Sesiones persistentes  
- Protección de páginas mediante `check_auth()`  

---

## 🗂️ Estructura del Proyecto


---

## 🎨 Estilos

La app utiliza un archivo `styles.css` personalizado para:

- Mejorar la experiencia móvil  
- Ajustar métricas  
- Hacer tablas responsivas  
- Mejorar inputs y botones  
- Unificar estética tipo dashboard  

---

## 🚀 Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py