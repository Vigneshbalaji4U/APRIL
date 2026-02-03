#!/bin/bash
# தமிழ் குரு உதவியாளர் நிறுவல் ஸ்கிரிப்ட்

echo "========================================"
echo "தமிழ் குரு திட்ட உதவியாளர் நிறுவல்"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Python பதிப்பு சரிபார்க்கிறது...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Python 3 நிறுவப்படவில்லை. முதலில் Python 3 நிறுவவும்.${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${YELLOW}மெய்நிகர் சூழலை உருவாக்குகிறது...${NC}"
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}pip ஐ மேம்படுத்துகிறது...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}சார்புகளை நிறுவுகிறது...${NC}"
pip install -r requirements.txt

# Download models
echo -e "${YELLOW}AI மாதிரிகளை பதிவிறக்குகிறது...${NC}"
python models/download_models.py

# Create necessary directories
echo -e "${YELLOW}தேவையான அடைவுகளை உருவாக்குகிறது...${NC}"
mkdir -p data/documents
mkdir -p data/audio_cache
mkdir -p data/chroma_db
mkdir -p logs

# Create sample Tamil document
echo -e "${YELLOW}மாதிரி தமிழ் ஆவணத்தை உருவாக்குகிறது...${NC}"
cat > data/documents/திட்டங்கள்.txt << 'EOF'
வார இறுதி திட்டங்கள்:
1. சனிக்கிழமை காலை: ஜிம்மிற்கு செல்லுதல்
2. சனிக்கிழமை மதியம்: நண்பர்களுடன் சிற்றுண்டி
3. ஞாயிற்றுக்கிழமை: குடும்பத்துடன் சுற்றுலா

மாதாந்திர திட்டங்கள்:
- வங்கி கணக்கு சரிபார்ப்பு: மாதம் 15ம் தேதி
- வீடு வாடகை: மாதம் 5ம் தேதி
- மின்சார பில்: மாதம் 10ம் தேதி

நீண்டகால திட்டங்கள்:
- டிசம்பர் மாதம் குடும்பத்துடன் கேரளா சுற்றுலா
- அடுத்த ஆண்டு புதிய கார் வாங்குதல்
- வீட்டுக் கடனுக்கு விண்ணப்பித்தல்
EOF

echo -e "${GREEN}✅ நிறுவல் முடிந்தது!${NC}"
echo ""
echo -e "${YELLOW}அடுத்த படிகள்:${NC}"
echo "1. மெய்நிகர் சூழலைச் செயல்படுத்தவும்: ${GREEN}source venv/bin/activate${NC}"
echo "2. பயன்பாட்டை இயக்கவும்: ${GREEN}python main.py${NC}"
echo "3. உங்கள் சொந்த திட்ட ஆவணங்களை ${GREEN}data/documents/${NC} அடைவில் சேர்க்கவும்"
echo ""
echo -e "${YELLOW}பயன்படுத்தும் வழிமுறைகள்:${NC}"
echo "• குரு பயன்முறை: 'உதவி' என்று சொல்லவும்"
echo "• நிறுத்த: 'நிறுத்து' என்று சொல்லவும்"
echo "• உரை பயன்முறை: நேரடியாக தமிழில் தட்டச்சு செய்யவும்"
echo ""
echo -e "${GREEN}நல்லதிர்ஷ்டம்! உங்கள் தமிழ் உதவியாளர் தயார்!${NC}"