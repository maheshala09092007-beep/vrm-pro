from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import date
import os
import shutil
import uuid

from database import get_connection

app = FastAPI(title="Vehicle Management System")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "vehicles")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# =========================
# DASHBOARD
# =========================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):

    conn = get_connection()

    vehicles = []
    customers = []
    bookings = []
    bills = []

    if conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM vehicles ORDER BY vehicle_id DESC")
        vehicles = cur.fetchall()

        cur.execute("SELECT * FROM customers ORDER BY customer_id DESC")
        customers = cur.fetchall()

        cur.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
        bookings = cur.fetchall()

        cur.execute("SELECT * FROM bills ORDER BY bill_id DESC")
        bills = cur.fetchall()

        cur.close()
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "vehicles": vehicles,
            "customers": customers,
            "bookings": bookings,
            "bills": bills
        }
    )


# =========================
# VEHICLES
# =========================

@app.get("/vehicles", response_class=HTMLResponse)
def vehicles_page(request: Request):

    conn = get_connection()
    vehicles = []

    if conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT vehicle_id,
                   registration_no,
                   brand,
                   model,
                   vehicle_type,
                   price_per_day,
                   status,
                   image_path
            FROM vehicles
            ORDER BY vehicle_id DESC
        """)

        vehicles = cur.fetchall()

        cur.close()
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="vehicles.html",
        context={
            "request": request,
            "vehicles": vehicles
        }
    )


@app.post("/vehicles/add")
async def add_vehicle(
    registration_no: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    vehicle_type: str = Form(...),
    price_per_day: float = Form(...),
    image: UploadFile | None = File(None)
):

    image_path = None

    if image and image.filename:

        extension = os.path.splitext(image.filename)[1].lower()

        if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
            return HTMLResponse("Invalid image format.", status_code=400)

        filename = f"{uuid.uuid4().hex}{extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"vehicles/{filename}"

    conn = get_connection()

    if not conn:
        return HTMLResponse("Database connection failed.", status_code=500)

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO vehicles
            (registration_no, brand, model, vehicle_type, price_per_day, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            registration_no,
            brand,
            model,
            vehicle_type,
            price_per_day,
            image_path
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return HTMLResponse(f"Database error: {e}", status_code=500)

    finally:
        cur.close()
        conn.close()

    return RedirectResponse("/vehicles", status_code=303)


# =========================
# CUSTOMERS
# =========================

@app.get("/customers", response_class=HTMLResponse)
def customers_page(request: Request):

    conn = get_connection()
    customers = []

    if conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT customer_id,
                   name,
                   phone,
                   email,
                   license_number,
                   address
            FROM customers
            ORDER BY customer_id DESC
        """)

        customers = cur.fetchall()

        cur.close()
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={
            "request": request,
            "customers": customers
        }
    )


@app.post("/customers/add")
def add_customer(
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(""),
    license_number: str = Form(...),
    address: str = Form("")
):

    conn = get_connection()

    if not conn:
        return HTMLResponse("Database connection failed.", status_code=500)

    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO customers
            (name, phone, email, license_number, address)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            email,
            license_number,
            address
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"Customer error: {e}",
            status_code=400
        )

    finally:

        cur.close()
        conn.close()

    return RedirectResponse("/customers", status_code=303)


# =========================
# BOOKINGS
# =========================

@app.get("/bookings", response_class=HTMLResponse)
def bookings_page(request: Request):

    conn = get_connection()

    bookings = []
    customers = []
    vehicles = []

    if conn:

        cur = conn.cursor()

        cur.execute("""
            SELECT
                b.booking_id,
                c.name,
                v.brand,
                v.model,
                v.registration_no,
                b.start_date,
                b.end_date,
                b.status
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            ORDER BY b.booking_id DESC
        """)

        bookings = cur.fetchall()

        cur.execute("""
            SELECT customer_id, name
            FROM customers
            ORDER BY name
        """)

        customers = cur.fetchall()

        cur.execute("""
            SELECT vehicle_id,
                   brand,
                   model,
                   registration_no,
                   price_per_day
            FROM vehicles
            WHERE status != 'Maintenance'
            ORDER BY brand, model
        """)

        vehicles = cur.fetchall()

        cur.close()
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="bookings.html",
        context={
            "request": request,
            "bookings": bookings,
            "customers": customers,
            "vehicles": vehicles
        }
    )


