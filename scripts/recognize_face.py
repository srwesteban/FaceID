import cv2

def recognize_face(image_path):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('models/trainer.yml')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        face = img[y:y+h, x:x+w]
        id, confidence = recognizer.predict(face)
        if confidence < 50:  # Ajusta este umbral según sea necesario
            print(f"Face recognized with ID: {id}")
            return id
    print("Face not recognized")
    return None

if __name__ == "__main__":
    image_path = 'path/to/your/test/image.jpg'
    recognize_face(image_path)
