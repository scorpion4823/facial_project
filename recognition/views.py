from django.shortcuts import render, redirect
from .models import Person
import numpy as np
import cv2
from PIL import Image
from deepface import DeepFace
from .forms import PersonForm
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
    debug_info = []  # Pour voir ce qui se passe

    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        temp_path = None

        try:
            temp_path = save_temp_image(uploaded_image)
            persons = Person.objects.all()

            if not persons:
                result = "Aucune personne enregistrée dans la base ❌"
            else:
                best_match = None
                best_distance = float('inf')

                for person in persons:
                    try:
                        verification = DeepFace.verify(
                            img1_path=temp_path,
                            img2_path=person.image.path,
                            model_name="Facenet",
                            detector_backend="opencv",
                            enforce_detection=False,
                            silent=True
                        )

                        distance = verification["distance"]
                        verified = verification["verified"]
                        threshold = verification["threshold"]

                        # Log pour debug
                        debug_info.append(
                            f"{person} → distance: {round(distance, 4)} / seuil: {threshold} → {'✅' if verified else '❌'}"
                        )

                        if distance < best_distance:
                            best_distance = distance
                            if verified:
                                best_match = person

                    except FileNotFoundError:
                        continue
                    except Exception as e:
                        debug_info.append(f"Erreur pour {person}: {str(e)}")
                        continue

                if best_match:
                    person_found = best_match
                else:
                    result = f"Personne non reconnue ❌ (meilleure distance: {round(best_distance, 4)})"

        except Exception as e:
            result = f"Erreur : {str(e)}"

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return render(request, 'recognize.html', {
        'result': result,
        'person': person_found,
        'debug_info': debug_info,  # À afficher temporairement dans le template
    })