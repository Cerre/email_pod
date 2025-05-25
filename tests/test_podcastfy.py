# Simple test script to verify Podcastfy installation

try:
    import podcastfy
    print("Podcastfy is installed and imported successfully.")
except ImportError as e:
    print("Error importing Podcastfy:", e)
