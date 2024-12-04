import os
from flask import Flask, request, jsonify
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

# Initialisation de l'API Facebook avec les informations d'identification
ACCESS_TOKEN = 'EAALAhLDRjTcBO4zyVuIVDmGvGYTkAlVeomK424zboUkAX2XEVluHHQ1dZBTfcSco81gBmyT6QWwcPScZAazbZA1VlTqaY2b0fHjlLPfrRS42kutByYCJajdwsroBE9kF0FTdADuuDbOoLcu1AQ9qDOs9i6wf6ZAZAGoWpO8yPadreZAkodyRcowiT7ZBhkVQW0DCdFwBbonJ6g0AZCF98Lf5W30enJVXhqx6QQZDZD'
APP_ID = '774626088160567'
APP_SECRET = '6a099ee373ff66d298b5e1001a3bdbdc'
AD_ACCOUNT_ID = 'act_1248987406405056'

FacebookAdsApi.init(access_token=ACCESS_TOKEN, app_id=APP_ID, app_secret=APP_SECRET)

# Configuration du serveur Flask
app = Flask(__name__)

@app.route('/create-campaign', methods=['POST'])
def create_campaign():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "Invalid input data"}), 400

    try:
        # Créer la campagne
        ad_account = AdAccount(AD_ACCOUNT_ID)
        params = {
            'name': data.get('name'),
            'objective': data.get('objective'),
            'status': data.get('status', 'PAUSED'),
            'special_ad_categories': data.get('special_ad_category', ['NONE']),
            'buying_type': data.get('buying_type', 'AUCTION'),
        }
        campaign = ad_account.create_campaign(params=params)

        # Créer le groupe d'annonces (ad set)
        adset_params = {
            'name': f"{data.get('name')} - Ad Set",
            'campaign_id': campaign[Campaign.Field.id],
            'status': data.get('status', 'PAUSED'),
            'daily_budget': data.get('daily_budget'),
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': data.get('optimization_goal'),
            'targeting': data.get('targeting', {}),
        }

        adset = ad_account.create_adset(params=adset_params)

        # Créer la publicité (Ad Creative)
        creative_params = {
            'name': f"{data.get('name')} - Creative",
            'object_story_spec': {
                'link_data': {
                    'link': data.get('creative').get('link'),
                    'message': data.get('creative').get('body'),
                    'image_hash': data.get('creative').get('image_hash'),
                },
                'page_id': data.get('creative').get('page_id')
            }
        }

        creative = ad_account.create_ad_creative(params=creative_params)

        # Créer l'annonce (Ad)
        ad_params = {
            'name': f"{data.get('name')} - Ad",
            'adset_id': adset[AdSet.Field.id],
            'creative': {
                'creative_id': creative[AdCreative.Field.id],
            },
            'status': data.get('status', 'PAUSED'),
        }

        ad = ad_account.create_ad(params=ad_params)

        return jsonify({
            "status": "success",
            "campaign_id": campaign[Campaign.Field.id],
            "adset_id": adset[AdSet.Field.id],
            "ad_id": ad[Ad.Field.id]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    # Port configuré pour Render ou par défaut à 5000
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
