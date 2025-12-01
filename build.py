import PyInstaller.__main__
import platform
import os
import shutil


def clean_dist():
    """Removes previous build folders to ensure a clean build."""
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("SteamTunnels.spec"):
        os.remove("SteamTunnels.spec")
    print("--- Cleaned previous builds ---")


def build():
    clean_dist()

    # Detect OS to handle file separators
    # Windows uses ';' to separate assets, Mac/Linux uses ':'
    system = platform.system()

    if system == "Windows":
        separator = ";"
        print("--- Building for WINDOWS (.exe) ---")
    else:
        separator = ":"
        print(f"--- Building for {system.upper()} (Unix Executable) ---")

    # Define the asset path
    # Format: "source_folder{separator}destination_folder"
    add_data = f"assets{separator}assets"

    # Run PyInstaller
    PyInstaller.__main__.run([
        'run_game.py',  # Your main script
        '--name=SteamTunnels',  # Name of the executable
        '--onefile',  # Bundle into a single file
        '--windowed',  # No terminal window
        f'--add-data={add_data}',  # Include assets

        # --- THE FIX IS HERE ---
        '--hidden-import=arcade.gl.backends.opengl',
        # -----------------------

        '--clean',  # Clean cache
        '--noconfirm',  # Don't ask to overwrite
    ])

    print("\n============================================")
    print(f"Build Complete! Check the 'dist' folder.")
    print("============================================")


if __name__ == "__main__":
    build()