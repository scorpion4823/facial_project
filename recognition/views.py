from django.shortcuts import render, redirect
from .models import Person
import numpy as np
import cv2
from .forms import PersonForm
import face_recognition
import os
import tempfile


def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_personne')
    else:
        form = PersonForm()
    return render(request, 'add_personne.html', {'form': form})


def index(request):
    return render(request, 'index.html')


def load_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return np.ascontiguousarray(image, dtype=np.uint8)


def save_temp_image(image_file):
    suffix = os.path.splitext(image_file.name)[-1] or '.jpg'
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    for chunk in image_file.chunks():
        temp.write(chunk)
    temp.close()
    return temp.name


def recognize_person(request):
    result = None
    person_found = None

    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        temp_path = None

        try:
            temp_path = save_temp_image(uploaded_image)
            unknown_image = load_image(temp_path)
            unknown_encodings = face_recognition.face_encodings(unknown_image)

            if not unknown_encodings:
                result = "Aucun visage détecté ❌"
            else:
                unknown_encoding = unknown_encodings[0]
                persons = Person.objects.all()
                best_match = None
                best_distance = 0.55

                for person in persons:
                    try:
                        known_image = load_image(person.image.path)
                        known_encodings = face_recognition.face_encodings(known_image)

                        if not known_encodings:
                            continue

                        distance = face_recognition.face_distance(
                            [known_encodings[0]], unknown_encoding
                        )[0]

                        if distance < best_distance:
                            best_distance = distance
                            best_match = person

                    except Exception:
                        continue

                if best_match:
                    person_found = best_match
                else:
                    result = "Personne non reconnue ❌"

        except Exception as e:
            result = f"Erreur : {str(e)}"

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return render(request, 'recognize.html', {
        'result': result,
        'person': person_found,
    })