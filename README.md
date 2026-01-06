# 🛒 StudentMart  
**An E-Commerce Web Application for International Students**

StudentMart is a full-stack e-commerce web application built using **Flask** and **SQLite**, designed to help international students easily browse, search, and purchase grocery and kitchen items. The application supports **role-based access control**, **product image uploads**, **shopping cart functionality**, and a **responsive user interface**.

---

##  Features

###  User Features
- User registration and login
- Browse products by category
- Search products by name (Home page search)
- View product details with images
- Add products to shopping cart
- Update cart quantities
- Place orders and view order history

### Admin Features
- Admin-only access for product management
- Add new products with image upload
- Update existing products
- Delete products
- Upload and manage product images
- Role-based UI (admin buttons hidden for normal users)

---

##  Project Architecture

The project follows a **modular MVC-style architecture**:

- **Controller**: `app.py` (Flask routes and business logic)
- **Model**: `db/db.py` (database operations)
- **View**: `templates/` (Jinja2 HTML templates)
- **Static assets**: `static/` (CSS and uploaded images)

This structure improves maintainability and scalability.

---

##  Technologies Used

| Technology | Description |
|----------|------------|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling |
| Bootstrap | Responsive design |
| Jinja2 | Template rendering |
| Flask-WTF | CSRF protection |

---

##  Project Structure

'''StudentMart/
│
├── app.py
├── db/
│ ├── db.py
│ ├── database.db
│ ├── schema.sql
│ ├── init_db.py
│ └── migrate_*.py
│
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── products.html
│ ├── product.html
│ ├── product_form.html
│ ├── cart.html
│ ├── orders.html
│ ├── order_receipt.html
│ ├── login.html
│ └── register.html
│
├── static/
│ ├── styles.css
│ └── uploads/
│
├── venv/
└── README.md'''


---

##  Getting Started

### 1️ Clone the repository
```bash
git clone https://github.com/your-username/studentmart.git
cd StudentMart

### 2️ Create and activate virtual environment

python -m venv venv
venv\Scripts\activate   # Windows

3️ Install dependencies
pip install flask flask-wtf

4️ Initialize the database
python db/init_db.py

5️ Run the application
python app.py


Visit:

http://127.0.0.1:5000/

Image Upload Handling

Product images are uploaded via product creation and update forms

Images are stored in:

static/uploads/


Only the image path is saved in the database

Images are resized using CSS (object-fit) for consistent layout

 Security Features

Session-based authentication

CSRF protection using Flask-WTF

Role-based access control (Admin vs User)

Input validation for forms

Protected admin routes using decorators

 Testing

The application was tested manually for:

User authentication

Admin access restrictions

Product CRUD operations

Image upload and display

Cart and order processing

Search functionality

All features function as expected.

 Limitations

No online payment gateway

No email notifications

Single image per product

SQLite is not suitable for large-scale production use

 Future Enhancements

Payment gateway integration

Product ratings and reviews

Multiple images per product

Admin analytics dashboard

Order tracking and notifications

Advanced search and filtering options

 Academic Context

This project was developed as part of a university coursework to demonstrate:

Full-stack web development

Flask framework usage

Database-driven applications

Role-based access control

Secure form handling

👤 Author

Abhishekar
Geetanjali
EkpezuEgwu 
MSc Computing Students
Sheffield Hallam University

 License

This project is intended for educational purposes only.


---

