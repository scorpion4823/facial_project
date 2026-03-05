from django.shortcuts import render, redirect
from .models import Person
import numpy as np
import cv2
from PIL import Image
from deepface import DeepFace
from .forms import PersonForm
import os
import tempfile


# ============================
# Vue pour ajouter une personne
# ============================
def add_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('add_personne')
    else:
        form = PersonForm()
    return render(request, 'add_personne.html', {'form': form})


# ============================
# Vue page d'accueil
# ============================
def index(request):
    return render(request, 'index.html')


# ============================
# Fonction pour sauvegarder temporairement une image uploadée
# ============================
def save_temp_image(image_file):
    # Crée un fichier temporaire pour DeepFace (qui a besoin d'un chemin)
    suffix = os.path.splitext(image_file.name)[-1] or '.jpg'
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    for chunk in image_file.chunks():
        temp.write(chunk)
    temp.close()
    return temp.name


# ============================
# Vue pour reconnaître une personne
# ============================
def recognize_person(request):

    result = None
    person_found = None

    if request.method == 'POST' and request.FILES.get('image'):

        uploaded_image = request.FILES['image']
        temp_path = None

        try:
            # Sauvegarde l'image uploadée dans un fichier temporaire
            temp_path = save_temp_image(uploaded_image)

            # Récupère toutes les personnes enregistrées
            persons = Person.objects.all()

            if not persons:
                result = "Aucune personne enregistrée dans la base ❌"
            else:
                best_match = None
                best_distance = 0.6  # Seuil de reconnaissance

                for person in persons:
                    try:
                        # Vérifie si les deux visages correspondent
                        verification = DeepFace.verify(
                            img1_path=temp_path,
                            img2_path=person.image.path,
                            model_name="VGG-Face",
                            enforce_detection=False,
                            silent=True
                        )

                        distance = verification["distance"]

                        if verification["verified"] and distance < best_distance:
                            best_distance = distance
                            best_match = person

                    except FileNotFoundError:
                        continue
                    except Exception:
                        continue

                if best_match:
                    person_found = best_match
                else:
                    result = "Personne non reconnue ❌"

        except Exception as e:
            result = f"Erreur lors du traitement de l'image : {str(e)}"

        finally:
            # Supprime le fichier temporaire dans tous les cas
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    return render(request, 'recognize.html', {
        'result': result,
        'person': person_found,
    })