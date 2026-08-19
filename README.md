# TechGear - Proyecto Full Stack

Este repositorio contiene la arquitectura base para el proyecto **TechGear**, dividida en servicios para el backend y frontend.

---

## 📁 Estructura del Proyecto

- `/techgear_api`: API REST asíncrona construida con **FastAPI**, **Motor** y **MongoDB Atlas**.
- `/techgear_web`: Aplicación web desarrollada con **Django** _(en desarrollo)_.

---

## 🚀 Guía de Inicio Rápido (Backend - FastAPI)

### 1. Requisitos Previos

- Python 3.10 o superior.
- Cuenta en MongoDB Atlas con una base de datos activa.

### 2. Configuración del Entorno

Navega a la carpeta del backend:

```bash
cd techgear_api

```
# TechGear - Proyecto Full Stack

Este repositorio contiene la arquitectura base para el proyecto **TechGear**, dividida en servicios para el backend y frontend.

---

## 📁 Estructura del Proyecto

```text
mongo/
├── .gitignore
├── README.md
│
├── techgear_api/  # Backend (FastAPI + MongoDB)
│   ├── .env
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
│
└── techgear_web/  # Frontend (Django) [En desarrollo]