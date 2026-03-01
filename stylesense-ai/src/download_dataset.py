import os
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("duckduckgo-search not installed. Run: pip install duckduckgo-search")
    import sys
    sys.exit(1)

# Configuration
CATEGORIES = [
    "shirt", "t-shirt", "pants", "jeans", "shoes", 
    "jacket", "dress", "accessories", "shorts", "skirt"
]
MAX_IMAGES_PER_CATEGORY = 120
TRAIN_SPLIT = 0.8  # 80% train, 20% validation

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "val"

def create_dirs():
    """Create directory structure for the dataset."""
    for category in CATEGORIES:
        (TRAIN_DIR / category).mkdir(parents=True, exist_ok=True)
        (VAL_DIR / category).mkdir(parents=True, exist_ok=True)

def download_image(url: str, save_path: Path, timeout: int = 5):
    """Download an image from a URL."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

def scrape_category(category: str):
    """Scrape and download images for a specific category."""
    print(f"🔍 Searching for '{category}'...")
    
    # We want clear, isolated clothing images
    search_query = f"{category} clothing product photography isolated white background"
    if category == "accessories":
        search_query = "fashion accessories jewelry watch sunglasses hat isolated"
        
    ddgs = DDGS()
    try:
        results = list(ddgs.images(
            search_query,
            region="wt-wt",
            safesearch="moderate",
            size="Medium",
            type_image="photo",
            max_results=200
        ))
    except Exception as e:
        print(f"❌ Error searching for {category}: {e}")
        return

    print(f"📥 Found {len(results)} URLs for {category}. Downloading...")
    
    success_count = 0
    urls = [r.get("image") for r in results if r.get("image")]
    
    # Determine split index
    train_target = int(MAX_IMAGES_PER_CATEGORY * TRAIN_SPLIT)
    
    for i, url in enumerate(urls):
        if success_count >= MAX_IMAGES_PER_CATEGORY:
            break
            
        # Decide if this goes to train or val
        if success_count < train_target:
            save_dir = TRAIN_DIR / category
        else:
            save_dir = VAL_DIR / category
            
        # Use simple naming
        ext = url.split('.')[-1][:4].split('?')[0]
        if ext.lower() not in ['jpg', 'jpeg', 'png', 'webp']:
            ext = 'jpg'
            
        save_path = save_dir / f"{category}_{success_count:03d}.{ext}"
        
        if download_image(url, save_path):
            success_count += 1
            if success_count % 20 == 0:
                print(f"   [{category}] Downloaded {success_count}/{MAX_IMAGES_PER_CATEGORY}")
                
        time.sleep(0.1)  # Be nice to servers

    print(f"✅ Finished {category}: {success_count} images downloaded.")

def main():
    print("🚀 Starting dataset creation...")
    create_dirs()
    
    # We can process a few categories in parallel to speed things up
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(scrape_category, CATEGORIES)

    print("\n🎉 Dataset building complete! Ready for training.")

if __name__ == "__main__":
    main()
