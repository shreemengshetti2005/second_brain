"""
Guide for setting up Google Cloud APIs.
"""

def print_setup_guide():
    """Print setup instructions for Google APIs."""
    
    print("="*70)
    print("GOOGLE CLOUD APIs SETUP GUIDE")
    print("="*70)
    
    print("\n📋 You need to set up 3 Google Cloud services:\n")
    
    # Gemini API
    print("1️⃣  GEMINI API (For AI classification & insights)")
    print("   " + "─"*65)
    print("   ✅ Steps:")
    print("      1. Go to: https://aistudio.google.com/app/apikey")
    print("      2. Click 'Create API Key'")
    print("      3. Copy the API key")
    print("      4. Add to .env file:")
    print("         GEMINI_API_KEY=your_api_key_here")
    print("\n   💰 Pricing: FREE (15 requests/min, 1M tokens/day)")
    print()
    
    # Speech-to-Text API
    print("2️⃣  SPEECH-TO-TEXT API (For audio transcription)")
    print("   " + "─"*65)
    print("   ✅ Steps:")
    print("      1. Go to: https://console.cloud.google.com")
    print("      2. Create a new project (or select existing)")
    print("      3. Enable 'Cloud Speech-to-Text API'")
    print("      4. Go to 'APIs & Services' > 'Credentials'")
    print("      5. Click 'Create Credentials' > 'Service Account'")
    print("      6. Download JSON key file")
    print("      7. Add to .env file:")
    print("         GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json")
    print("         GCP_PROJECT_ID=your-project-id")
    print("\n   💰 Pricing: FREE (60 minutes/month), then $0.006 per 15 seconds")
    print()
    
    # Google Drive API
    print("3️⃣  GOOGLE DRIVE API (For exporting notes)")
    print("   " + "─"*65)
    print("   ✅ Steps:")
    print("      1. Go to: https://console.cloud.google.com")
    print("      2. In the same project, enable 'Google Drive API'")
    print("      3. Go to 'OAuth consent screen'")
    print("         - Choose 'External'")
    print("         - Add app name and email")
    print("         - Add scope: '.../auth/drive.file'")
    print("      4. Go to 'Credentials'")
    print("      5. Create 'OAuth 2.0 Client ID' (Desktop app)")
    print("      6. Download client configuration")
    print("      7. Add to .env file:")
    print("         GDRIVE_CLIENT_ID=your_client_id.apps.googleusercontent.com")
    print("         GDRIVE_CLIENT_SECRET=your_client_secret")
    print("\n   💰 Pricing: FREE (15 GB storage)")
    print()
    
    # Cloud SQL (Optional)
    print("4️⃣  CLOUD SQL (Optional - for deployment)")
    print("   " + "─"*65)
    print("   ✅ For local development: Use local PostgreSQL")
    print("   ✅ For demo/deployment: Set up Cloud SQL")
    print("      1. Go to Cloud SQL in GCP Console")
    print("      2. Create PostgreSQL instance")
    print("      3. Add to .env file:")
    print("         USE_CLOUD_SQL=true")
    print("         CLOUD_SQL_CONNECTION_NAME=project:region:instance")
    print()
    
    print("="*70)
    print("📝 QUICK START")
    print("="*70)
    print("\n✅ Minimum required to get started:")
    print("   1. Gemini API (for AI features)")
    print("   2. Local PostgreSQL (for database)")
    print("\n⚠️  Optional (can add later):")
    print("   - Speech-to-Text API (for audio transcription)")
    print("   - Google Drive API (for exporting notes)")
    print("\n💡 Without these APIs, you can still:")
    print("   - Create text notes manually")
    print("   - Search and filter notes")
    print("   - View basic analytics")
    print()
    
    print("="*70)
    print("🔗 HELPFUL LINKS")
    print("="*70)
    print("   • Gemini API: https://aistudio.google.com")
    print("   • GCP Console: https://console.cloud.google.com")
    print("   • API Documentation: https://cloud.google.com/docs")
    print("="*70)


if __name__ == "__main__":
    print_setup_guide()