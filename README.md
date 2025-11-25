# Textio – Mini E-commerce Platform

A mini e-commerce platform built using Django.  
Includes session-based authentication, product variants, a full cart system, and Razorpay integration — all designed with a clean, responsive UI.

---

## 🚀 Features

### **User Features**
- Session-based login and authentication  
- Product listing and product detail pages  
- Variant-based product selection  
- Session-based cart (add/remove/update quantity)  
- “Buy Now” flow  
- Full checkout system  
- Razorpay integrated for online payments  
- Responsive user dashboard  

### **Admin Features**
- Manage products  
- Manage variants  
- Manage coupons and discount rules  
- Manage orders  
- Simple, clean Django admin interface  

---

## 🧩 Tech Stack

- **Backend:** Django, Python  
- **Frontend:** HTML, CSS, Tailwind  
- **Database:** SQLite  
- **Payments:** Razorpay  
- **Tools:** Git, GitHub  

---

## 📂 Project Structure

```
projecttextio/
|
├── apptextio
|    |     
|    ├── migrations/
|    ├── templates/
|    └── # project .py files
|
├── projecttextio/# project config
└── manage.py
```

---

## 🛠️ Setup Instructions

```bash
git clone https://github.com/Mohan3C/Textio.git
cd Textio

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📜 License

For portfolio and learning use.

---