@app.post("/bookings/add")
def add_booking(
    customer_id: int = Form(...),
    vehicle_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...)
):

    if end_date < start_date:
        return HTMLResponse(
            "End date cannot be before start date.",
            status_code=400
        )

    conn = get_connection()

    if not conn:
        return HTMLResponse("Database connection failed.", status_code=500)

    cur = conn.cursor()

    try:

        # Check vehicle
        cur.execute("""
            SELECT status
            FROM vehicles
            WHERE vehicle_id = ?
        """, (vehicle_id,))

        vehicle = cur.fetchone()

        if not vehicle:
            return HTMLResponse("Vehicle not found.", status_code=404)

        if vehicle[0] == "Maintenance":
            return HTMLResponse(
                "Vehicle is under maintenance.",
                status_code=400
            )

        # Check overlapping bookings
        cur.execute("""
            SELECT booking_id
            FROM bookings
            WHERE vehicle_id = ?
              AND status = 'Confirmed'
              AND start_date <= ?
              AND end_date >= ?
        """, (
            vehicle_id,
            end_date,
            start_date
        ))

        existing = cur.fetchone()

        if existing:
            return HTMLResponse(
                "Vehicle is already booked for these dates.",
                status_code=400
            )

        cur.execute("""
            INSERT INTO bookings
            (customer_id, vehicle_id, start_date, end_date, status)
            VALUES (?, ?, ?, ?, 'Confirmed')
        """, (
            customer_id,
            vehicle_id,
            start_date,
            end_date
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"Booking error: {e}",
            status_code=400
        )

    finally:

        cur.close()
        conn.close()

    return RedirectResponse("/bookings", status_code=303)


@app.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int):

    conn = get_connection()

    if conn:
        cur = conn.cursor()

        cur.execute("""
            UPDATE bookings
            SET status = 'Cancelled'
            WHERE booking_id = ?
        """, (booking_id,))

        conn.commit()

        cur.close()
        conn.close()

    return RedirectResponse("/bookings", status_code=303)


@app.post("/bookings/{booking_id}/complete")
def complete_booking(booking_id: int):

    conn = get_connection()

    if conn:
        cur = conn.cursor()

        cur.execute("""
            UPDATE bookings
            SET status = 'Completed'
            WHERE booking_id = ?
        """, (booking_id,))

        conn.commit()

        cur.close()
        conn.close()

    return RedirectResponse("/bookings", status_code=303)


# =========================
# BILLING
# =========================

@app.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request):

    conn = get_connection()

    bills = []
    bookings = []

    if conn:

        cur = conn.cursor()

        cur.execute("""
            SELECT
                b.bill_id,
                b.booking_id,
                c.name,
                v.brand,
                v.model,
                b.rental_amount,
                b.extra_charges,
                b.total_amount,
                b.payment_status,
                b.payment_method,
                b.bill_date
            FROM bills b
            JOIN bookings bk ON b.booking_id = bk.booking_id
            JOIN customers c ON bk.customer_id = c.customer_id
            JOIN vehicles v ON bk.vehicle_id = v.vehicle_id
            ORDER BY b.bill_id DESC
        """)

        bills = cur.fetchall()

        cur.execute("""
            SELECT
                bk.booking_id,
                c.name,
                v.brand,
                v.model,
                bk.start_date,
                bk.end_date,
                v.price_per_day
            FROM bookings bk
            JOIN customers c ON bk.customer_id = c.customer_id
            JOIN vehicles v ON bk.vehicle_id = v.vehicle_id
            WHERE bk.status != 'Cancelled'
              AND bk.booking_id NOT IN (
                  SELECT booking_id FROM bills
              )
            ORDER BY bk.booking_id DESC
        """)

        bookings = cur.fetchall()

        cur.close()
        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="billing.html",
        context={
            "request": request,
            "bills": bills,
            "bookings": bookings
        }
    )


@app.post("/billing/add")
def add_bill(
    booking_id: int = Form(...),
    extra_charges: float = Form(0),
    payment_method: str = Form(...)
):

    conn = get_connection()

    if not conn:
        return HTMLResponse("Database connection failed.", status_code=500)

    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                DATEDIFF(end_date, start_date),
                v.price_per_day
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.booking_id = ?
        """, (booking_id,))

        result = cur.fetchone()

        if not result:
            return HTMLResponse("Booking not found.", status_code=404)

        days = result[0]
        price_per_day = float(result[1])

        # Minimum 1 rental day
        days = max(days, 1)

        rental_amount = days * price_per_day
        total_amount = rental_amount + extra_charges

        cur.execute("""
            INSERT INTO bills
            (
                booking_id,
                rental_amount,
                extra_charges,
                total_amount,
                payment_status,
                payment_method,
                bill_date
            )
            VALUES (?, ?, ?, ?, 'Pending', ?, ?)
        """, (
            booking_id,
            rental_amount,
            extra_charges,
            total_amount,
            payment_method,
            date.today()
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        return HTMLResponse(
            f"Billing error: {e}",
            status_code=400
        )

    finally:

        cur.close()
        conn.close()

    return RedirectResponse("/billing", status_code=303)


@app.post("/billing/{bill_id}/paid")
def mark_bill_paid(bill_id: int):

    conn = get_connection()

    if conn:

        cur = conn.cursor()

        cur.execute("""
            UPDATE bills
            SET payment_status = 'Paid'
            WHERE bill_id = ?
        """, (bill_id,))

        conn.commit()

        cur.close()
        conn.close()

    return RedirectResponse("/billing", status_code=303)
