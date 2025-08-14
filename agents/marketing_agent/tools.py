# agents/marketing_agent/tools.py

import os
import psycopg2
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class FacebookMarketingTools:
    def __init__(self, business_id):
        self.business_id = business_id
        self.db_connection = psycopg2.connect(os.getenv('DATABASE_URL'))

        # Load this business's Facebook credentials
        self._load_credentials()

    def _load_credentials(self):
        """Private method to load Facebook tokens from database"""
        cur = self.db_connection.cursor()
        cur.execute("""
            SELECT page_id, access_token, page_name, refresh_token, expires_at 
            FROM marketing_tokens 
            WHERE business_id = %s AND platform = 'facebook'
        """, (self.business_id,))

        result = cur.fetchone()
        if result:
            self.page_id, self.access_token, self.page_name, self.refresh_token, self.expires_at = result
        else:
            raise Exception(f"No Facebook credentials found for business {self.business_id}")
        cur.close()

    def _check_and_refresh_token(self):
        """Check if token is expired and refresh if needed"""
        if self.expires_at and datetime.now() >= self.expires_at:
            print("⏰ Token expired, refreshing...")
            self._refresh_access_token()

    def _refresh_access_token(self):
        """Refresh the access token using Facebook API"""
        try:
            # Exchange current token for a new long-lived token
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': os.getenv('FACEBOOK_APP_ID'),
                'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
                'fb_exchange_token': self.access_token
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            new_token = data['access_token']
            expires_in = data.get('expires_in', 5184000)  # Default 60 days
            new_expires_at = datetime.now() + timedelta(seconds=expires_in)

            # Update database with new token
            self._update_token_in_db(new_token, new_expires_at)

            # Update instance variables
            self.access_token = new_token
            self.expires_at = new_expires_at

            print(f"✅ Token refreshed successfully, expires: {new_expires_at}")

        except Exception as e:
            raise Exception(f"Token refresh failed: {e}")

    def _update_token_in_db(self, new_token, expires_at):
        """Update the database with new token and expiration"""
        cur = self.db_connection.cursor()
        cur.execute("""
            UPDATE marketing_tokens 
            SET access_token = %s, expires_at = %s
            WHERE business_id = %s AND platform = 'facebook'
        """, (new_token, expires_at, self.business_id))

        self.db_connection.commit()
        cur.close()

    def _make_api_call(self, endpoint, params=None):
        """Make API call with automatic token refresh"""
        # Check and refresh token if needed
        self._check_and_refresh_token()

        # Add access token to params
        if params is None:
            params = {}
        params['access_token'] = self.access_token

        # Make the API call
        url = f"https://graph.facebook.com/v18.0/{endpoint}"
        response = requests.get(url, params=params)

        # Debug: print the response if it's an error
        if response.status_code != 200:
            print(f"API Error Response: {response.text}")

        return response

    def list_pages(self):
        """MCP Tool: List Facebook pages for this business"""
        try:
            # Use the automatic refresh API call method
            response = self._make_api_call(
                endpoint=self.page_id,
                params={'fields': 'id,name,category,followers_count,fan_count'}
            )

            response.raise_for_status()
            page_data = response.json()

            return {
                'success': True,
                'pages': [{
                    'id': page_data['id'],
                    'name': page_data['name'],
                    'category': page_data.get('category', 'Unknown'),
                    'followers': page_data.get('followers_count', 0),
                    'likes': page_data.get('fan_count', 0)
                }],
                'count': 1
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Facebook API error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def post_text(self, message):
        """MCP Tool: Post text to Facebook page"""
        try:
            # Check and refresh token if needed
            self._check_and_refresh_token()

            # Facebook POST requires different handling than GET
            response = requests.post(
                f"https://graph.facebook.com/v18.0/{self.page_id}/feed",
                data={
                    'message': message,
                    'access_token': self.access_token
                }
            )

            # Debug: print the response if it's an error
            if response.status_code != 200:
                print(f"POST Error Response: {response.text}")

            response.raise_for_status()
            result = response.json()

            return {
                'success': True,
                'post_id': result.get('id'),
                'message': f'Successfully posted: "{message}"',
                'page_name': self.page_name
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Facebook API error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def post_image(self, caption, image_url):
        """MCP Tool: Post image with caption to Facebook page"""
        try:
            # Check and refresh token if needed
            self._check_and_refresh_token()

            # Facebook photos endpoint for posting images
            response = requests.post(
                f"https://graph.facebook.com/v18.0/{self.page_id}/photos",
                data={
                    'url': image_url,
                    'caption': caption,
                    'access_token': self.access_token
                }
            )

            # Debug: print the response if it's an error
            if response.status_code != 200:
                print(f"POST Image Error Response: {response.text}")

            response.raise_for_status()
            result = response.json()

            return {
                'success': True,
                'post_id': result.get('id'),
                'message': f'Successfully posted image with caption: "{caption}"',
                'page_name': self.page_name,
                'image_url': image_url
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Facebook API error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }

    def get_page_insights(self):
        """MCP Tool: Get page analytics"""
        # Implementation here
        pass


# MCP Tool Functions (these call the class methods)
def create_marketing_tools(business_id):
    """Factory function to create tools for a specific business"""
    return FacebookMarketingTools(business_id)