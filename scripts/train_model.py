import face_recognition
import os
import pickle


def train_model(dataset_path):
    known_encodings = []
    known_names = []

    # Verificar que el directorio de datos existe
    if not os.path.exists(dataset_path):
        print(f"Error: el directorio '{dataset_path}' no existe.")
        return

    # Obtener la lista de imágenes con extensiones .jpg y .jpeg
    image_paths = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path) if f.endswith(('.jpg', '.jpeg'))]

    if not image_paths:
        print(f"No se encontraron imágenes en el directorio '{dataset_path}'.")
        return

    for image_path in image_paths:
        try:
            print(f"Procesando {image_path}")
            image = face_recognition.load_image_file(image_path)

            encodings = face_recognition.face_encodings(image)

            if encodings:
                print(f"Codificación generada para {image_path}")
                known_encodings.append(encodings[0])
                name = os.path.split(image_path)[-1].split(".")[0]
                known_names.append(name)
            else:
                print(f"No se encontró codificación facial para {image_path}")

        except Exception as e:
            print(f"Error procesando {image_path}: {e}")

    if not os.path.exists('models'):
        os.makedirs('models')

    data = {"encodings": known_encodings, "names": known_names}
    with open('models/face_enc', 'wb') as f:
        pickle.dump(data, f)
    print(f"Modelo entrenado con {len(known_encodings)} rostros")


if __name__ == "__main__":
    dataset_path = 'dataset'
    train_model(dataset_path)
