# E-commerce Project

This is an e-commerce project built using Django. It includes various features such as search and filter, user registration and login, product management, and a chat feature. The project uses Django Channels for asynchronous capabilities and WebSockets for real-time communication, with Redis as the message broker.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Search & Filter**: Allows users to search for products using various filters.
- **User Registration & Login**: Users can create accounts, log in, and change passwords.
- **Product Management**: Create, update, and delete products.
- **Product Detail & Reviews**: View detailed product pages with ratings and reviews.
- **Wishlist**: Users can add products to their wishlist.
- **Cart Management**: Add, remove, and update items in the cart.
- **Checkout**: Complete the purchase process.
- **Chat**: Real-time chat functionality using Django Channels and WebSockets.
- **Consumer and Vendor Dashboards**: Separate dashboards for consumers and vendors.

## Setup

To set up the project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone [repository URL]
    cd [repository name]
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database**:
    ```bash
    python manage.py migrate
    ```

5. **Create a superuser account** (for admin access):
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

7. **Set up Redis**:
    Make sure you have a Redis server running on your machine. You can specify the Redis connection details in your settings file.

8. **Start Django Channels**:
    ```bash
    python manage.py runserver 0.0.0.0:8000 --channel_layers "default:redis:localhost:6379"
    ```

## Usage

Once you have the project set up locally:

- Access the application in your browser at `http://localhost:8000/`.
- Log in using your superuser credentials to access the admin dashboard.
- Use the application as a consumer or vendor to test the features.

## Contributing

Contributions are welcome! If you'd like to contribute, please:

- Fork the repository.
- Create a new branch for your feature or bugfix.
- Submit a pull request.

Please follow the existing coding style and write tests for any new features.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use the code as you like, but remember to credit the original authors.
