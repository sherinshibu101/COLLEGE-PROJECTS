# 🔐 Phishing Website Detection using Machine Learning

This project presents a machine learning solution to detect phishing websites based on various features extracted from URLs and web content. Phishing attacks pose serious threats to online security, and this model aims to classify whether a given website is **legitimate** or **phishing**.

---

## 📂 Dataset

The project utilizes the open-source dataset from Hugging Face:  
[LochanaAbeywickrama/phishing](https://huggingface.co/datasets/LochanaAbeywickrama/phishing)

The dataset includes several features extracted from websites (e.g., presence of SSL, domain info, etc.) along with a binary target variable `phishing`.

---

## 🧠 Key Steps

1. **Data Loading & Preprocessing**
   - Loaded the dataset using the `datasets` library
   - Converted the training and validation sets into pandas DataFrames
   - Removed any missing or null values to ensure clean input

2. **Exploratory Data Analysis**
   - Inspected class distribution to verify balance between phishing and legitimate sites
   - Visualized feature correlation using heatmaps to understand relationships

3. **Modeling (details inside notebook)**
   - Split the data into features (`X`) and target (`y`)
   - Trained classification models and evaluated performance on a validation set
   - Metrics such as accuracy, precision, recall, and F1-score were used for assessment

---

## 📈 Objective

To develop an effective phishing detection model that can help cybersecurity systems automatically flag suspicious websites.

---

## 🔧 Technologies Used

- Python
- Pandas & NumPy
- Matplotlib & Seaborn (for visualization)
- Hugging Face `datasets`
- Scikit-learn (for modeling)

---

## 💡 What This Demonstrates

- Practical application of machine learning for cybersecurity
- Ability to work with real-world, messy datasets
- Understanding of class imbalance and evaluation metrics
- End-to-end ML workflow from data loading to model evaluation

---

## 📎 Files Included

- `22355.ipynb`: Complete notebook with data analysis, preprocessing, modeling, and evaluation
- `README.md`: Project overview

---

## 👨‍💻 Author

**SHERIN SHIBU**  
Computer Science Undergrad | Aspiring Data Scientist  
[www.linkedin.com/in/sherin-shibu-4628a1319]

---

## 📫 Contact

Feel free to reach out for collaboration or opportunities related to ML and cybersecurity!

