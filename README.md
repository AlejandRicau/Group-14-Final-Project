# Steam Tunnels Defense

A procedural Tower Defense game set in the steam tunnels underneath UT Austin. Built with **Python** and the **Arcade** library, featuring custom GLSL shaders for atmospheric lighting, procedural audio, and particle effects.

![Game Screenshot](assets/images/screenshot.png)

## Features

* **Procedural Map Generation:** Every game features a unique layout with procedurally generated steam tunnels and autotiling.
* **Dynamic Lighting Engine:** Custom GLSL shaders provide additive blending, glowing projectiles, and a dynamic vignette "Fog of War" that reacts to tower placement.
* **Procedural Audio:** Sound effects and the dynamic ambient soundtrack (E Phrygian mode) are generated mathematically at runtime.
* **Animated Enemies:** Zombies feature custom-processed animations with UT branding (Orange shirts).
* **Pathfinding:** Enemies navigate complex mazes using BFS pathfinding.
* **Three Unique Towers:**
    * **Base Tower:** Fires high-velocity steam bolts (Beam Shader).
    * **AOE Tower:** Launches explosive steam canisters (Orb Shader).
    * **Laser Tower:** Emits a continuous, fading beam of concentrated energy (Gradient Shader).
* **Wave System:** Difficulty scales over time, expanding the map and adding new spawn/goal points dynamically.
* **Persistence:** High scores (Waves Survived) are saved securely using encryption.

## Distribution

Pre-packaged installations are available in `/dist`. Download the one appropriate to your system to play the game without the need to run the script or install dependencies.

## Installation (To install and run from scratch)

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/steam-tunnels-defense.git](https://github.com/yourusername/steam-tunnels-defense.git)
    cd steam-tunnels-defense
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Game**
    ```bash
    python run_game.py
    ```

## Controls

* **Mouse:** Interaction (Click buttons, select towers).
* **Arrow Keys:** Pan the camera around the map.
* **Hammer Icon:** Toggle the Build Menu.
* **Left Click (Map):** Place selected tower / Select existing tower to view range.
* **P / Pause Icon:** Pause/Unpause the game.
* **F / Speed Icon:** Toggle Fast Forward (2x Speed).
* **H:** Toggle Shaders (Performance Mode).
* **ESC:** Close the game.

## Project Structure

The game code is organized as follows for ease of access and logical grouping:

```text
Group-14-Final-Project/
├── run_game.py             # Entry point
├── fetch_assets.py         # Tool to grab image resources
├── generate_sounds.py      # Tool to synthesize audio
├── assets/                 # Shaders, Sounds, and Textures
└── src/
    ├── views/              # Screen management (Start, Instructions, Game, Game Over)
    ├── entities/           # Sprites (Towers, Enemies, Tiles)
    ├── managers/           # Logic (GameManager, WaveManager, SoundManager)
    ├── map/                # Procedural generation logic
    ├── ui/                 # Interface elements (Feedback, Bars)
    └── utils/              # Helper functions and Shader wrappers
```

## Credits

This game was developed by Tianqin Puyang and Alejandro Ricaurte, with heavy help from the arcade documentation and examples.