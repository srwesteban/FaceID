# Face Recognition Project

This project uses OpenCV and Flask to create a face recognition system that can authenticate users based on their facial features.

## Setup

1. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

2. Prepare your dataset:
    - Add images of your face to the `dataset/` folder. Name the files as `1.jpg`, `2.jpg`, etc.

3. Train the model:
    ```bash
    python scripts/train_model.py
    ```

4. Run the Flask application:
    ```bash
    python app.py
    ```

## Usage

- Send a POST request to `http://localhost:5000/login` with an image file to authenticate.

