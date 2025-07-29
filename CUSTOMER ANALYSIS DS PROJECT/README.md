# 🛍 Customer Shopping Behavior Analysis using Machine Learning

This project presents a full data science pipeline from **synthetic data generation** to **model evaluation**, focused on understanding customer shopping trends and predicting shopping behavior. It simulates a real-world retail environment using the `Faker` library and dives deep into preprocessing, analysis, and performance comparison before and after cleaning the data.

---

## 📊 Project Overview

**Goal:** To analyze customer shopping trends and evaluate how preprocessing improves the performance of machine learning models.

**Highlights:**
- Synthetic dataset generation using `Faker`
- Deep preprocessing: handling nulls, encoding, and feature selection
- Comparative analysis of model performance **before vs after data preprocessing**
- Clear visualization of model metrics including ROC, Confusion Matrix, and Classification Reports

---

## 🧱 Dataset

The dataset was generated with:
- 1500 customer records
- Features such as: `Item Purchased`, `Review Rating`, `Shipping Type`, `Color`, `Size`, `Payment Method`, `Purchase Date`, `Purchase Frequency`, etc.
- Controlled missing values to simulate real-world data quality issues

---

## 📈 Key Steps

### 🔧 1. Data Generation
- Used `Faker` to simulate customer shopping data
- Introduced random null values in specific features to simulate data imperfections

### 🧹 2. Data Preprocessing
- Handled missing values
- Encoded categorical variables
- Normalized and scaled data where needed
- Feature selection and correlation analysis

### 🤖 3. Modeling
- Applied classification models to predict shopping behavior (e.g., category preference or purchase pattern)
- Evaluated model performance on:
  - **Raw (uncleaned) data**
  - **Cleaned (preprocessed) data**

### 📊 4. Visualization & Evaluation
- Confusion Matrix
- ROC Curves (Before & After preprocessing)
- Classification Reports
- Correlation heatmaps, missing value maps, histograms, box plots

---

## 🧠 Tools & Libraries Used

- Python
- Pandas, NumPy
- Matplotlib, Seaborn
- Faker (for data generation)
- Scikit-learn (for modeling and evaluation)
