class AgriChatbot:
    """
    Intelligent Agricultural NLP Chatbot & Farming Advisory Assistant.
    Provides instant expert answers on crop pests, organic fertilizers,
    weather management, market prices, and government schemes.
    """
    
    INTENT_RESPONSES = [
        {
            "keywords": ["blight", "early blight", "late blight", "spots on leaves", "leaf spot"],
            "reply": "🌱 **Leaf Blight Management**: For early/late blight, spray Copper Oxychloride 50% WP (2.5g/L) or Mancozeb 75% WP. Remove infected bottom leaves and avoid overhead sprinkler watering. You can also scan your leaf image in the **Crop Disease Scanner** tab for an instant deep learning diagnosis!"
        },
        {
            "keywords": ["fertilizer", "npk", "urea", "dap", "organic fertilizer", "manure"],
            "reply": "🧪 **Fertilizer Guidance**: Balanced NPK application is vital. For vegetative growth use higher Nitrogen (Urea), for root & flowering use Phosphorus (DAP) and Potassium (MOP). Supplement with 2 tons of vermicompost per acre and Neem cake for pest deterrence. Try our **Soil & Fertilizer Advisor** tool for precise calculations!"
        },
        {
            "keywords": ["water", "irrigation", "drip", "how much water"],
            "reply": "💧 **Smart Irrigation**: Drip irrigation saves 40-60% water while boosting yield. Water early in the morning (6:00 AM - 8:30 AM). In sandy soil, irrigate lightly every 2 days; in clay soil, irrigate deeply every 4-5 days. Check the **Smart Irrigation** tab for daily litres required!"
        },
        {
            "keywords": ["sell crop", "harvest", "sell harvest", "market", "mandi price"],
            "reply": "🌾 **Selling Your Harvest**: You can list your harvested crops directly via the **My Harvest -> Sell My Crop** button on your dashboard. Verified buyers and agribusiness sellers on the **Seller Website** will instantly view your produce and submit purchase offers!"
        },
        {
            "keywords": ["pest", "insect", "aphid", "caterpillar", "whitefly", "worm"],
            "reply": "🐛 **Pest Control**: For sucking pests like aphids and whiteflies, spray Pure Cold-Pressed Neem Oil (10,000 PPM) @ 5ml/L water with mild soap. For caterpillars, use Bacillus thuringiensis (Bt) or Emamectin Benzoate 5% SG @ 0.5g/L."
        },
        {
            "keywords": ["scheme", "subsidy", "pm kisan", "government", "loan"],
            "reply": "🏛️ **Govt Schemes & Subsidies**: Key active schemes include **PM-KISAN** (₹6,000/year direct transfer), **Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)** (up to 55-80% subsidy on drip/sprinkler kits), and **Kisan Credit Card (KCC)** at 4% subsidized interest rate."
        }
    ]

    def get_reply(self, message):
        msg_lower = message.lower()
        for intent in self.INTENT_RESPONSES:
            for kw in intent["keywords"]:
                if kw in msg_lower:
                    return intent["reply"]
                    
        return "🌾 **AgriBot Advisory**: I can help you with crop disease diagnosis, organic & chemical fertilizers, smart irrigation schedules, pest remedies, selling your harvest, and government schemes. Feel free to ask any farming question or use our dedicated AI tools on the dashboard!"

