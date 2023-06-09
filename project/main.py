from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
import cloudinary
from cloudinary.uploader import upload, destroy
import requests, urllib
from . import db
from datetime import datetime
from .models import User, Predict

main = Blueprint('main', __name__)

def get_image_id_from_url(image_url):
    # Extraire le public_id de l'URL de l'image
    public_id = image_url.split('/')[-1].split('.')[0]
    return public_id

@main.route('/supprimer_image_cloudinary', methods=['GET' , 'POST'])
def supprimer_image_cloudinary():
    cloudinary.config(
    cloud_name = "dcjkfjdiv",
    api_key = "668559953486661",
    api_secret = "vVQ6CyNlSr8qCt54zMbstlLKZdY"
    )
    image_url = request.json['url']
    public_id = get_image_id_from_url(image_url)

    # Supprimer la ressource (image)
    response = destroy(public_id, resource_type = "image")

    if response['result'] == 'ok':
        print("L'image a été supprimée avec succès.")
    else:
        print("Une erreur s'est produite lors de la suppression de l'image.")

@main.route('/', methods=['GET' , 'POST'])
def index():
    if request.method == 'POST' and 'photo' in request.files:
        cloudinary.config(
        cloud_name = "dcjkfjdiv",
        api_key = "668559953486661",
        api_secret = "vVQ6CyNlSr8qCt54zMbstlLKZdY"
        )

        file = request.files['photo']
        
        upload_result = upload(file)
        image_url = upload_result['secure_url']
        print(image_url)

        selected_option = request.form.get('selected_option')
        print(selected_option)

        button = 'wait'

        if selected_option == "": # if a user is found, we want to redirect back to signup page so user can try again
            flash('Please select a language to start recognition')
            return redirect(url_for('main.index'))
        
        return render_template('render.html', url=image_url, button=button, language=selected_option)
    return render_template('index.html')

@main.route('/profile', methods=['GET' , 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.json
        prediction_idList = data['predictionId']
        print(prediction_idList)

        for prediction_id in prediction_idList:
            print(prediction_id)
            prediction = Predict.query.get(prediction_id)
            if prediction:
                db.session.delete(prediction)
                db.session.commit()
                print('message: Prédiction supprimée')
            else:
                print('message: Prédiction non trouvée')

            return redirect(url_for('main.profile'))


    return render_template('profile.html',user_name=current_user.name, user_id=current_user.id, predictions=current_user.predictions)

@main.route('/render', methods=['POST'])
@login_required
def render_save():
    ocr_text = request.form.get('textpredict')
    url = request.form.get('imageurl')
    title = request.form.get('title')

    existing_prediction = Predict.query.filter_by(title=title, text=ocr_text, user_id=current_user.id).first()
    if existing_prediction is None:
        # Aucune prédiction avec le même titre, texte et utilisateur n'existe
        # Ajoutez la nouvelle prédiction à la base de données
        prediction = Predict(title=title, text=ocr_text, date=datetime.now(), user_id=current_user.id)
        db.session.add(prediction)
        db.session.commit()
        print('New Entry')
    else:
        # Une prédiction avec le même titre, texte et utilisateur existe déjà
        print('Already saved')
    
    button = 'validate'

    return render_template('render.html', ocr_text=ocr_text, url=url, button=button)

@main.route('/mobile')
def mobile():
    return render_template('mobile.html')

@main.route('/blog')
def blog():
    return render_template('blog.html')

@main.route('/about_us')
def about_us():
    return render_template('about_us.html')

@main.route('/services')
def services():
    return render_template('services.html')