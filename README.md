# Foodifly - Premium Gourmet E-Commerce Platform

Foodifly is a full-stack Django-based e-commerce platform designed for gourmet food lovers. The platform provides a premium shopping experience with advanced product management, secure authentication, dynamic cart functionality, online payments, coupon management, wallet payments, order tracking, and a luxury-themed user interface.

---

## Features

### User Authentication

* Custom User Model using Email Authentication
* User Registration with OTP Verification
* Secure Login & Logout
* Password Reset Functionality
* Session Management

### Product Management

* Product Categories
* Product Variants (Weight / Size Based)
* Multiple Product Images
* Product Search
* Product Filtering & Sorting
* Related Product Recommendations
* Stock Management

### Shopping Features

* Add to Cart
* Update Cart Quantity
* Remove from Cart
* Wishlist Management
* Dynamic Variant Selection
* Offer Price Calculation
* Product-Level & Category-Level Offers

### Checkout & Payments

* Secure Checkout Process
* Address Management
* Multiple Payment Methods:

  * Cash on Delivery (COD)
  * Razorpay
  * Wallet Payment
* Coupon Application System
* Tax Calculation
* Order Confirmation Modal

### Order Management

* Order Placement
* Order Success Page
* Order Details Page
* Invoice Generation & Download
* Order Cancellation
* Product Return Requests
* Refund Management
* Order Status Tracking:

  * Pending
  * Confirmed
  * Shipped
  * Delivered
  * Cancelled
  * Returned

### Coupon System

* Create Coupons
* Edit Coupons
* Activate / Deactivate Coupons
* Percentage Discounts
* Fixed Discounts
* Minimum Purchase Validation
* Maximum Discount Limits
* Expiry Date Validation

### Wallet System

* Wallet Balance Management
* Wallet Transactions
* Wallet Payment Checkout
* Refunds to Wallet

### Admin Dashboard

* User Management
* Product Management
* Category Management
* Order Management
* Coupon Management
* Offer Management
* Banner Management
* Return Request Management
* Sales Reporting

---

## Tech Stack

### Backend

* Python 3
* Django 6
* PostgreSQL

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript
* AJAX

### Payment Gateway

* Razorpay

### Database

* PostgreSQL

### Styling

* Custom Luxury UI
* Playfair Display
* Inter Font

---

## Project Structure

```text
Foodifly/
│
├── accounts/
├── store/
├── cart/
├── wishlist/
├── orders/
├── coupon/
├── offers/
├── wallet/
├── admin_panel/
├── templates/
├── static/
├── media/
└── manage.py
```

---

## Installation

### Prerequisites

* Python 3.x
* PostgreSQL
* Git

---

### Clone Repository

```bash
git clone https://github.com/Sudheesh-0007/foodifly.git

cd foodifly
```

### Create Virtual Environment

```bash
python -m venv env
```

### Activate Environment

Windows:

```bash
env\Scripts\activate
```

Mac/Linux:

```bash
source env/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

DB_NAME=foodifly
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password

RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

### Apply Migrations

```bash
python manage.py makemigrations

python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Server

```bash
python manage.py runserver
```

Visit:

```text
http://127.0.0.1:8000/
```

---

## Current Modules Completed

Authentication System

Product Management

Category Management

Cart System

Wishlist System

Razorpay Integration

Wallet System

Coupon Management

Order Management

Return Management

Invoice Generation

Admin Dashboard

---

## Future Enhancements

* Product Reviews & Ratings
* Referral System
* Advanced Analytics Dashboard
* Inventory Reports
* Sales Charts

---

## Author

**Sudheesh EC**

Foodifly - Premium Gourmet E-Commerce Platform
