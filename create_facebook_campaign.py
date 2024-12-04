import os
from flask import Flask, request, jsonify
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Initialisation de l'API Facebook avec les informations d'identification du fichier .env
ACCESS_TOKEN = os.getenv('FB_ACCESS_TOKEN')
APP_ID = os.getenv('FB_APP_ID')
APP_SECRET = os.getenv('FB_APP_SECRET')
AD_ACCOUNT_ID = os.getenv('FB_AD_ACCOUNT_ID')

FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

# Configuration du serveur Flask
app = Flask(__name__)

@app.route('/create-campaign', methods=['POST'])
def create_campaign():
    # Récupération des données JSON envoyées dans la requête
    data = request.get_json()
    try:
        # Créer une campagne en utilisant les données reçues
        ad_account = AdAccount(AD_ACCOUNT_ID)
        params = {
            'name': data.get('name'),
            'objective': data.get('objective', 'LEAD_GENERATION'),
            'status': data.get('status', 'PAUSED'),
            'special_ad_categories': data.get('special_ad_category', 'NONE'),
            'daily_budget': data.get('daily_budget'),
            'lifetime_budget': data.get('lifetime_budget'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'spend_cap': data.get('spend_cap'),
            'bid_strategy': data.get('bid_strategy', 'LOWEST_COST_WITHOUT_CAP'),
            'advantage_campaign_budget': data.get('advantage_campaign_budget', False),
            'lead_placement': data.get('lead_placement'),
        }

        campaign = ad_account.create_campaign(params=params)

        # Créer le groupe d'annonces (ad set) avec les informations de ciblage
        adset_params = {
            'name': f"{data.get('name')} - Ad Set",
            'campaign_id': campaign[Campaign.Field.id],
            'status': data.get('status', 'PAUSED'),
            'daily_budget': data.get('daily_budget'),
            'start_time': data.get('start_time'),
            'end_time': data.get('end_time'),
            'bid_amount': data.get('bid_amount'),
            'billing_event': 'IMPRESSIONS',
            'optimization_goal': data.get('optimization_goal', 'LEAD'),
            'targeting': {
                'geo_locations': data.get('targeting', {}).get('geo_locations', {}),
                'age_min': data.get('targeting', {}).get('age_min'),
                'age_max': data.get('targeting', {}).get('age_max'),
                'genders': data.get('targeting', {}).get('genders', []),
                'interests': data.get('targeting', {}).get('interests', []),
            },
            'placements': {
                'facebook_positions': data.get('placements', {}).get('facebook_positions', []),
                'instagram_positions': data.get('placements', {}).get('instagram_positions', []),
                'messenger_positions': data.get('placements', {}).get('messenger_positions', []),
                'audience_network_positions': data.get('placements', {}).get('audience_network_positions', []),
                'device_platforms': data.get('device_platforms', ['mobile', 'desktop']),
                'publisher_platforms': data.get('publisher_platforms', ['facebook', 'instagram']),
                'advantage_plus': data.get('placements_advantage', False),
            },
            'adset_schedule': data.get('adset_schedule', []),
            'dynamic_ad_voice': data.get('dynamic_ad_voice'),
            'dynamic_creative': data.get('dynamic_creative', False),
        }

        adset = ad_account.create_ad_set(params=adset_params)

        # Créer l'annonce (ad creative)
        creative_params = {
            'name': f"{data.get('name')} - Creative",
            'adset_id': adset['id'],
            'status': data.get('status', 'PAUSED'),
            'creative': {
                'title': data.get('creative', {}).get('title'),
                'body': data.get('creative', {}).get('body'),
                'link': data.get('creative', {}).get('link'),
                'image_hash': data.get('creative', {}).get('image_hash'),
            }
        }

        ad = ad_account.create_ad(params=creative_params)

        return jsonify({
            "status": "success",
            "campaign_id": campaign[Campaign.Field.id],
            "adset_id": adset['id'],
            "ad_id": ad['id']
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
