# PriceHub

PriceHub is a Python Django project that provides a platform for tracking and comparing prices of various products.

## Requirements

Before getting started, ensure that you have the following prerequisites installed on your system:

- Python (version 3.10)
- Django (version 4.2)
- Docker

## Installation

Follow these steps to set up the PriceHub project:

1. Clone the repository:

   ```
   git clone https://github.com/diyor28/pricehub.git
   ```

2. Navigate to the project directory:

   ```
   cd pricehub
   ```

3. Create a virtual environment:

   ```
   python -m venv venv
   ```

4. Activate the virtual environment:

   - For Windows:

     ```
     venv\Scripts\activate
     ```

   - For Unix/Linux:

     ```
     source venv/bin/activate
     ```

5. Install the project dependencies:

   ```
   pip install -r requirements.txt
   ```

6. Perform database migrations:

   ```
   python manage.py migrate
   ```

7. Start the development server:

   ```
   python manage.py runserver
   ```

8. Access the application in your browser:

   ```
   http://localhost:8000
   ```

## Usage
  - Creating an account or logging in
  - Adding products to track
  - Comparing prices
  - Managing user settings or preferences

## License

- GNU General Public License

## Support

Help - https://github.com/diyor28
