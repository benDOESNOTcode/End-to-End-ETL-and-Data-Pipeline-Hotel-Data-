#Hotel Reservation Analytics Pipeline & Web Dashboard

##Overview
This project is an end-to-end data analytics pipeline designed to process, analyze, and visualize hotel reservation data from **2015–2018**.

The system performs:
- **Data ingestion** from raw CSV files  
- **Cleaning, validation, and normalization** using PySpark  
- **Database loading** into a Dockerized PostgreSQL instance  
- **Interactive visualization** through a web dashboard  

This project was completed as part of the **CS 236 — Database Management Systems** course at **UC Riverside**.

---

##Tech Stack

### 🔹 Data Processing
- **PySpark 3.5.1**  
  Used for scalable ETL, data cleaning, transformation, and schema normalization.

### 🔹 Database
- **PostgreSQL 16 (Dockerized)**  
  All processed data is loaded into a relational schema optimized for analytical queries.

### 🔹 Backend
- **Flask (Python)**  
- **SQLAlchemy ORM**  
- **psycopg2 PostgreSQL driver**

### 🔹 Frontend
- **Vanilla JavaScript (ES6+)**  
- **Bootstrap 5**  
- **HTML5/CSS3**

### 🔹 Containerization
- **Docker & Docker Compose**

---

##Project Architecture

### **1. Phase 1 & 2 — Data Engineering (ETL)**  
PySpark handles the heavy lifting for our ETL pipeline.

####  **Ingestion**  
- Loaded two raw datasets (2015–2018) into Spark DataFrames  
- Performed schema validation and type casting

####  **Transformation & Cleaning**
- Handled missing values  
- Normalized date formats  
- Standardized categorical fields  
- Removed duplicates  
- Applied domain-specific business rules

####  **Load**
- Exported cleaned datasets as CSV  
- Used Python scripts + psycopg2 to load them into PostgreSQL  

---

## **2. Phase 3 — Web Dashboard & API Layer**

### 🔹 Flask Backend  
The backend exposes RESTful endpoints to query the normalized database, including:
- Filtering by year, hotel type, booking status  
- Revenue, cancellations, and guest analytics  
- Aggregation queries for dashboards

### 🔹 JavaScript Frontend  
The dashboard supports:
- Dynamic filters  
- Real-time table updates  
- Visual charts (Bootstrap + custom JS)  
- Clean responsive layout

---

##  Final Features
- End-to-end ETL processing using **PySpark**
- Fully containerized setup using **Docker**
- Normalized relational database schema in **PostgreSQL**
- REST API using **Flask + SQLAlchemy**
- Interactive analytics dashboard with filtering controls
- Queryable visual insights into reservation trends, cancellations, and customer behavior

---
