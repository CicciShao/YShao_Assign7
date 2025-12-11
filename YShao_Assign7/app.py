from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ====================
# Database Connection
# ====================
def get_db_connection():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_categories():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return rows



# ====================
# Home Page
# ====================
@app.route('/')
def home():
    return render_template("index.html", categories=get_categories())



# ====================
# Category Page
# ====================
@app.route('/category')
def category():
    category_id = request.args.get("categoryId", type=int)

    conn = get_db_connection()

    # books in category
    books = conn.execute(
        "SELECT * FROM books WHERE categoryId = ?",
        (category_id,)
    ).fetchall()

    # category name
    cat_row = conn.execute(
        "SELECT name FROM categories WHERE id = ?",
        (category_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "categories.html",
        categories=get_categories(),
        books=books,
        selectedCategory=category_id,
        currentCategoryName=cat_row["name"]
    )



# ====================
# Book Detail Page
# ====================
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute("""
        SELECT books.*, categories.name AS categoryName
        FROM books
        JOIN categories ON categories.id = books.categoryId
        WHERE books.id = ?
    """, (book_id,)).fetchone()
    conn.close()

    return render_template("book_detail.html", book=book)



# ====================
# Search Page  ← MUST be BEFORE app.run()
# ====================
@app.route('/search', methods=['POST'])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM books WHERE lower(title) LIKE lower(?)",
        (f"%{term}%",)
    ).fetchall()
    conn.close()

    return render_template(
        "search.html",
        categories=get_categories(),
        books=books,
        term=term
    )



# ====================
# Error handling
# ====================
@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    print("=== ERROR ===")
    traceback.print_exc()
    return render_template("error.html", error=str(e))



# ====================
# Run app
# ====================
if __name__ == "__main__":
    app.run(debug=True)
