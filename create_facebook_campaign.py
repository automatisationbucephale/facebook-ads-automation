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
            'advantage_plus': data.get('placements_advantage', False)
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
                'behaviors': data.get('targeting', {}).get('behaviors', []),
                'custom_audiences': data.get('targeting', {}).get('custom_audiences', []),
                'excluded_custom_audiences': data.get('targeting', {}).get('excluded_custom_audiences', []),
                'life_events': data.get('targeting', {}).get('life_events', []),
                'work_employers': data.get('targeting', {}).get('work_employers', []),
                'industries': data.get('targeting', {}).get('industries', []),
                'education_schools': data.get('targeting', {}).get('education_schools', []),
                'income': data.get('targeting', {}).get('income', []),
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
                'call_to_action': data.get('creative', {}).get('call_to_action', 'SIGN_UP'),
            },
            'content': {
                'text': data.get('content', {}).get('text', 'Default text'),
                'title': data.get('content', {}).get('title', 'Default title'),
                'description': data.get('content', {}).get('description', 'Default description'),
                'media': {
                    'type': data.get('content', {}).get('media', {}).get('type', 'IMAGE'),
                    'media_id': data.get('content', {}).get('media', {}).get('media_id', 'Default media ID'),
                }
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
        # Cette ligne est corrigée pour avoir la bonne indentation
        return jsonify({"status": "error", "message": str(e)})

# Ajoutez cette route pour définir un endpoint par défaut
@app.route('/', methods=['GET'])
def home():
    return "Bienvenue sur l'API Facebook Ads Automation", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

