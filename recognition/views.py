from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from .models import Person
import numpy as np
from PIL import Image
import face_recognition
from django.shortcuts import render
from .forms import PersonForm
import cv2

# ============================
# Vue pour ajouter une personne
# ============================
def add_person(request):
    # Vérifie si le formulaire est soumis (méthode POST)
    if request.method == 'POST':
        # On récupère les données envoyées (texte + image)
        form = PersonForm(request.POST, request.FILES)

        # Vérifie si les données sont valides
        if form.is_valid():
            # Sauvegarde la personne dans la base de données
            form.save()

            # Redirige vers la même page après enregistrement
            return redirect('add_personne')
    else:
        # Si ce n'est pas POST (ex: GET), on affiche un formulaire vide
        form = PersonForm()

    # Affiche la page avec le formulaire
    return render(request, 'add_personne.html', {'form': form})


# ============================
# Vue page d'accueil
# ============================
def index(request):
    # Affiche simplement la page index.html
    return render(request, 'index.html')


# ============================
# Fonction pour charger une image de manière robuste
# ============================
def load_image_robust(image_source, is_path=False):

    # Si l'image vient d'un chemin (image déjà stockée sur disque)
    if is_path:
        with open(image_source, 'rb') as f:
            # Lecture des bytes de l'image
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
    else:
        # Si l'image vient d'un upload (request.FILES)
        image_source.seek(0)  # Revenir au début du fichier
        file_bytes = np.frombuffer(image_source.read(), dtype=np.uint8)

    # Décodage de l'image avec OpenCV
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Vérifie si le décodage a échoué
    if image is None:
        raise ValueError("Impossible de décoder l'image.")

    # OpenCV charge en BGR → conversion en RGB (obligatoire pour face_recognition)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Assure que le tableau est continu en mémoire (important pour dlib)
    image = np.ascontiguousarray(image)

    # Force le format en uint8 propre
    image = np.array(image, dtype=np.uint8, order='C')

    return image


# ============================
# Vue pour reconnaître une personne
# ============================
def recognize_person(request):

    result = None          # Message d'erreur ou information
    person_found = None    # Personne reconnue

    # Vérifie que c'est une requête POST avec une image
    if request.method == 'POST' and request.FILES.get('image'):

        uploaded_image = request.FILES['image']

        try:
            # Charge l'image envoyée
            unknown_image = load_image_robust(uploaded_image)

            # Extraction des encodages faciaux (vecteur 128D)
            unknown_encodings = face_recognition.face_encodings(unknown_image)

            # Si aucun visage détecté
            if not unknown_encodings:
                result = "Aucun visage détecté dans l'image ❌"
            else:
                # On prend le premier visage détecté
                unknown_encoding = unknown_encodings[0]

                # Récupère toutes les personnes enregistrées
                persons = Person.objects.all()

                best_match = None
                best_distance = 0.6  # Seuil de reconnaissance (plus petit = plus strict)

                # Parcours toutes les personnes en base
                for person in persons:
                    try:
                        # Charge l'image enregistrée de la personne
                        known_image = load_image_robust(person.image.path, is_path=True)

                        # Extraire son encodage facial
                        known_encodings = face_recognition.face_encodings(known_image)

                        # Si aucun visage dans l'image enregistrée → on ignore
                        if not known_encodings:
                            continue

                        # Calcul de la distance entre les deux vecteurs
                        distance = face_recognition.face_distance(
                            [known_encodings[0]],
                            unknown_encoding
                        )[0]

                        # Si la distance est meilleure que la précédente
                        if distance < best_distance:
                            best_distance = distance
                            best_match = person

                    # Si fichier image introuvable → on ignore
                    except FileNotFoundError:
                        continue

                    # Ignore toute autre erreur pour éviter que le système plante
                    except Exception:
                        continue

                # Si on a trouvé une correspondance
                if best_match:
                    person_found = best_match
                else:
                    result = "Personne non reconnue ❌"

        # Gestion des erreurs globales
        except Exception as e:
            result = f"Erreur lors du traitement de l'image : {str(e)}"

    # Retourne le résultat vers la page HTML
    return render(request, 'recognize.html', {
        'result': result,
        'person': person_found,
    })